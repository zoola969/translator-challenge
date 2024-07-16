from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic.json_schema import SkipJsonSchema
from starlette import status

from db import delete_word, get_word, get_words, save_word
from enums import SortingOrderEnum, TranslationLanguageEnum
from google_api import get_translation_from_google_translate
from schemas import DeleteTranslatedWordSchema, TranslateWordSchema, WordListSchema, WordRetrieveSchema

translator_router = APIRouter(tags=["Translator"])


@translator_router.get("/words", response_model=WordListSchema)
async def words__list(
    search: str | None = Query(None),
    target_lang: Annotated[TranslationLanguageEnum | SkipJsonSchema[None], Query()] = None,
    source_lang: Annotated[TranslationLanguageEnum | SkipJsonSchema[None], Query()] = None,
    limit: int = Query(50, gt=0, le=50),
    offset: int = Query(0, ge=0),
    sorting_order: SortingOrderEnum = Query(SortingOrderEnum.ASC),
    return_full_info: bool = Query(
        description="If true, the full info will be returned (including definitions and synonyms).",
    ),
) -> WordListSchema:
    return WordListSchema(
        words=[
            WordRetrieveSchema.from_db_schema(word)
            for word in await get_words(
                search=search,
                target_lang=target_lang,
                source_lang=source_lang,
                limit=limit,
                offset=offset,
                sorting_order=sorting_order,
                full_document=return_full_info,
            )
        ],
        limit=limit,
        offset=offset,
    )


@translator_router.delete("/words", status_code=status.HTTP_204_NO_CONTENT)
async def words__delete(data: DeleteTranslatedWordSchema) -> Response:
    word = await get_word(data.word, source_lang=data.source_lang, target_lang=data.target_lang)
    if not word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found.")
    await delete_word(data.word, source_lang=data.source_lang, target_lang=data.target_lang)
    return Response()


@translator_router.post("/words/translate", response_model=WordRetrieveSchema)
async def words__translate(
    data: TranslateWordSchema,
) -> WordRetrieveSchema:
    word_from_db = await get_word(data.word, source_lang=data.source_lang, target_lang=data.target_lang)
    if word_from_db:
        return WordRetrieveSchema.from_db_schema(word_from_db)
    result = await get_translation_from_google_translate(
        data.word,
        source_lang=data.source_lang,
        target_lang=data.target_lang,
    )
    await save_word(result)
    return WordRetrieveSchema.from_db_schema(result)
