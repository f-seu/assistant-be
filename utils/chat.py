from assistant_be.settings import BACKEND_URL, MODEL_NAME,MODEL_OUT_TIMEOUT
import logging
from openai import OpenAI


class ChatService:
    def __init__(self):
        self.chat_url = f"{BACKEND_URL}chat/chat"  # 确保URL是正确的
        self.model_name = MODEL_NAME
        self.temperature = 0.7
        self.logger = logging.getLogger("myapp")
        self.client = OpenAI(
            base_url=f"{BACKEND_URL}chat",
            api_key="abc",
        )

    def chat_stream(self, history: list[dict], message: str):
        history.append({
            "role": "user",
            "content": message,
        })
        self.logger.info(f"收到一个流式对话的请求，prompt:{message}")
        stream = self.client.chat.completions.create(
            messages=history,
            model=MODEL_NAME,
            stream=True,
            timeout=MODEL_OUT_TIMEOUT,
        )
        for chunk in stream:
            yield chunk.choices[0].delta.content or ""

    def chat(self, history: list[dict], message: str):
        history.append({
            "role": "user",
            "content": message,
        })
        self.logger.info(f"收到一个非流式对话的请求，prompt:{message}")
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=MODEL_NAME,
            stream=False,
            timeout=MODEL_OUT_TIMEOUT,
        )
        response = chat_completion.choices[0].message.content
        self.logger.info(f"模型回答为:{response}")
        return response

    def chat_with_search_engine(self, history: list[dict], message: str):
        history.append({
            "role": "user",
            "content": message,
        })
        self.logger.info(f"收到一个浏览器对话的请求，prompt:{message}")
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=MODEL_NAME,
            stream=False,
            tools=['search_internet'],
            timeout=MODEL_OUT_TIMEOUT,
        )
        response = chat_completion.choices[0].message.content
        self.logger.info(f"模型回答为:{response}")
        return response

    def chat_with_search_engine_and_knowledgebase(self, history: list[dict], message: str):
        history.append({
            "role": "user",
            "content": message,
        })
        self.logger.info(f"收到一个浏览器对话的请求，prompt:{message}")
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=MODEL_NAME,
            stream=False,
            tools=['search_internet','search_local_knowledgebase'],
            timeout=MODEL_OUT_TIMEOUT,
        )
        response = chat_completion.choices[0].message.content
        self.logger.info(f"模型回答为:{response}")
        return response


if __name__ == "__main__":
    client1 = OpenAI(
        base_url=f"{BACKEND_URL}chat",
        api_key="abc",
    )

    chat_completion1 = client1.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "你好",
            }
        ],
        model=MODEL_NAME,
        stream=False,
        tools=['search_internet'],
    )

    print(chat_completion1)
