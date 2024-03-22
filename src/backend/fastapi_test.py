import uvicorn
import utils
import json
from fastapi import FastAPI
from apps.web import *
from apps.miniapp import *
from fastapi.templating import Jinja2Templates


app = FastAPI()

app.include_router(app_web, prefix="/app_web", tags=['web api'])
app.include_router(app_mini, prefix="/app_mini", tags=['web api'])

templates = Jinja2Templates(directory='./templates')

@app.get("/index")
async def index():
    
    return templates.TemplateResponse(
        ""
    )

@app.get("/chat")
async def shop():
    return {"shop": "..."}

if __name__ == "__main__":
    uvicorn.run('fastapi_test:app', port=241, reload=True)