from hanlp_restful import HanLPClient
from utils.chat import ChatService
import logging
import requests
from assistant_be.settings import HEFENG_KEY, HEFENG_HOST


# 获取一个名为 'myapp' 的日志记录器

class CalendarService(object):
    def __init__(self):
        self.chat = ChatService()
        self.logger = logging.getLogger('myapp')
        self.hanlp = HanLPClient('https://www.hanlp.com/api', auth=None, language='zh')  # auth不填则匿名，zh中文，mul多语种

    def get_plan(self, year, month, day, content):

        weather_prompt = ""
        positions = self.get_calendar_positions(content)
        if len(positions) != 0:
            weather_prompt += "注意以下是部分地点的天气："

        seen = set()
        unique_positions = []
        for position in positions:
            if position not in seen:
                unique_positions.append(position)
                seen.add(position)

        positions = unique_positions
        num_positions = len(positions)

        for i, position in enumerate(positions):
            weather_prompt += f"{position}:{self.get_weather(position, year, month, day)}"
            if i < num_positions - 1:
                weather_prompt += ","
            else:
                weather_prompt += "。"

        prompt = f"我{year}年{month}月{day}的行程为{content}。{weather_prompt}帮我看一下车票之类的, 结合以上内容，详细的为我规划这天的行程安排推荐，如果需要乘坐公共交通工具，例如高铁，请给出我具体车次。如果要乘坐地铁，请给出我具体几号线到哪一站。"

        self.logger.info(f"正在尝试规划行程，prompt为：{prompt}")
        result = self.chat.chat_with_search_engine([], prompt)
        self.logger.info(f"结果：{result}")
        return result

    def get_weather(self, position, year, month, day):
        self.logger.info(f"正在获取{position}的天气")

        def get_weather_str(weather_obj):
            return f"{weather_obj['textDay']},{weather_obj['windDirDay']}{weather_obj['windScaleDay']}级，最高温度{weather_obj['tempMax']},最低温度{weather_obj['tempMin']}"

        logger = logging.getLogger('myapp')

        url = f"https://geoapi.qweather.com/v2/city/lookup?location={position}&key={HEFENG_KEY}&number=1"
        logger.info(f"尝试获取地点id:{url}")
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"获取地点id失败，{position}状态码{response.status_code}")
            return "获取天气失败，请忽略"
        response = response.json()
        if response['code'] != "200":
            logger.error(f"获取地点id失败，{position}code为{response['code']}")
            return "获取天气失败，请忽略"
        location = response['location'][0]['id']

        url = f"https://{HEFENG_HOST}/v7/weather/30d?location={location}&key={HEFENG_KEY}"
        response = requests.get(url=url)
        if response.status_code != 200:
            logger.error(f"获取天气失败,{position}状态码{response.status_code}")
            return "获取天气失败，请忽略"

        data = response.json()

        if data["code"] != "200":
            logger.error(f"获取天气失败，{position}code为{data['code']}")
            return "获取天气失败，请忽略"

        target_date_str = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        for daily_forecast in data["daily"]:
            if daily_forecast["fxDate"] == target_date_str:
                weather_str = get_weather_str(daily_forecast)
                logger.info(f"{position}天气获取成功:{weather_str}")
                return weather_str

        return "获取天气失败，请忽略"

    def get_calendar_positions(self, content):
        result = self.hanlp.parse(content, tasks='ner/msra')
        result = result['ner/msra']
        positions = list()
        for sentence in result:
            for item in sentence:
                if item[1] == "LOCATION":
                    positions.append(item[0])
        return positions
#
#
#
# def get_weather(position,year,month,day):
#     logger = logging.getLogger('myapp')
#
#     url = f"https://geoapi.qweather.com/v2/city/lookup?location={position}&key={HEFENG_KEY}&number=1"
#     logger.info(f"尝试获取地点id:{url}")
#     response = requests.get(url)
#     if response.status_code != 200:
#         logger.error(f"获取地点id失败，{position}状态码{response.status_code}")
#         return "获取天气失败，请忽略"
#     response = response.json()
#     if response['code'] != "200":
#         logger.error(f"获取地点id失败，{position}code为{response['code']}")
#         return "获取天气失败，请忽略"
#     location = response['location'][0]['id']
#
#     url = f"https://{HEFENG_HOST}/v7/weather/30d?location={location}&key={HEFENG_KEY}"
#     response = requests.get(url=url)
#     if response.status_code != 200:
#         logger.error(f"获取天气失败,{position}状态码{response.status_code}")
#         return "获取天气失败，请忽略"
#
#     data = response.json()
#
#     if data["code"] != "200":
#         logger.error(f"获取天气失败，{position}code为{data['code']}")
#         return "获取天气失败，请忽略"
#
#     target_date_str = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
#     for daily_forecast in data["daily"]:
#         if daily_forecast["fxDate"] == target_date_str:
#             weather_str = get_weather_str(daily_forecast)
#             logger.info(f"{position}天气获取成功:{weather_str}")
#             return weather_str
#
#     return "获取天气失败，请忽略"
#
# class CalendarService:
#     def __init__(self):
#         self.chat_url = f"{BACKEND_URL}chat/knowledge_base_chat"  # 确保URL是正确的
#         self.model_name = MODEL_NAME
#         self.temperature = 0.7
#         self.chat = CalendarChatService()
#
#     def get_calendar(self, year, month, day):
#
#         prompt = f"请你根据我{year}年{month}月{day}日的安排，为我推荐一个行程"
#
#         positions = self.chat.get_calendar_positions(year, month, day)
#         if len(positions) != 0:
#             prompt += ",注意以下是部分地点的天气："
#
#         seen = set()
#         unique_positions = []
#         for position in positions:
#             if position not in seen:
#                 unique_positions.append(position)
#                 seen.add(position)
#
#         positions = unique_positions
#         num_positions = len(positions)
#
#         for i, position in enumerate(positions):
#             prompt += f"{position}:{get_weather(position,year,month,day)}"
#             if i < num_positions - 1:
#                 prompt += ","
#
#         logging.info(prompt)
#         data = {
#             "query": prompt,
#             "knowledge_base_name": "samples",
#             "top_k": 3,
#             "score_threshold": 1,
#             "history": [],
#             "stream": False,
#             "model_name": self.model_name,
#             "temperature": self.temperature,
#             "max_tokens": 0,
#             "prompt_name": "default"
#         }
#
#         response = requests.post(self.chat_url, json=data)
#         response.raise_for_status()
#         response = response.text
#         if response.startswith('data:'):
#             event_data = response.split('data: ')[1]
#             result = json.loads(event_data)
#             result = result['answer']
#             return result  # 安全地解析JSON数据
#         return ""
#
#
# class CalendarChatService:
#     def __init__(self):
#         self.chat_url = f"{BACKEND_URL}chat/knowledge_base_chat"  # 确保URL是正确的
#         self.model_name = MODEL_NAME
#         self.temperature = 0.7
#         self.hanlp = HanLPClient('https://www.hanlp.com/api', auth=None, language='zh')  # auth不填则匿名，zh中文，mul多语种
#
#     # def get_calendar_str(self, year, month, day):
#     #     data = {
#     #         "query": f"请你根据知识库，列一下{year}年{month}月{day}日我有哪些日程",
#     #         "conversation_id": "",
#     #         "history_len": -1,
#     #         "history": [],
#     #         "stream": False,
#     #         "model_name": self.model_name,
#     #         "temperature": self.temperature,
#     #         "max_tokens": 0,
#     #         "prompt_name": "default"
#     #     }
#     #
#     #     response = requests.post(self.chat_url, json=data)
#     #     response.raise_for_status()
#     #     response = response.text
#     #     if response.startswith('data:'):
#     #         event_data = response.split('data: ')[1]
#     #         return json.loads(event_data)['text']  # 安全地解析JSON数据
#     #     return None
#
#     def get_calendar_positions(self, year, month, day):
#         data = {
#             "query": f"请你根据知识库，说明{year}年{month}月{day}日我要去哪些地点",
#             "knowledge_base_name": "samples",
#             "top_k": 3,
#             "score_threshold": 1,
#             "history": [],
#             "stream": False,
#             "model_name": self.model_name,
#             "temperature": self.temperature,
#             "max_tokens": 0,
#             "prompt_name": "default"
#         }
#
#         response = requests.post(self.chat_url, json=data)
#         response.raise_for_status()
#         response = response.text
#
#         match = re.search(r'data: ({.*?})', response, re.DOTALL)
#         if not match:
#             return []
#         json_str = match.group(1)
#         result = json.loads(json_str)
#         result = result['answer']
#         result = self.hanlp.parse(result, tasks='ner/msra')
#         result = result['ner/msra']
#         positions = list()
#         for sentence in result:
#             for item in sentence:
#                 if item[1] == "LOCATION":
#                     positions.append(item[0])
#         return positions
#
