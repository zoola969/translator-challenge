import requests
from fastapi import APIRouter, Response
from starlette import status

system_roter = APIRouter(tags=["System"])

_WORDS = [
    "time",
    "year",
    "people",
    "way",
    "school",
    "state",
    "family",
    "student",
    "point",
    "home",
    "water",
    "room",
    "mother",
    "area",
    "money",
    "story",
    "health",
    "history",
    "party",
    "result",
    "change",
    "morning",
    "reason",
    "research",
    "girl",
    "guy",
    "moment",
    "air",
    "teacher",
    "force",
    "education",
]


_LANGUAGES = [
    "it",
    "fr",
    "es",
    "ja",
    "la",
]


@system_roter.post("/system/words/populate", status_code=status.HTTP_204_NO_CONTENT)
def populate_words() -> Response:
    """Insert 30 english words with translations to 5 languages."""
    with requests.Session() as session:
        for word in _WORDS:
            for lang in _LANGUAGES:
                session.post(
                    "http://localhost:80/words/translate",
                    json={"word": word, "source_lang": "en", "target_lang": lang},
                )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
