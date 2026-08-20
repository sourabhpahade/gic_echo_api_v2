# import FastAPI from fastapi module
from fastapi import FastAPI
from controllers.query_controller import router as query_router


# initialize FastAPI app
app = FastAPI(title="GIS ECHO API")

app.include_router(query_router)  # Include the router from query_controller.py

# endpoints
@app.get("/handshake") 
async def root() : 
    return {"message": "Hello World"}

