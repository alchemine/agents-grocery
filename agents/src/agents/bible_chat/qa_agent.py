"""Question-Answering Agent"""

from typing import Dict
from textwrap import dedent

from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import InMemorySaver
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.state import CompiledStateGraph

from src.common.timer import T
from src.common.logger import log_chat_history
from src.agents.base_agent import BaseAgent


LAST_NODE_NAME = "generate_response"


class GraphState(MessagesState):
    question: str
    question_en: str
    path_state: str
    verse: str
    response: str
    contexts: list
    references: dict
    # remaining_steps: RemainingSteps


class QAAgent(BaseAgent):
    def __init__(
        self,
        llm_provider: str = "tpu_naver_14b",
        embeddings_provider: str = "local",
        use_llm_cache: bool = False,
        use_embeddings_cache: bool = True,
    ):
        super().__init__(
            llm_provider, embeddings_provider, use_llm_cache, use_embeddings_cache
        )
        self.graph = self._build_graph()

    def match_references(self, text, url_list):
        import re

        # 참고 자료 번호 추출 (예: [[3,4]] 형식)
        references = []
        for match in re.finditer(r"\[\[([^\]]+)\]\]", text):
            # 쉼표로 구분된 숫자들을 개별 참조로 분리
            nums = match.group(1).split(",")
            for num in nums:
                references.append(int(num.strip()))

        # 참고 자료 순서대로 정렬 (등장 순서 유지)
        unique_references = list(dict.fromkeys(references))

        # 참고 자료 매핑 생성 (등장 순서대로 1부터 번호 부여)
        reference_mapping = {}
        for i, ref in enumerate(unique_references):
            reference_mapping[ref] = i + 1

        # URL 매핑 생성 (새로운 참조 번호에 맞춰 URL 재배열)
        url_mapping = {}
        for orig_num, new_num in reference_mapping.items():
            # 원래 인덱스는 1부터 시작하므로 -1 해줌
            if orig_num >= 1 and orig_num < len(url_list):
                url_mapping[new_num] = url_list[orig_num - 1]

        # 텍스트 내 참고 자료 번호 변환
        def replace_references(match):
            nums = match.group(1).split(",")
            # 각 번호를 개별 [[]] 태그로 변환
            new_refs = []
            for num in nums:
                new_num = reference_mapping[int(num.strip())]
                new_refs.append(f"[[{new_num}]]")
            return "".join(new_refs)

        # 텍스트에서 참고 자료 번호 변환
        modified_text = re.sub(r"\[\[([^\]]+)\]\]", replace_references, text)

        return modified_text, url_mapping

    def chunk_formatting(self, contexts: list[dict]) -> tuple[str, list[str]]:
        if len(contexts) == 0:
            return ""

        formatted_results = []
        url_list = []
        for i, result in enumerate(contexts):
            formatted_results.append(f"참고자료{i+1} : {result['content']}")
            url_list.append(f"{result['url']}")
        return "\n".join(formatted_results), url_list

    def _build_nodes(self) -> dict:
        @T
        def search_internet(state: GraphState) -> GraphState:
            # Tavily 검색 도구 설정
            tavily_search_tool = TavilySearch(
                max_results=5,
                include_domains=[
                    "biblehub.com",
                    "biblegateway.com",
                    "gotquestions.org",
                    "bible.org",
                    "christianity.com",
                ],
            )

            # 사용자 질문으로 검색 수행
            search_results = tavily_search_tool.invoke(state["question"])

            # 검색 결과가 없는 경우 처리
            if not search_results["results"]:
                return {
                    "verse": {
                        "answer": "죄송합니다. 해당 질문에 대한 검색 결과를 찾을 수 없습니다. 다른 방식으로 질문해 주시겠습니까?",
                        "reference": [],
                    },
                    "chunk": [],
                }

            result = {"contexts": search_results["results"]}
            return result

        @T
        def generate_response(state: GraphState) -> Dict:
            """
            Generate a response based on the retrieved verses.
            """
            # 프롬프트 정의 수정
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        dedent(
                            """
                            # Role
                            당신은 비기독교인들을 대상으로 기독교/성경/삶에 관련된 질문에 답하는 챗봇입니다.
                            유저의 질문의 핵심을 파악하고, 필요한 자료를 참고해서 적절한 대답을 해주세요.
                            검색 결과를 바탕으로 비기독교인도 가능한 납득할 수 있도록 논리적으로 답변을 작성해주세요.
                            답변을 줄때 논문과 같이 참고한 자료의 번호를 [[*]] 형태로 적어주세요. (예시: "...[[1]] ...[[2,3]]").
                            참고자료 번호는 반드시 reference에 있는 내용과 동일해야합니다.
                            """
                        ),
                    ),
                    MessagesPlaceholder(variable_name="messages"),
                    ("human", "question: {question}"),
                    ("ai", "검색 결과: {search_results}"),
                ]
            )
            formatted_result, url_list = self.chunk_formatting(state["contexts"])

            # LLM으로 응답 생성
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke(
                {
                    "messages": state.get("messages", []),
                    "question": state["question"],
                    "search_results": formatted_result,
                }
            )
            response, references = self.match_references(response, url_list)
            result = {
                "response": response,
                "references": references,
                "messages": [state["question"], response],
            }
            return result

        return {
            "search_internet": search_internet,
            "generate_response": generate_response,
        }

    def _build_graph(self) -> CompiledStateGraph:
        workflow = StateGraph(GraphState)

        # Define the nodes
        nodes = self._build_nodes()
        workflow.add_node("search_internet", nodes["search_internet"])
        workflow.add_node("generate_response", nodes["generate_response"])

        workflow.add_edge(START, "search_internet")
        workflow.add_edge("search_internet", "generate_response")
        workflow.add_edge("generate_response", END)

        # Compile
        workflow = workflow.compile(checkpointer=InMemorySaver())
        return workflow

    @T
    def invoke(self, question: str, user_id: str = "test") -> dict:
        """Invoke the graph."""
        for step in self.graph.stream(
            {"question": question},
            config={"configurable": {"thread_id": user_id}},
            stream_mode="values",
        ):
            pass

        response = self._extract_text_content(step["messages"][-1])
        log_chat_history(question, response, user_id, "bible_chat")
        return {"response": response, "references": step["references"]}

    # @T
    # async def astream(
    #     self, question: str, thread_id: str = "test", user_id: str = "test"
    # ) -> AsyncGenerator[str, None]:
    #     """Asynchronous stream the graph."""
    #     async for event in self.graph.astream_events(
    #         {"question": question}, configurable={"thread_id": thread_id}
    #     ):
    #         kind = event["event"]
    #         if kind == "on_chat_model_stream":
    #             # Print only in the last node
    #             node_name = event["metadata"]["langgraph_node"]
    #             if node_name == LAST_NODE_NAME:
    #                 if (
    #                     hasattr(event["data"]["chunk"], "content")
    #                     and event["data"]["chunk"].content
    #                 ):
    #                     addition = event["data"]["chunk"].content
    #                     yield addition

    # @T
    # def stream(self, question: str, thread_id: str = "test", user_id: str = "test"):
    #     """Synchronous stream the graph."""
    #     for event in self.graph.stream({"question": question}):
    #         kind = event["event"]
    #         if kind == "on_chat_model_stream":
    #             # Print only in the last node
    #             node_name = event["metadata"]["langgraph_node"]
    #             if node_name == LAST_NODE_NAME:
    #                 if (
    #                     hasattr(event["data"]["chunk"], "content")
    #                     and event["data"]["chunk"].content
    #                 ):
    #                     addition = event["data"]["chunk"].content
    #                     yield addition


if __name__ == "__main__":
    qa_agent = QAAgent()
    qa_agent.invoke("하나님이 죄를 창조하신 이유?")
