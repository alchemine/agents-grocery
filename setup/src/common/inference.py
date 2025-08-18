"""Inference module."""

import re
import tiktoken
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config import (
    CFG,
    SERVICE_NAME,
    ELASTICSEARCH_URL,
    ELASTICSEARCH_USER,
    ELASTICSEARCH_PASSWORD,
)
from src.common.utils import SingletonBase, dump_json
from src.common.logger import log_info, log_success, log_warning, log_error


def create_llm_cache(service_name: str, model_name: str):
    """Create LLM cache instance for individual model."""
    cache_key = f"{service_name}_{model_name}"

    try:
        from langchain_elasticsearch import ElasticsearchCache

        param = {
            "es_url": ELASTICSEARCH_URL,
            "es_user": ELASTICSEARCH_USER,
            "es_password": ELASTICSEARCH_PASSWORD,
            "index_name": CFG.inference.llm.cache.index,
            "metadata": {"service": service_name, "model": model_name},
        }
        cache = ElasticsearchCache(**param)
        log_success(f"LLM cache for {cache_key} using Elasticsearch created.")
    except Exception as e:
        try:
            from langchain_community.cache import SQLiteCache

            log_warning(
                f"LLM cache using Elasticsearch failed: {e}\n{dump_json(param)}"
            )
            db_path = f"llm_cache_{cache_key}.db"
            cache = SQLiteCache(database_path=db_path)
            log_success(f"LLM cache for {cache_key} using SQLiteCache created.")
        except Exception as e:
            log_warning(f"LLM cache using SQLiteCache failed: {e}")
            cache = None

    return cache


def create_embeddings_cache(service_name: str, model_name: str):
    """Create embeddings cache instance for individual model."""
    cache_key = f"{service_name}_{model_name}"

    try:
        from langchain_elasticsearch import ElasticsearchEmbeddingsCache

        param = {
            "es_url": ELASTICSEARCH_URL,
            "es_user": ELASTICSEARCH_USER,
            "es_password": ELASTICSEARCH_PASSWORD,
            "index_name": CFG.inference.embeddings.cache.index,
            "metadata": {"service": service_name, "model": model_name},
        }
        cache = ElasticsearchEmbeddingsCache(**param)
        log_success(f"Embeddings cache for {cache_key} using Elasticsearch created.")
    except Exception as e:
        try:
            from langchain.storage import LocalFileStore

            log_warning(
                f"Embeddings cache using Elasticsearch failed: {e}\n{dump_json(param)}"
            )
            db_path = f"embeddings_cache_{cache_key}.db"
            cache = LocalFileStore(db_path)
            log_success(
                f"Embeddings cache for {cache_key} using LocalFileStore created."
            )
        except Exception as e:
            log_warning(f"Embeddings cache using LocalFileStore failed: {e}")
            cache = None

    return cache


class LLMManager(SingletonBase):
    """LLM manager.

    Attributes:
        provider: provider name
        model_name: model name
        model: LLM model
        batch_config: batch config for LLM

    References:
        - Prompt optimizer: https://platform.openai.com/chat/edit?models=gpt-5&optimize=true
        - Reasoning guide: https://platform.openai.com/docs/guides/reasoning
        - Prompt examples: https://platform.openai.com/docs/guides/reasoning?example=planning#prompt-examples
    """

    # https://platform.openai.com/docs/guides/latest-model#preambles
    PREAMBLES = "Before you call a tool, explain why you are calling it."

    @classmethod
    def _generate_instance_key(cls, provider: str, *args, **kwargs) -> tuple:
        return (provider,)

    def _init_once(self, provider: str, use_cache: bool = False) -> None:
        """Initialize LLM manager."""
        assert (
            provider in CFG.inference.llm.providers
        ), f"provider({provider}) should be in CFG.inference.llm.providers"

        self.provider = provider
        self.model_name = self._get_model_name()
        self.model = self._get_model(use_cache)
        self.batch_config = self._get_batch_config()

    def _get_model(self, use_cache: bool) -> ChatOpenAI:
        """Get LLM model."""
        try:
            model_config = CFG.inference.llm.providers[self.provider].get(
                "model_config"
            )
            if use_cache:
                cache = create_llm_cache(SERVICE_NAME, self.model_name)
                if cache is not None:
                    model_config["cache"] = cache
            return ChatOpenAI(**model_config)
        except Exception:
            log_error(f"Invalid model config: {dump_json(model_config)}")
            raise ValueError(f"No model config found for {self.provider}")

    def _get_batch_config(self) -> dict:
        """Get batch config for LLM."""
        try:
            return CFG.inference.llm.providers[self.provider].batch_config
        except Exception:
            log_info(f"No batch config found for {self.provider}")
            return {}

    def _get_model_name(self) -> str:
        """Get model name."""
        return CFG.inference.llm.providers[self.provider].model_config.model

    def truncate_text_by_tokens(
        self, text: str, max_tokens: int | None = None, model: str | None = None
    ) -> str:
        """Truncate text to fit within token limit"""
        if max_tokens is None:
            max_tokens = CFG.inference.llm.providers[
                self.provider
            ].model_config.max_tokens

        try:
            if model is None:
                model = self.model_name
            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(text)
        except Exception:
            model = "gpt-4o-mini"
            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(text)

        if len(tokens) > max_tokens:
            truncated_tokens = tokens[:max_tokens]
            truncated_text = encoding.decode(truncated_tokens)

            # 문장이 중간에 잘리지 않도록 마지막 완전한 문장까지만 반환
            # TODO: 문장 분리 방법 개선
            sentences = re.split(r"[.!?]+\s+", truncated_text)
            if len(sentences) > 1:
                result = ". ".join(sentences[:-1]) + "."
            else:
                result = truncated_text
        else:
            result = text
        return result


class EmbeddingsManager(SingletonBase):
    """Embeddings manager.

    Attributes:
        provider: provider name
        model_name: model name
        model: Embeddings model
        chunk_size: chunk size (max concurrency)
    """

    @classmethod
    def _generate_instance_key(cls, provider: str, *args, **kwargs) -> tuple:
        return (provider,)

    def _init_once(self, provider: str, use_cache: bool = False) -> None:
        self.provider = provider
        self.model_name = self._get_model_name()
        self.model = self._get_model(use_cache)
        self.chunk_size = self._get_chunk_size()

    def _get_model(self, use_cache: bool) -> OpenAIEmbeddings:
        """Get embeddings model."""
        try:
            model_config = CFG.inference.embeddings.providers[self.provider].get(
                "model_config"
            )
            model = OpenAIEmbeddings(**model_config)

            if use_cache:
                from langchain.embeddings import CacheBackedEmbeddings

                cache = create_embeddings_cache(SERVICE_NAME, self.model_name)
                if cache is not None:
                    model = CacheBackedEmbeddings.from_bytes_store(
                        model,
                        cache,
                        namespace=f"{SERVICE_NAME}_{self.model_name}",
                        key_encoder="blake2b",
                    )

            return model
        except Exception:
            log_error(f"Invalid embeddings config: {dump_json(model_config)}")
            raise ValueError(f"No embeddings config found for {self.provider}")

    def _get_model_name(self) -> str:
        """Get model name."""
        return CFG.inference.embeddings.providers[self.provider].model_config.model

    def _get_chunk_size(self) -> int:
        """Get chunk size."""
        return CFG.inference.embeddings.providers[self.provider].chunk_size


if __name__ == "__main__":
    llm_manager = LLMManager(provider="gpt_4o_mini", use_cache=True)
    embeddings_manager = EmbeddingsManager(provider="local", use_cache=True)
    print(llm_manager.model_name)
    print(embeddings_manager.model_name)
