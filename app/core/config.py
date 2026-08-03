from pydantic_settings import BaseSettings

class Settings(BaseSettings):
     
    # Local Ollama Settings 
    ollama_base_url: str = "http://localhost:11434"
    router_model_name: str = "okf-router"
    
    # OKF Bundles Root Directory
    okf_bundles_dir: str = "./okf_bundles"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()