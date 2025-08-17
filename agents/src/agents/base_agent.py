"""Base Agent"""

import re
from typing import Any
from datetime import datetime
from abc import ABCMeta, abstractmethod
from textwrap import dedent
from functools import reduce

from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from src.common.inference import LLMManager, EmbeddingsManager


class BaseAgent(metaclass=ABCMeta):
    def __init__(
        self,
        llm_provider: str,
        embeddings_provider: str,
        use_llm_cache: bool = False,
        use_embeddings_cache: bool = False,
    ) -> None:
        self._setup_inference_managers(
            llm_provider, embeddings_provider, use_llm_cache, use_embeddings_cache
        )

    @abstractmethod
    def invoke(self, *args, **kwargs) -> dict: ...

    ############################################################
    # Private methods
    ############################################################
    def _setup_inference_managers(
        self,
        llm_provider: str,
        embeddings_provider: str,
        use_llm_cache: bool,
        use_embeddings_cache: bool,
    ) -> None:
        self.llm_manager = LLMManager(llm_provider, use_llm_cache)
        self.llm = self.llm_manager.model
        self.embeddings_manager = EmbeddingsManager(
            embeddings_provider, use_embeddings_cache
        )
        self.embeddings = self.embeddings_manager.model

    def _extract_text_content(self, message: Any) -> str:
        """Extract plain text from a message content that could be str or list of parts."""
        content = getattr(message, "content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts: list[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_value = part.get("text")
                    if text_value:
                        texts.append(str(text_value))
            return "\n".join(texts)
        return str(content)

    @staticmethod
    def _format_contexts(state) -> str:
        contexts = []
        idx = 1
        for retriever_id, docs in state["contexts"].items():
            for doc in docs:
                if "metadata" in doc:
                    doc_format = f"### Metadata\n{doc['metadata']}\n\n### Content\n{doc['page_content']}"
                else:
                    doc_format = doc["page_content"]
                doc_format = f"<idx={idx}>\n{doc_format.strip()}\n</idx={idx}>"
                contexts.append(doc_format)
                idx += 1
        return "\n\n".join(contexts).strip()

    @staticmethod
    def _match_references(
        text: str, url_list: list[str], blacklist: list[str] = ["https://tavily.com"]
    ) -> tuple[str, dict]:
        # 참고 자료 번호 추출 (예: [[3,4]] 형식)
        references = []
        for match in re.finditer(r"\[\[([^\]]+)\]\]", text):
            # 쉼표로 구분된 숫자들을 개별 참조로 분리
            nums = match.group(1).split(",")
            for num in nums:
                references.append(int(num.strip()))

        # 참고 자료 순서대로 정렬 (등장 순서 유지)
        unique_references = list(dict.fromkeys(references))

        # 블랙리스트에 포함되지 않은 유효한 참고 자료만 필터링
        valid_references = []
        for ref in unique_references:
            if (
                ref >= 1
                and ref <= len(url_list)
                and all(url not in url_list[ref - 1] for url in blacklist)
            ):
                valid_references.append(ref)

        # URL 기반으로 참고 자료 매핑 생성
        url_to_new_ref: dict[str, int] = {}
        reference_mapping: dict[int, int] = {}
        for ref in valid_references:
            url = url_list[ref - 1]
            if url not in url_to_new_ref:
                url_to_new_ref[url] = len(url_to_new_ref) + 1
            reference_mapping[ref] = url_to_new_ref[url]

        # URL 매핑 생성 (새로운 참조 번호에 맞춰 URL 재배열)
        url_mapping = {v: k for k, v in url_to_new_ref.items()}

        # 텍스트 내 참고 자료 번호 변환
        def replace_references(match):
            nums = match.group(1).split(",")
            new_ref_nums = set()
            for num_str in nums:
                num = int(num_str.strip())
                if num in reference_mapping:
                    new_ref_nums.add(reference_mapping[num])

            # 각 번호를 개별 [[]] 태그로 변환하고 정렬
            new_refs = [f"[[{num}]]" for num in sorted(list(new_ref_nums))]
            return "".join(new_refs)

        # 텍스트에서 참고 자료 번호 변환
        modified_text = re.sub(r"\[\[([^\]]+)\]\]", replace_references, text)

        return modified_text, url_mapping

    @staticmethod
    def _get_global_context(state) -> str:
        """Get global context"""
        return dedent(
            f"""
            - 현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            - 위치: 대한민국 / 서울
            - 이름: AI 어시스턴트 챗봇
            """
        ).strip()

    async def _ainvoke_agent(
        self, agent_id: str, input: dict, log_prompt: bool = False
    ) -> Any:
        """Invoke the agent."""
        # Invoke the agent
        if agent_id not in self.agents:
            msg = f"Invalid agent id: {agent_id}"
            log_error(msg)
            raise ValueError(msg)
        agent = self.agents[agent_id]
        result = await agent.ainvoke(input)

        # Print the prompts and the result
        if log_prompt or self.log_prompt:
            prompt_steps = []
            for step in agent.steps:
                prompt_steps.append(step)
                if isinstance(step, ChatPromptTemplate):
                    break
            prompt = reduce(lambda x, y: x | y, prompt_steps)

            for msg in prompt.invoke(input).to_messages():
                msg.pretty_print()
            if isinstance(result, BaseMessage):
                result.pretty_print()
            else:
                AIMessage(str(result)).pretty_print()
            print(
                "================================================================================"
            )

        return result

    def _invoke_agent(
        self, agent_id: str, input: dict, log_prompt: bool = False
    ) -> Any:
        """Invoke the agent."""
        # Invoke the agent
        if agent_id not in self.agents:
            msg = f"Invalid agent id: {agent_id}"
            log_error(msg)
            raise ValueError(msg)
        agent = self.agents[agent_id]
        result = agent.invoke(input)

        # Print the prompts and the result
        if log_prompt:
            prompt_steps = []
            for step in agent.steps:
                prompt_steps.append(step)
                if isinstance(step, ChatPromptTemplate):
                    break
            prompt = reduce(lambda x, y: x | y, prompt_steps)

            for msg in prompt.invoke(input).to_messages():
                msg.pretty_print()
            if isinstance(result, BaseMessage):
                result.pretty_print()
            else:
                AIMessage(str(result)).pretty_print()
            print(
                "================================================================================"
            )

        return result
