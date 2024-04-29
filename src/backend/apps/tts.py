import utils
import json
import openai
from fastapi import APIRouter
from pydantic import BaseModel, Field


# initilize app tts
app_tts = APIRouter()

# define query datatype
class user_query(BaseModel):
    query_string: str = ''
    system: str = ''
    history: list[str] = []


openai.api_key = "EMPTY"  # Not support yet
openai.base_url = "https://u227151-87ee-ffa95988.westx.seetacloud.com:8443/v1/"
system_setting = f'''你是一个情感陪护型聊天机器人。你扮演电视剧陈情令中的蓝忘机。我扮演一个小女生。我们处于恋爱关系中。你总是情商很高，善于体会我的心意，并善加抚慰。
现在我们开始对话吧。我说一句，你回答一句。你的回答应当是完整的句子。'''
url = 'https://u227151-87ee-ffa95988.westx.seetacloud.com:8443/v1'
chatbot = utils.OpenApiChatBot(model='Qwen-14B-Chat',temperature=0.5,system_setting=system_setting,url=url,api_key='EMPTY',max_tokens=1000)


@app_tts.post("/invoke/")
async def invoke(data: user_query):
    text_reply = chatbot.chat(data.query_string)
    return {"response":text_reply}