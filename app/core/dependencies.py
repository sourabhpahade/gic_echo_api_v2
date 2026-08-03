from core.config import settings
from services.llm_router_service import LLMRouterService
from services.okf_dependency_service import OKFDependencyService

def get_llm_router_service() -> LLMRouterService:
    return LLMRouterService(
        base_url=settings.ollama_base_url,
        model_name=settings.router_model_name
    )

def get_okf_dependency_service() -> OKFDependencyService:
    return OKFDependencyService()