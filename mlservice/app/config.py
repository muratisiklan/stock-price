from pydantic_settings import BaseSettings


class SettingsApi(BaseSettings):
    mongo_url:str
    app_host: str
    app_port: int

    # class Config:
    #     env_file = "../.env.mlservice"


settings_api = SettingsApi()
