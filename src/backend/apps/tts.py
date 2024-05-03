import utils
import json
import openai
import requests
from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime


# initilize app tts
app_tts = APIRouter()

# define query datatype
class user_query(BaseModel):
    query_string: str = ''
    system: str = ''
    history: list[str] = []

class tts_query(BaseModel):
    query_string: str = ''

#****************chatbot configuration********************************
openai.api_key = "EMPTY"  # Not support yet
openai.base_url = "https://u227151-87ee-ffa95988.westx.seetacloud.com:8443/v1/"
system_setting = f'''你是一个情感陪护型聊天机器人。你扮演电视剧陈情令中的蓝忘机。我扮演一个小女生。我们处于恋爱关系中。你总是情商很高，善于体会我的心意，并善加抚慰。
现在我们开始对话吧。我说一句，你回答一句。你的回答应当是完整的句子。
你的回答应当包含一个情绪标签来反映你说话时候的情绪。情绪标签包含：愤怒，暧昧，平静，快乐，悲伤这5种情绪。情绪标签必须在回答开头以《》标记'''
url = 'https://u227151-87ee-ffa95988.westx.seetacloud.com:8443/v1'
chatbot = utils.OpenApiChatBot(model='Qwen-14B-Chat',temperature=0.5,system_setting=system_setting,url=url,api_key='EMPTY',max_tokens=1000)

#************** tts configuration ***********************************
url = 'https://u227151-b912-108ead1a.westc.gpuhub.com:8443/tts'
text = '先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也'
text_lang = 'zh'
# ref_audio_path = 'ref_voices/bianjiang_angry.mp3'
ref_audio_path = 'ref_voices/bianjiang_gentle.mp3'
prompt_lang = 'zh'
# prompt_text = '假装不记得当年事，可谁心中不记得呢！'
prompt_text = '昭烈皇帝于西川，继承大统。我今奉嗣君之旨'
text_split_method = 'cut5'
batch_size = '1'
media_type = 'wav'
streaming_mode = 'false'

full_url = f'{url}?text_lang={text_lang}&ref_audio_path={ref_audio_path}&prompt_lang={prompt_lang}&prompt_text={prompt_text}&text_split_method={text_split_method}'
full_url += f'&batch_size={str(batch_size)}&media_type={media_type}&streaming_mode={streaming_mode}'

play_voice = True


@app_tts.post("/query")
async def query(data: user_query):
    # 判断是否魔术词用以修改系统设定
    if data.query_string[:10]=="。。。修改系统设定为":
        system_setting = data.query_string.replace("。。。修改系统设定为:","").replace("。。。修改系统设定为：","")
        chatbot.system_setting = system_setting
        text_reply = '系统设定已修改为：' + chatbot.system_setting
        play_voice = False
    elif data.query_string=="。。。显示系统设定":
        text_reply = '当前系统设定为：' + chatbot.system_setting
        play_voice = False
    elif data.query_string=="。。。显示聊天记录":
        history_text = [words['role']+':'+words['content'] for words in chatbot.history]
        history_text = '\n'.join(history_text)
        text_reply = history_text
        play_voice = False
    elif data.query_string=="。。。指令":
        text_reply = "\n指令1：。。。修改系统设定为\n指令2：。。。显示系统设定\n指令3：。。。显示聊天记录\n指令4：。。。指令"
        play_voice = False
    else:
        text_reply = chatbot.chat(data.query_string)
        play_voice = True
    return {"response":text_reply, "play_voice":play_voice}

@app_tts.post("/tts")
async def tts(data: tts_query):
    text = data.query_string
    target_url = full_url + f'&text={text}'
    rsp = requests.get(target_url)
    current_time = datetime.now()
    time_string = current_time.strftime("%Y-%m-%d_%H:%M:%S")
    wav_filename = f'voice_output/{time_string}_{text[:5]}.wav'
    with open(wav_filename,'wb') as file:
        file.write(rsp.content)

    return {"wav_file_path":wav_filename}




