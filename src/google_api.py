from google.auth.api_key import Credentials
from google.cloud import translate_v2
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from config import settings
from db import WordTranslationDBSchema
from enums import TranslationLanguageEnum


class GoogleTranslateV2Response(BaseModel):
    input: str
    detectedSourceLanguage: TranslationLanguageEnum | None = None
    translatedText: str


async def get_translation_from_google_translate(
    word: str,
    source_lang: TranslationLanguageEnum | None = None,
    target_lang: TranslationLanguageEnum = TranslationLanguageEnum.ENGLISH,
) -> WordTranslationDBSchema:
    return await run_in_threadpool(_get_translation_from_google_translate, word, source_lang, target_lang)


def _get_translation_from_google_translate(
    word: str,
    source_lang: TranslationLanguageEnum | None = None,
    target_lang: TranslationLanguageEnum = TranslationLanguageEnum.ENGLISH,
) -> WordTranslationDBSchema:
    client = translate_v2.Client(
        credentials=Credentials(settings.API_KEY.get_secret_value()),  # type: ignore[no-untyped-call]
    )
    result = GoogleTranslateV2Response.model_validate(
        client.translate(
            word,
            target_language=target_lang,
            source_language=source_lang,
        ),
    )
    return WordTranslationDBSchema(
        word=word,
        target_lang=target_lang,
        source_lang=result.detectedSourceLanguage or source_lang,
        definitions=[
            word,
            result.translatedText,
        ],
        synonyms=[word, result.translatedText],
        translations=[result.translatedText],
    )
