from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, TypeAdapter
from pydantic.config import JsonDict
from pymongo.errors import CollectionInvalid

from config import settings
from enums import SortingOrderEnum, TranslationLanguageEnum

client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_DSN.get_secret_value())


db = client.get_database(settings.MONGO_DB_NAME)


def _pop_default(s: JsonDict) -> None:
    s.pop("default")


class WordTranslationDBSchema(BaseModel):
    word: str
    target_lang: str
    source_lang: str
    # Mongo does not support default in JSONSchema
    definitions: list[str] = Field([], json_schema_extra=_pop_default)
    synonyms: list[str] = Field([], json_schema_extra=_pop_default)
    translations: list[str] = Field([], json_schema_extra=_pop_default)


_DB_SCHEMA = WordTranslationDBSchema.model_json_schema()


async def create_schema() -> None:
    try:
        collection = await db.create_collection(
            settings.MONGO_COLLECTION_NAME,
            check_exists=True,
            validator={"$jsonSchema": _DB_SCHEMA},
        )
    except CollectionInvalid:  # Don't know why, but motor ignores check_exists arg
        collection = db.get_collection(settings.MONGO_COLLECTION_NAME)
    await collection.create_index([("word", 1), ("target_lang", 1), ("source_lang", 1)], unique=True)


_WORDS_LIST_ADAPTER = TypeAdapter(list[WordTranslationDBSchema])


async def get_words(
    *,
    search: str | None = None,
    source_lang: TranslationLanguageEnum | None = None,
    target_lang: TranslationLanguageEnum | None = None,
    limit: int,
    offset: int = 0,
    sorting_order: SortingOrderEnum = SortingOrderEnum.ASC,
    full_document: bool,
) -> list[WordTranslationDBSchema]:
    query_filter: dict[str, Any] = {}
    if search:
        query_filter["word"] = {"$regex": search, "$options": "i"}
    if target_lang:
        query_filter["target_lang"] = target_lang
    if source_lang:
        query_filter["source_lang"] = source_lang
    if full_document:
        projection = None
    else:
        projection = {"word": 1, "target_lang": 1, "source_lang": 1}

    result = _WORDS_LIST_ADAPTER.validate_python(
        await db.get_collection(settings.MONGO_COLLECTION_NAME)
        .find(query_filter, projection)
        .sort(
            "word",
            sorting_order,
        )
        .skip(
            offset,
        )
        .limit(
            limit,
        )
        .to_list(
            limit,
        ),
    )
    return result


async def get_word(
    word: str,
    *,
    source_lang: TranslationLanguageEnum | None = None,
    target_lang: TranslationLanguageEnum,
) -> WordTranslationDBSchema | None:
    query_filter: dict[str, Any] = {"word": word, "target_lang": target_lang}
    if source_lang is not None:
        query_filter["source_lang"] = source_lang
    result = await db.get_collection(settings.MONGO_COLLECTION_NAME).find_one(query_filter)
    if result is None:
        return None
    return WordTranslationDBSchema.model_validate(result)


async def save_word(
    word: WordTranslationDBSchema,
) -> None:
    await db.get_collection(settings.MONGO_COLLECTION_NAME).insert_one(word.model_dump())


async def delete_word(
    word: str,
    *,
    source_lang: TranslationLanguageEnum,
    target_lang: TranslationLanguageEnum,
) -> None:
    await db.get_collection(settings.MONGO_COLLECTION_NAME).delete_one(
        {"word": word, "source_lang": source_lang, "target_lang": target_lang},
    )
    return
