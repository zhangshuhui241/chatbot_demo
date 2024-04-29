import os
import time
import base64
import hashlib
import hmac
import json
import ssl
import openai
import websocket
import _thread as thread
from urllib.parse import urlparse
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time


# 这个class用来保存websocket的基本配置参数，并且动态生成url
class Websocket_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, gpt_url, domain):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.domain = domain
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url
    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url
    
# 下面是websocket运行过程中需要使用的辅助函数
# 收到websocket错误的处理
def websocket_on_error(ws:websocket.WebSocketApp, error):
    print("### error:", error)

# 收到websocket关闭的处理
def websocket_on_close(ws, *args):
    if ws.debug:
        print(*args)
        print("### closed ###")

# 收到websocket连接建立的处理
def websocket_on_open(ws):
    thread.start_new_thread(websocket_run, (ws,))

# 下面是websocket运行函数
def websocket_run(ws, *args):
    data,history = gen_params(ws, query=ws.query)
    if ws.debug:
        print(f'websocket run data:{data}\nhistory:{history}')
    data = json.dumps(data)
    ws.history = history
    ws.send(data)

# 收到websocket消息的处理
def websocket_on_message(ws, message, debug=False):
    # print(message)
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        ws.response += content
        if ws.debug: print(content)
        if status == 2:
            if ws.debug: 
                print("#### 关闭会话")
            ws.close()
            
# 此函数用于生成websocket的请求信息
def gen_params(ws, query, debug=False):
    """
    通过appid和用户的提问来生成请参数
    """
    # 如果没有历史对话，那么直接将系统设定加入到空白历史对话中
    if len(ws.history)==0:
        ws.history = [{'role':'system','content':ws.system}]
    # 如果有历史对话，并且有系统设定，那么替换掉最开头的系统设定
    elif len(ws.system) > 0 and len(ws.history) > 0:
        ws.history = [{'role':'system','content':ws.system}] + ws.history[1:]
    else:
        pass
    ws.history += [{"role": "user", "content": query}]
    if debug:
        print(f'gen params history: {ws.history}')
    data = {
        "header": {
            "app_id": ws.appid,
            "uid": "1234",           
            # "patch_id": []    #接入微调模型，对应服务发布后的resourceid          
        },
        "parameter": {
            "chat": {
                "domain": ws.domain,
                "temperature": 0.6,
                "max_tokens": 4096,
                "auditing": "default",
            }
        },
        "payload": {
            "message": {
                "text": ws.history
            }
        }
    }
    return data, ws.history


def chat_with_xunfei(query, wsParam, history=[],system='', debug=False):
    url = wsParam.create_url()
    ws = websocket.WebSocketApp(url,
                                on_message=websocket_on_message, 
                                on_error=websocket_on_error, 
                                on_close=websocket_on_close, 
                                on_open=websocket_on_open)
    ws.response = ''
    ws.debug = debug
    websocket.enableTrace(False)
    ws.appid = wsParam.APPID
    ws.domain = wsParam.domain
    ws.query = query
    ws.history = history
    ws.system = system
    ws.debug = debug
    _ = ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    history = ws.history + [{"role": "assistant", "content": ws.response}]
    return ws.response, history


class OpenApiChatBot(object):

    def __init__(self,model='Qwen-14B-Chat',temperature=0.5,system_setting='',url='',api_key='EMPTY',max_tokens=1000,history=[]):
        self.model = model
        self.temperature = temperature
        self.system_setting = system_setting
        self.url = url
        self.api_key = api_key
        self.max_tokens = 1000
        self.history = []
        return
    
    def chat(self,user_input):
        system_messages = [{'role':'user','content':self.system_setting},
                           {'role':'assistant','content':'好的，我们现在就开始吧。'}]
        history_messages = self.history
        user_messages = [{'role':'user','content':user_input}]
        messages = system_messages + history_messages + user_messages
        reply = self.invoke(messages)
        self.history = self.history + user_messages + [{'role':'assistant','content':reply}]
        return reply
    
    def invoke(self,messages,debug=False):
        # 这个方法用于单次调用大模型的应答能力
        res = openai.chat.completions.create(model=self.model, messages=messages, stream=True, temperature=self.temperature)
        reply = ''
        for chunk in res:
            try:
                content = chunk.choices[0].delta.content
                if content is None:
                    content = ""
            except Exception as e:
                content = chunk.choices[0].delta.get("content", "")
            reply += content
            if debug:
                print(f'invoke: messages = {messages}, reply = {reply}')
        return reply
        
    
    def summary(self,num_records,debug=False):
        contexts = [ct['role'] + ':' + ct['content'] for ct in self.history[:num_records]]
        context = '\n'.join(contexts)
        messages = [{'role':'user','content':f'请将下面用<>括起来的文字进行归纳总结，字数不超过100。<{context}>'}]
        summary = self.invoke(messages)
        if debug:
            print(f'context: {context} \n summary: {summary}')
        return summary