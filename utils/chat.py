from assistant_be.settings import BACKEND_URL, MODEL_NAME
import requests
import json
import logging
import re

class ChatService:
    def __init__(self):
        self.chat_url = f"{BACKEND_URL}chat/chat"  # 确保URL是正确的
        self.model_name = MODEL_NAME
        self.temperature = 0.7
        self.logger = logging.getLogger("myapp")

    def chat_stream(self, history: list[dict], message: str):
        data = {
            "query": message,
            "conversation_id": "",
            "history_len": -1,
            "history": history,
            "stream": True,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": 0,
            "prompt_name": "default"
        }
        self.logger.info(f"收到一个流式的请求，prompt:{message}")

        with requests.post(self.chat_url, json=data, stream=True) as response:
            response.raise_for_status()  # 确保连接成功
            for line in response.iter_lines():
                if line:  # 过滤掉可能的空行
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        event_data = decoded_line.split('data: ')[1]
                        yield json.loads(event_data)  # 安全地解析JSON数据

    def chat(self, history: list[dict], message: str):
        data = {
            "query": message,
            "conversation_id": "",
            "history_len": -1,
            "history": history,
            "stream": False,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": 0,
            "prompt_name": "default"
        }
        self.logger.info(f"收到一个对话的请求，prompt:{message}")
        response = requests.post(self.chat_url, json=data)
        response.raise_for_status()
        self.logger.info(f"返回结果:{response.status_code},{response.text}")
        response = response.text
        if response.startswith('data:'):
            event_data = response.split('data: ')[1]
            return json.loads(event_data)['text']  # 安全地解析JSON数据
        return ""

    def chat_with_search_engine(self, history: list[dict], message: str):
        url = f"{BACKEND_URL}chat/search_engine_chat"  # 确保URL是正确
        data = {
            "query": message,
            "top_k": 1,
            "search_engine_name": "duckduckgo",
            "history": history,
            "stream": False,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": 0,
            "prompt_name": "default"
        }
        self.logger.info(f"收到一个与搜索引擎对话的请求，prompt:{message}")
        response = requests.post(url, json=data)
        response.raise_for_status()
        self.logger.info(f"返回结果:{response.status_code},{response.text}")
        response = response.text
        match = re.search(r'data: ({.*?})', response, re.DOTALL)
        if not match:
            return None
        json_str = match.group(1)
        return json.loads(json_str)['answer']
