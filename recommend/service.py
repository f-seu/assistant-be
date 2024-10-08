import datetime

from hanlp_restful import HanLPClient
from utils.chat import ChatService
import logging
import requests
import re
import json
from assistant_be.settings import TMDB_KEY

class RecommendService(object):
    def __init__(self):
        self.chat = ChatService()
        self.logger = logging.getLogger('myapp')

    def get_music(self, num):
        prompt = (f'请根据知识库，推荐{num}个我可能喜欢的音乐，给出我一个json格式的list，确保输出是紧凑格式的有效 JSON 对象，不包含任何其他解释、转义符、换行符或反斜杠。每个元素里面包含一个title和一个reason，title是音乐的名字，reason'
                  f'是推荐的原因，推荐原因用一句话说明即可，不要有额外的内容。例如你应该输出:[{{"title":"标题","reason":"原因"}}]')

        self.logger.info(f"正在尝试推荐音乐，prompt为：{prompt}")
        results = self.chat.chat_with_search_engine_and_knowledgebase([], prompt)

        result = results.split("```")[-1]
        if len(result) < 10:
            result = results[-2]
        try:
            result = result.replace("json","")
            result = result.lstrip("\n")

            results = json.loads(result)
            idx = 0
            for result in results:
                title = result['title']
                title,poster,url = self.get_music_poster_and_title(title)
                # result['title'] = title
                result['poster'] = poster
                result['url'] = url
                result['id'] = idx
                result['update_time'] = datetime.datetime.now().strftime("%H:%M:%S")
                idx += 1
            modified_results = json.dumps(results, ensure_ascii=False, indent=2)
            return modified_results
        except Exception as err:
            import traceback
            traceback.print_exc()
            raise AssertionError("模型输出解析失败")

    def get_movie(self, num):
        prompt = (f'请根据知识库，推荐{num}个我可能喜欢的电影，给出我一个json格式的list，确保输出是紧凑格式的有效 JSON 对象，不包含任何其他解释、转义符、换行符或反斜杠。每个元素里面包含一个title和一个reason，title是电影的名字，reason'
                  f'是推荐的原因，推荐原因用一句话说明即可，不要有额外的内容。例如你应该输出:[{{"title":"标题","reason":"原因"}}]')

        self.logger.info(f"正在尝试推荐电影，prompt为：{prompt}")
        results = self.chat.chat_with_search_engine_and_knowledgebase([], prompt)

        # 修正正则表达式以匹配正确的内容
        result = results.split("```")[-1]
        if len(result) < 10:
            result = results[-2]
        try:
            result = result.replace("json","")
            result = result.lstrip("\n")
            results = json.loads(result)
            idx = 0
            for result in results:
                title = result['title']
                title,poster,url = self.get_movie_poster_and_title(title)
                # result['title'] = title
                result['poster'] = poster
                result['url'] = url
                result['id'] = idx
                idx += 1
            modified_results = json.dumps(results, ensure_ascii=False, indent=2)
            return modified_results
        except Exception as err:
            import traceback
            traceback.print_exc()
            raise AssertionError("模型输出解析失败")

    def get_movie_poster_and_title(self,name):
        url = f'https://api.themoviedb.org/3/search/movie?query={name}&api_key={TMDB_KEY}'
        res = requests.get(url,timeout=10,proxies=[])
        res = res.json()
        res = res['results'][0]
        name = res['title']
        poster = res['poster_path']
        poster = f'https://image.tmdb.org/t/p/w500/{poster}'
        movie_id = res['id']
        url = f'https://www.themoviedb.org/movie/{movie_id}'
        return name,poster,url

    def get_music_poster_and_title(self,name):
        url = f"https://dataiqs.com/api/kgmusic/?msg={name}&type=mv&n=0"
        res = requests.get(url,timeout=10,proxies=[])
        res = res.json()
        res = res['data']
        name = res['name']
        poster = res['cover_url']
        url = res['mv_url']
        return name, poster, url
