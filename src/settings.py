from pydantic import ConfigDict, BaseSettings


class Settings(BaseSettings):
    token_secret: str
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
