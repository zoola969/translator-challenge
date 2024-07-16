from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: SecretStr
    MONGO_HOST: str = "localhost"
    MONDO_PORT: int = 27017
    MONGO_DB_NAME: str = "translates"
    MONGO_COLLECTION_NAME: str = "words"
    API_KEY: SecretStr

    @property
    def MONGO_DSN(self) -> SecretStr:
        return SecretStr(
            f"mongodb://"
            f"{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD.get_secret_value()}"
            f"@{self.MONGO_HOST}:{self.MONDO_PORT}",
        )


settings = Settings(_env_file="../.env")  # for start in local mode with .venv
