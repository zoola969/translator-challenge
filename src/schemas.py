from typing import Annotated, Self

from annotated_types import MinLen
from pydantic import BaseModel, BeforeValidator, Field, Strict, field_validator
from pydantic_core.core_schema import ValidationInfo

from db import WordTranslationDBSchema
from enums import TranslationLanguageEnum


class WordRetrieveSchema(BaseModel):
    word: str
    target_lang: str
    source_lang: str
    definitions: list[str]
    synonyms: list[str]
    translations: list[str]

    @classmethod
    def from_db_schema(cls, model: WordTranslationDBSchema) -> Self:
        return cls(
            word=model.word,
            target_lang=model.target_lang,
            source_lang=model.source_lang,
            definitions=model.definitions,
            synonyms=model.synonyms,
            translations=model.translations,
        )


class WordListSchema(BaseModel):
    words: list[WordRetrieveSchema]
    limit: int
    offset: int


class DeleteTranslatedWordSchema(BaseModel):
    word: str
    target_lang: TranslationLanguageEnum
    source_lang: TranslationLanguageEnum


class TranslateWordSchema(BaseModel):
    word: Annotated[
        str,
        BeforeValidator(lambda v: v.strip() if isinstance(v, str) else v),
        MinLen(1),
        Strict(),
    ]
    target_lang: TranslationLanguageEnum = TranslationLanguageEnum.ENGLISH
    source_lang: TranslationLanguageEnum | None = Field(
        None,
        description="If not provided, the source language will be detected by translation service.",
    )

    @field_validator("word", mode="after")
    @classmethod
    def validate_word(cls, word: str, _info: ValidationInfo) -> str:
        if len(word.split(" ")) > 1:
            raise ValueError("Only one word is allowed.")
        return word
