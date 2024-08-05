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
from django.utils import timezone
from .serializers import RecommendModelSerializer

desktop_to_name = {
    "qq.desktop": "qq",
    "code.desktop": "vscode",
    "bytedance-feishu.desktop": "飞书",
    "wechat.desktop":"微信",
    "ukui-notebook.desktop":"便利贴",
    "google-chrome.desktop":"谷歌浏览器"
}
name_to_path = {
    "qq": "/usr/share/applications/qq.desktop",
    "vscode": "/usr/share/applications/code.desktop",
    "飞书": "/usr/share/applications/bytedance-feishu.desktop",
    "便利贴":"/usr/share/applications/ukui-notebook.desktop",
    "微信":"/usr/share/applications/wechat.desktop",
    "谷歌浏览器":"/usr/share/applications/google-chrome.desktop"
}
apps_desc = {
    "qq": "一个流行的即时通讯和社交软件，由腾讯开发，支持文本聊天、语音通话、视频通话、文件传输等功能，广泛应用于个人社交和工作沟通。",
    "飞书": "一个集成即时通讯、文档协作、日历管理和视频会议等功能的工作办公软件，由字节跳动开发，旨在提升团队协作效率和信息共享。",
    "vscode": "一个由微软开发的轻量级且功能强大的代码编写软件，支持多种编程语言和扩展插件，广泛应用于软件开发和调试。",
    "微信": "一个由腾讯开发的多功能社交软件，提供即时通讯、朋友圈、公众号、支付等多种功能，是中国最受欢迎的社交平台之一。",
    "谷歌": "全球最大的搜索引擎公司，提供包括搜索引擎、电子邮件、地图、浏览器和操作系统等多种互联网服务和产品，致力于组织全球信息并使其可供用户访问和使用。",
    "便利贴": "一种用于快速记录和管理笔记的小工具，通常以虚拟或实体纸片形式出现，帮助用户方便地记录待办事项、提醒和重要信息。"
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
            f'reason是推荐的原因，推荐原因用一句话说明即可，不要有额外的内容，在可能的情况下请尽量强调与刚刚打开的APP的联系。例如你应该输出类似于如下内容:[{{"name":"应用名称","reason":"打开原因"}}')


        prompt = prompt + self.get_app_log_and_desc()
        retry = 0
        while retry < 5:
            result = self.chat.chat([], prompt)
            results = result.split("```")
            result = results[-1]
            print(results)
            if len(result) < 10:
                result = results[-2]
            try:
                result = result.replace("json","")
                result = result.lstrip("\n")
                results = json.loads(result)
                idx = 0
                for result in results:
                    result['name'] = str(result['name']).lower()
                    result['id'] = idx

                    icon, exec_command = self.get_app_icon_and_exec_command(name_to_path[result['name']])
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
            local_time = timezone.localtime(app.create_at)
            formatted_date = local_time.strftime("%Y年%m月%d日%H时%M分%S秒")
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
        app_desktop = app_path.split("/")[-1]
        if app_desktop not in desktop_to_name:
            return False

        app_name = desktop_to_name[app_desktop]
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
