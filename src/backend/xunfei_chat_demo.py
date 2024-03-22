import sys
import utils
import json

with open('../local_pass.txt','r') as f:
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

def main():
    system = '你是一个聊天机器人，你的任务就是陪幼儿玩过家家的游戏。你的回复应当简洁而易于理解，情绪投入而无冗余的话语'
    print(f'system setting: {system}\n')
    query = '我们一起来玩过家家吧。'
    print(f'user: {query}\n')
    rsp,history = utils.chat_with_xunfei(query, wsParam, system=system, history=[], debug=False)
    print(f'assistant: {rsp}\n')
    
    query = '我来扮演妈妈，你来扮演姐姐, 她来扮演宝宝'
    print(f'user: {query}\n')
    rsp,history = utils.chat_with_xunfei(query, wsParam, system=system, history=history, debug=False)
    print(f'assistant: {rsp}\n')
    
    print('---------------------------------------')
    print(f'total chat history: {history}')
    
if __name__ == '__main__':
    main()
    
          