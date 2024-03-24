import utils
import json
from fastapi import APIRouter
from pydantic import BaseModel, Field

# load configuration
with open('../../config/local_pass.txt','r') as f:
    local_pass = f.read()
local_pass = json.loads(local_pass)
# 基本的websocket设置

gpt_url = "wss://spark-api.xf-yun.com/v3.5/chat"
domain = "generalv3.5"
appid = local_pass['appid']
api_key = local_pass['api_key']
api_secret = local_pass['api_secret']
# 按照基本配置生成一个ws配置实体，用于实时生成url
wsParam = utils.Websocket_Param(appid, api_key, api_secret, gpt_url, domain)

# initilize app web
app_web = APIRouter()

# define query datatype
class user_query(BaseModel):
    query_string: str = ''
    system: str = ''
    history: list[str] = []


@app_web.post("/invoke/")
async def invoke(data: user_query):
    llm_rsp,llm_history = utils.chat_with_xunfei(data.query_string, wsParam, system=data.system, history=data.history, debug=False)
    return {"response":llm_rsp}





