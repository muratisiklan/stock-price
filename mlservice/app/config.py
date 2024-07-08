from pydantic_settings import BaseSettings


class SettingsApi(BaseSettings):
    mongo_url:str

    # class Config:
    #     env_file = "../.env.mlservice"


settings_api = SettingsApi()
