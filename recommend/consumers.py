import datetime
import logging

from django.utils.timezone import now

from .models import RecommendModel
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
import subprocess
from utils.chat import ChatService
from .models import AppOpenModel
import threading

from .serializers import RecommendModelSerializer

path_to_name = {
    "/usr/share/applications/qq.desktop": "qq",
    "/usr/share/applications/code.desktop": "vscode",
    "/usr/share/applications/bytedance-feishu.desktop": "飞书",
}
name_to_path = {
    "qq": "/usr/share/applications/qq.desktop",
    "vscode": "/usr/share/applications/code.desktop",
    "飞书": "/usr/share/applications/bytedance-feishu.desktop",
}
apps_desc = {
    "qq": "一个社交软件",
    "飞书": "一个工作办公软件",
    "vscode": "一个代码编写软件",
}


class Consumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat = ChatService()
        self.logger = logging.getLogger('myapp')
        self.process = None
        self.monitor_thread = None
        self.stop_monitor = threading.Event()

    def connect(self):
        self.accept()
        self.start_process_monitor()


    def disconnect(self, close_code):
        if self.process is not None:
            self.process.terminate()
        if self.monitor_thread is not None:
            self.stop_monitor.set()
            self.monitor_thread.join()

    def start_process_monitor(self):
        # 启动新线程来监控进程
        self.monitor_thread = threading.Thread(target=self.send_app_launch_notifications)
        self.monitor_thread.start()

    def send_app_launch_notifications(self):

        latest_recommendation = RecommendModel.objects.filter(recommend_type="app").order_by('-create_at').first()
        if not latest_recommendation:
            recommend_app_message = self.get_recommend_message()
            latest_recommendation = RecommendModel.objects.create(recommend_type="app",content=recommend_app_message)

        serialized_data = RecommendModelSerializer(latest_recommendation).data
        self.send(text_data=json.dumps(serialized_data))


        self.logger.info("monitor subprocess opened")
        self.process = subprocess.Popen(
            ["dbus-monitor", "interface='com.kylin.AppManager', member='LaunchApp'"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # 监控进程输出
        while not self.stop_monitor.is_set():
            line = self.process.stdout.readline()
            if line:
                line = line.strip()  # Assuming output is encoded in utf-8
                if "string" in line:
                    app_path = line.strip().split(' ')[1]
                    if self.handle_new_app_open(app_path):
                        recommend_app_message = self.get_recommend_message()
                        latest_recommendation = RecommendModel.objects.create(recommend_type="app",content=recommend_app_message)
                        serialized_data = RecommendModelSerializer(latest_recommendation).data
                        self.send(text_data=json.dumps(serialized_data))

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=text_data)

    def get_recommend_message(self):
        prompt = (
            f'请根据以下信息，结合app打开的时间，以及打开app的顺序，推荐2个我现在最可能打开的应用，给出我一个json格式的list，每个元素里面包含一个name和一个reason，name是app的名字，'
            f'reason是推荐的原因，推荐原因用一句话说明即可，不要有额外的内容。例如你应该输出类似于如下内容:[{{"name":"应用名称","reason":"打开原因"}}')


        prompt = prompt + self.get_app_log_and_desc()
        retry = 0
        while retry < 5:
            result = self.chat.chat_with_search_engine_and_knowledgebase([], prompt)
            results = result.split("```")
            result = results[-1]
            if len(result) < 10:
                result = results[-2]
            try:
                results = json.loads(result)
                idx = 0
                for result in results:
                    result['name'] = str(result['name']).lower()
                    result['id'] = idx
                    result['path'] = name_to_path[result['name']]
                    icon, exec_command = self.get_app_icon_and_exec_command(result['path'])
                    result['icon'] = icon
                    result['exec_command'] = exec_command
                    idx += 1
                modified_results = json.dumps(results, ensure_ascii=False, indent=2)
                return modified_results
            except Exception as err:
                self.logger.error(f"模型输出解析失败:{err}")

    def get_app_log_and_desc(self):
        app_log_message = "以下是我最近打开的APP以及时间："
        apps = AppOpenModel.objects.order_by("-create_at").all()[:20]  # 获取最近打开的20个应用
        app_name_set = set()
        for app in apps:
            # 格式化日期和时间
            formatted_date = app.create_at.strftime("%Y年%m月%d日%H时%M分%S秒")
            app_log_message += f"于{formatted_date}打开{app.name}\n"  # 每条记录后加换行符以便阅读
            app_name_set.add(app.name)

        app_desc_message = "。以下是部分APP的简介："
        for app_name in app_name_set:
            if app_name not in apps_desc:
                continue
            app_desc_message += f"{app_name}:{apps_desc[app_name]}"
        return app_log_message + app_desc_message

    def handle_new_app_open(self, app_path):
        app_path = app_path.replace("\"","")
        if app_path not in path_to_name:
            return False

        app_name = path_to_name[app_path]
        AppOpenModel.objects.create(name=app_name)
        return True

    def get_app_icon_and_exec_command(self, app_pah):
        with open(app_pah, mode='r') as f:
            contents = f.readlines()

            icon = None
            exec_command = None

            for line in contents:
                if line.startswith('Icon='):
                    icon = line.strip().split('=', 1)[1]
                elif line.startswith('Exec='):
                    exec_command = line.strip().split('=', 1)[1]

            return icon, exec_command
