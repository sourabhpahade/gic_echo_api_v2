# import FastAPI from fastapi module
from fastapi import FastAPI
from controllers.query_controller import router as query_router
from controllers.page_index_controller import router as page_index_router
from controllers.tree_based_search_controller import router as tree_based_search_router



# initialize FastAPI app
app = FastAPI(title="GIS ECHO API")

app.include_router(query_router)  # Include the router from query_controller.py
app.include_router(page_index_router)  # Include the router from query_controller.py
app.include_router(tree_based_search_router)  

# endpoints
@app.get("/handshake") 
async def root() : 
    return {"message": "Hello World"}

