from pydantic import BaseModel, Field
from typing import List, Optional
from textwrap import dedent

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

from src.common.llm import llm
from src.common.timer import T


class Verse(BaseModel):
    book: str = Field(description="성경의 책 이름 (예: '요한복음', '마태복음')")
    chapter: int = Field(description="장 번호")
    verse: int = Field(description="절 번호")

    def get_reference(self) -> str:
        """성경 구절 참조를 문자열로 반환합니다 (예: '요한복음 3:16')"""
        return f"{self.book} {self.chapter}:{self.verse}"


class BibleReference(BaseModel):
    """성경 구절과 그 이유를 담는 모델"""

    start_verse: Verse = Field(description="시작 절")
    end_verse: Verse | None = Field(None, description="끝 절. (단일 절인 경우 None)")
    # reason: str = Field(
    #     description="이 구절이 사용자의 고민과 관련이 있는 이유를 간결하게 설명합니다."
    # )

    def get_reference(self) -> str:
        """성경 구절 참조를 문자열로 반환합니다 (예: '요한복음 3:16-17')"""
        if self.end_verse:
            return (
                f"{self.start_verse.get_reference()} - {self.end_verse.get_reference()}"
            )
        else:
            return self.start_verse.get_reference()


class BibleRetriever:
    """사용자의 고민에 관련된 성경 구절을 찾아주는 클래스"""

    def __init__(self):
        self.verse_retriever = self._build_verse_retriever()
        self.response_generator = self._build_response_generator()

    def _build_verse_retriever(self) -> RunnablePassthrough:
        """사용자의 고민에 관련된 성경 구절을 찾아 반환합니다."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    dedent(
                        """
                        당신은 성경에 대한 깊은 지식을 가진 조언자입니다. 
                        사용자의 고민이나 질문에 관련된 성경 구절을 찾아 제공하세요.
                        구절은 정확한 책, 장, 절을 포함해야 하며, 구절의 내용과 왜 이 구절이 사용자의 고민과 관련이 있는지 설명해야 합니다.
                        가장 적절한 성경 구절을 선택하세요.
                        """
                    ),
                ),
                ("user", "{input}"),
            ]
        )
        return (
            prompt
            | llm.with_structured_output(BibleReference)
            | (lambda x: [x] if isinstance(x, BibleReference) else x)
        )

    def _build_response_generator(self) -> RunnablePassthrough:
        """사용자의 고민에 관련된 성경 구절을 찾고, 상세한 설명을 텍스트로 반환합니다."""
        return (
            RunnablePassthrough.assign(
                references=lambda x: "\n".join([v.get_reference() for v in x["verses"]])
            )
            | ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        dedent(
                            """
                            당신은 성경에 대한 깊은 지식을 가진 조언자입니다.
                            사용자의 고민이나 질문에 관련된 성경 구절을 찾아 제공하세요.
                            구절은 정확한 책, 장, 절을 포함해야 하며, 구절의 내용을 인용하고 왜 이 구절이 사용자의 고민과 관련이 있는지 자세히 설명해주세요.
                            가장 적절한 성경 구절을 선택하고, 사용자에게 위로와 지혜를 줄 수 있는 따뜻한 조언으로 마무리하세요.
                            """
                        ),
                    ),
                    (
                        "human",
                        "# 사용자 발화\n{input}\n\n# 관련 성경 구절\n{references}",
                    ),
                ]
            )
            | llm
            | StrOutputParser()
        )

    def invoke(self, user_concern: str) -> str:
        verses = self.verse_retriever.invoke({"input": user_concern})
        # for verse in verses:
        #     print(f"참조: {verse.get_reference()}")
        #     print(
        #         f"시작 구절: {verse.start_verse.book} {verse.start_verse.chapter}:{verse.start_verse.verse}"
        #     )
        #     if verse.end_verse:
        #         print(
        #             f"끝 구절: {verse.end_verse.book} {verse.end_verse.chapter}:{verse.end_verse.verse}"
        #         )
        #     else:
        #         print("끝 구절: 없음")
        #     # print(f"이유: {verse.reason}")
        #     print("---")
        # return self.response_generator.invoke({"input": user_concern, "verses": verses})
        return verses[0].get_reference()


if __name__ == "__main__":
    bible_retriever = BibleRetriever()

    # 구조화된 출력 테스트
    user_concern = "직장에서 스트레스를 많이 받고 있어요. 어떻게 해야 할까요?"
    result = bible_retriever.invoke(user_concern)
    print(result)

    # verses = bible_retriever.get_bible_verses(user_concern)
    # for verse in verses:
    #     print(f"참조: {verse.get_reference()}")
    #     print(
    #         f"시작 구절: {verse.start_verse.book} {verse.start_verse.chapter}:{verse.start_verse.verse}"
    #     )
    #     if verse.end_verse:
    #         print(
    #             f"끝 구절: {verse.end_verse.book} {verse.end_verse.chapter}:{verse.end_verse.verse}"
    #         )
    #     else:
    #         print("끝 구절: 없음")
    #     # print(f"이유: {verse.reason}")
    #     print("---")

    # # 텍스트 설명 테스트
    # explanation = bible_retriever.get_bible_verses_with_explanation(
    #     user_concern, verses
    # )
    # print("\n상세 설명:")
    # print(explanation)
