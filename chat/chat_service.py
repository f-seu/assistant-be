import requests
from assistant_be.settings import BACKEND_URL
import json
class ChatService:
    def __init__(self):
        self.chat_url = f"{BACKEND_URL}/chat/chat"  # 确保URL是正确的

    def chat(self, history: list[dict], message: str):
        data = {
            "query": message,
            "conversation_id": "",
            "history_len": -1,
            "history": history,
            "stream": True,
            "model_name": "chatglm3-6b",
            "temperature": 0.7,
            "max_tokens": 0,
            "prompt_name": "default"
        }

        with requests.post(self.chat_url, json=data, stream=True) as response:
            response.raise_for_status()  # 确保连接成功
            for line in response.iter_lines():
                if line:  # 过滤掉可能的空行
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        event_data = decoded_line.split('data: ')[1]
                        yield json.loads(event_data)  # 安全地解析JSON数据

if __name__ == '__main__':
    chat_service = ChatService()
    history1 = [
        {
            "role": "user",
            "content": "我们来玩成语接龙，我先来，生龙活虎"
        },
        {
            "role": "assistant",
            "content": "虎头虎脑"
        }
    ]
    msg = "恼羞成怒"
    for res in chat_service.chat(history1,msg):
        print(res)

