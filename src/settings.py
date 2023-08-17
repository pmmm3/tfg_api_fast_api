from pydantic import ConfigDict, BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    token_secret: str
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


class FrontURL(BaseSettings):
    ACTIVATE_ACCOUNT_URL: AnyHttpUrl
    RESET_PASSWORD_URL: AnyHttpUrl
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
