"""QA Agent"""

import os
from os.path import join
from typing import Any
from textwrap import dedent

from langchain.prompts import ChatPromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
    # LLMChainExtractor,
    # LLMChainFilter,
    # LLMListwiseRerank,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph, MessagesState

from config import ROOT_DIR
from src.common.logger import log_warning, log_info, log_chat_history
from src.common.timer import T
from src.agents.base_agent import BaseAgent


class GraphState(MessagesState):
    question: str
    contexts: dict
    references: dict


class QAAgent(BaseAgent):
    def __init__(
        self,
        llm_provider: str = "tpu_naver_14b",
        embeddings_provider: str = "local",
        use_llm_cache: bool = False,
        use_embeddings_cache: bool = True,
    ) -> None:
        super().__init__(
            llm_provider, embeddings_provider, use_llm_cache, use_embeddings_cache
        )
        self.agents = self._build_agents()
        self.graph = self._build_graph()

    ############################################################
    # Public methods
    ############################################################
    @T
    def invoke(self, question: str, user_id: str) -> dict[str, Any]:
        """Invoke the agent and return answer with contexts."""
        for step in self.graph.stream(
            {"question": question},
            config={"configurable": {"thread_id": user_id}},
            stream_mode="values",
        ):
            pass

        response = self._extract_text_content(step["messages"][-1])
        log_chat_history(question, response, user_id, "qa_agent")
        return {"response": response, "references": step["references"]}

    ############################################################
    # Private methods
    ############################################################
    def _build_retrievers(self) -> dict:
        # Retriever
        base_retriever = MultiQueryRetriever.from_llm(
            retriever=TavilySearchAPIRetriever(k=3, include_generated_answer=True),
            llm=self.llm,
        )

        # Document compressor
        transformers = [
            RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50),
            EmbeddingsRedundantFilter(embeddings=self.embeddings),  # deduplication
            EmbeddingsFilter(embeddings=self.embeddings, similarity_threshold=0.3),
            # LLMChainExtractor.from_llm(self.llm),
            # LLMChainFilter.from_llm(self.llm),
            # LLMListwiseRerank.from_llm(self.llm, top_n=5),
        ]
        base_compressor = DocumentCompressorPipeline(transformers=transformers)
        web_search_retriever = ContextualCompressionRetriever(
            base_compressor=base_compressor,
            base_retriever=base_retriever,
        )

        return {
            "web_search": web_search_retriever,
        }

    def _build_agents(self) -> dict:
        """Build agents."""
        prompt = RunnablePassthrough.assign(
            global_context=self._get_global_context,
            contexts=self._format_contexts,
        ) | ChatPromptTemplate.from_messages(
            [
                (
                    "user",
                    dedent(
                        """
                        다음 <contexts>를 기반으로 질문에 답변하세요.
                        논문과 같이 참고한 자료의 번호를 [[*]] 형태로 적어주세요. (예시: "...[[1]] ...[[2,3]]").
                        참고자료 번호는 반드시 contexts에 있는 내용과 동일해야합니다.
                        
                        <global_context>
                        {global_context}
                        </global_context>

                        <contexts>
                        {contexts}
                        </contexts>

                        <question>
                        {question}
                        </question>
                        """
                    ),
                ),
            ]
        )
        response_generator = prompt | self.llm | StrOutputParser()
        return {
            "response_generator": response_generator,
        }

    def _build_graph(self) -> CompiledStateGraph:
        """Build graph."""
        graph = StateGraph(GraphState)
        nodes = self._build_nodes()

        graph.add_node("retrieve_contexts", nodes["retrieve_contexts"])
        graph.add_node("generate_response", nodes["generate_response"])

        graph.add_edge(START, "retrieve_contexts")
        graph.add_edge("retrieve_contexts", "generate_response")
        graph.add_edge("generate_response", END)
        graph = graph.compile(InMemorySaver())

        # Save graph image
        os.makedirs(join(ROOT_DIR, "logs"), exist_ok=True)
        try:
            graph.get_graph(xray=True).draw_mermaid_png(
                output_file_path=join(ROOT_DIR, "logs", "qa_agent.png")
            )
        except Exception as e:
            log_warning(f"Failed to save graph image: \n{e}")

        return graph

    def _build_nodes(self) -> dict:
        """Build nodes."""
        retrievers = self._build_retrievers()

        @T
        def retrieve_contexts(state: GraphState) -> GraphState:
            """Retrieve contexts."""
            contexts = {}
            for id, retriever in retrievers.items():
                docs = retriever.invoke(state["question"])
                contexts[id] = [
                    {"page_content": doc.page_content, "metadata": doc.metadata}
                    for doc in docs
                ]
                log_info(f"Retrieved {len(contexts[id])} contexts from {id}")

            return {"contexts": contexts}

        @T
        def generate_response(state: GraphState) -> GraphState:
            """Generate response."""
            response = self._invoke_agent("response_generator", state, log_prompt=True)
            url_list = [
                doc["metadata"]["source"] for doc in state["contexts"]["web_search"]
            ]
            response, references = self._match_references(response, url_list)
            return {
                "messages": [state["question"], response],
                "references": references,
            }

        return {
            "retrieve_contexts": retrieve_contexts,
            "generate_response": generate_response,
        }


if __name__ == "__main__":
    qa_agent = QAAgent(use_llm_cache=True)
    result = qa_agent.invoke("트럼프랑 일론이랑 요즘 어떻게 지내?", user_id="test")
    log_info(result)
