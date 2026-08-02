from pydantic import BaseSettings

class Settings(BaseSettings):
    bundle_path: str = "./okf_bundles" # Fallback if .env is missing

    routing_llm_base_url: str = "http://localhost:11434/v1"
    routing_llm_model_name: str = "sqlcoder"
    routing_llm_api_key: str = "local" # not in use for local llm, just a placeholder for future use

    sql_dialect: str = "MS SQL Server (T-SQL)"
    
    class Config:
        env_file = ".env"

settings = Settings()