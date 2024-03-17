import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def home():
    return {"user_id": 1001}

@app.get("/shop")
async def shop():
    return {"shop": "..."}

if __name__ == "__main__":
    uvicorn.run('fastapi_test:app', port=8080, reload=True)