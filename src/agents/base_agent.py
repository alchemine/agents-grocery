"""Base Agent"""

from typing import Any
from abc import ABCMeta, abstractmethod

from src.common.inference import LLMManager, EmbeddingsManager


class BaseAgent(metaclass=ABCMeta):
    def __init__(
        self, llm_provider: str, embeddings_provider: str, use_llm_cache: bool = False
    ) -> None:
        self._setup_inference_managers(llm_provider, embeddings_provider, use_llm_cache)

    @abstractmethod
    def invoke(self, *args, **kwargs) -> dict: ...

    ############################################################
    # Private methods
    ############################################################
    def _setup_inference_managers(
        self, llm_provider: str, embeddings_provider: str, use_llm_cache: bool
    ) -> None:
        self.llm_manager = LLMManager(llm_provider, use_llm_cache)
        self.llm = self.llm_manager.model
        self.embeddings_manager = EmbeddingsManager(embeddings_provider)
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
