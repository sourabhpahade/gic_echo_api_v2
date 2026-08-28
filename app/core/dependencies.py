
from core.config import settings
from services.llm_router_service import LLMRouterService
from services.helper_service import HelperService
from services.sql_execution_service import SQLExecutionService
from services.data_analysis_service import DataAnalysisService
from services.pageindex_service import PageIndexService
from services.tree_based_llm_search_service import TreeBasedLLMSerach

def get_llm_router_service() -> LLMRouterService:
    return LLMRouterService( 
        base_url=settings.ollama_base_url,
        model_name=settings.router_model_name
    )

def get_helper_service() -> HelperService:
    return HelperService()

def get_sql_execution_service() -> SQLExecutionService:
    return SQLExecutionService()

def get_data_analysis_service() -> DataAnalysisService:
    return DataAnalysisService()

def get_page_index_service() -> PageIndexService:
    return PageIndexService()

def get_tree_based_llm_search_service() -> TreeBasedLLMSerach:
    return TreeBasedLLMSerach()