"""Question-Answering Agent"""

from typing import Dict

from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import InMemorySaver
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.state import CompiledStateGraph

from src.common.timer import T
from src.common.logger import log_chat_history
from src.common.utils import dedent
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
        self.runnables = self._build_runnables()
        self.graph = self._build_graph()

    def _chunk_formatting(self, contexts: list[dict]) -> tuple[str, list[str]]:
        if len(contexts) == 0:
            return ""

        formatted_results = []
        url_list = []
        for i, result in enumerate(contexts, start=1):
            formatted_results.append(
                f"<idx={i}>\n{result['content'].strip()}\n</idx={i}>"
            )
            url_list.append(f"{result['url']}")
        return "\n\n".join(formatted_results), url_list

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
            formatted_result, url_list = self._chunk_formatting(state["contexts"])
            response = self._invoke_runnable(
                "generate_response",
                {
                    "messages": state.get("messages", []),
                    "question": state["question"],
                    "search_results": formatted_result,
                },
            )
            response, references = self._match_references(response, url_list)
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

    def _build_runnables(self) -> dict:
        """Build runnables."""
        # 프롬프트 정의 수정
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    dedent(
                        """
                        # Role
                        당신은 비기독교인들을 대상으로 기독교/성경/삶에 관련된 질문에 답하는 챗봇입니다.
                        사용자에게 기독교를 전도하는 것이 아니라, 기독교의 가치를 소개하는 것이 목적입니다.
                        주어진 <contexts>를 참고하여 비기독교인도 납득할 수 있도록 중립적이고 객관적인 답변을 작성해주세요.
                        답변을 줄때 논문과 같이 참고한 자료의 번호를 [[*]] 형태로 적어주세요. (예시: "...[[1]] ...[[2,3]] ... [[4,5]]").
                        참고자료 번호는 반드시 <contexts>에 있는 내용과 동일해야합니다.
                        
                        <contexts>
                        {search_results}
                        </contexts>
                        """
                    ),
                ),
                MessagesPlaceholder(variable_name="messages"),
                ("user", "question: {question}"),
            ]
        )

        # LLM으로 응답 생성
        chain = prompt | self.llm | StrOutputParser()
        return {
            "generate_response": chain,
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
