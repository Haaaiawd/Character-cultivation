import os
from typing import Any, Dict, Optional

from pydantic import PostgresDsn, model_validator # field_validator is not used in the provided code
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "修仙文字游戏"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    # Using Optional with PostgresDsn for the URI
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @model_validator(mode='before')
    @classmethod # model_validator should be a classmethod
    def build_db_connection_str(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # This function receives the raw values (e.g. from .env or explicit instantiation)
        # BEFORE Pydantic attempts to validate or assign them to the model fields.

        # If SQLALCHEMY_DATABASE_URI is already provided (e.g. directly in .env or passed to constructor),
        # Pydantic will use it. We don't need to do anything special here for that case.
        # Pydantic will later try to validate it against PostgresDsn.
        if values.get('SQLALCHEMY_DATABASE_URI'):
            return values

        # If SQLALCHEMY_DATABASE_URI is NOT provided, try to build it from components.
        db_user = values.get('POSTGRES_USER')
        db_password = values.get('POSTGRES_PASSWORD')
        db_server = values.get('POSTGRES_SERVER')
        db_name = values.get('POSTGRES_DB')

        if all([db_user, db_password, db_server, db_name]):
            # All components are present, so construct the URI.
            # Pydantic will then validate this constructed URI against PostgresDsn.
            values['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_server}/{db_name}"
        # If SQLALCHEMY_DATABASE_URI was not provided AND not all components are present,
        # we don't explicitly raise an error here. Pydantic will handle it:
        # - If SQLALCHEMY_DATABASE_URI remains None, it will be validated against Optional[PostgresDsn].
        #   If it were not Optional, Pydantic would raise a validation error if it's None.
        #   Since it IS Optional, None is acceptable at this stage.
        #   However, for a database connection, you'd typically want this to be non-Optional
        #   or have a check elsewhere in your app startup that ensures it's configured.
        #   For this specific class, allowing None if not buildable is fine as per Optional type.

        return values

    OPENAI_API_KEY: str

    # Pydantic V2 uses SettingsConfigDict for configuration
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore" # Allow and ignore extra fields from .env
    )

# The following lines are for testing and verification as per the subtask.
# In a real application, you would just export `settings = Settings()`
try:
    settings = Settings()
    # print(f"Loaded settings: {settings.model_dump_json(indent=2)}") # For debugging if needed
    # print(f"Database URI: {settings.SQLALCHEMY_DATABASE_URI}")
    # print(f"Project Name: {settings.PROJECT_NAME}")
    # print(f"OpenAI API Key: {settings.OPENAI_API_KEY}")
except Exception as e:
    # print(f"Error loading settings: {e}") # For debugging if needed
    pass # Pass for now, will be checked in bash execution

settings = Settings() # Re-instantiate for export if previous block is commented out for prod.
