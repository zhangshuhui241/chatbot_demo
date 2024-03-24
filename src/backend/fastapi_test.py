import uvicorn
import utils
import json
from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from apps.web import *
from apps.restapi import *
from fastapi.templating import Jinja2Templates


app = FastAPI()
# init static files
app.mount("/statics",StaticFiles(directory="statics"))
# init additional rounter files
app.include_router(app_web, prefix="/app_web", tags=['web api'])
app.include_router(app_rest, prefix="/app_rest", tags=['api rest'])

templates = Jinja2Templates(directory='./templates')

@app.get("/index")
async def index(request:Request):
    user_input = ""
    history_text = ""
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "user_input":user_input,
            "history_text":history_text,
        }
    )

@app.get("/test")
async def test():
    return {"test": "Go back home, boy. There nothing here."}

if __name__ == "__main__":
    uvicorn.run('fastapi_test:app', port=241, reload=True)