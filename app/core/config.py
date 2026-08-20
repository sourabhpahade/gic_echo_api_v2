from pydantic_settings import BaseSettings

class Settings(BaseSettings):
     
    # Local Ollama Settings 
    ollama_base_url: str = "http://localhost:11434"
    router_model_name: str = "okf-router"
    sqlcoder_model_name: str = "okf-sqlcoder"
    data_analysis_model_name : str = ""
    
    # OKF Bundles Root Directory
    okf_bundles_dir: str = "./okf_bundles"

    DB_CONNECTION_STRING : str = ""
    DB_CONNECTION_TIMEOUT : int = 10
    DB_QUERY_TIMEOUT : int = 15
    DB_FETCH_LIMIT : int = 100  # Set to -1 to fetch all records

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()