from typing import Any, Optional
import random

from src.agents.base_agent import BaseAgent
from src.common.timer import T


class ClientAgent(BaseAgent):
    def __init__(
        self, llm_provider: str = "tpu_virtual_client", embeddings_provider: str = "local"
    ) -> None:
        super().__init__(llm_provider, embeddings_provider)
        self.persona = ["computer scientist", "software engineer", "mathematician", "teacher", "student", "doctor", "driver", "trader", "translator", "tennis player", "basketball player"]


    ############################################################
    # Public methods
    ############################################################
    @T
    def invoke(self, prompt: str, user_id: Optional[str] = None) -> dict[str, Any]:
        """LLM에 직접 질의하여 답변을 반환합니다.

        Args:
            prompt: 사용자 입력 프롬프트
            user_id: 호출자 식별자(옵션). 추적/스레드 구분용

        Returns:
            {"response": <string>} 형태의 딕셔너리
        """
        if prompt == "":
            prompt = self.persona[random.randint(0, len(self.persona) - 1)]

        result = self.llm.invoke(
            prompt,
            config=self.llm_manager.invoke_config,
        )
        text = self._extract_text_content(result)
        return {"response": text}


if __name__ == "__main__":
    agent = ClientAgent()
    print(agent.invoke(""))
