import plugins
from plugins import *
from common.log import logger
from bridge.bridge import Bridge
from bridge.context import ContextType
import re
import requests
from bridge.reply import Reply, ReplyType


@plugins.register(
    name="Music",
    desire_priority=0,
    hidden=True,
    desc="基于网易云搜索音乐的插件",
    version="0.1",
    author="nautilis",
)
class Music(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Music] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [ContextType.TEXT]:
            return
        query = e_context["context"].content
        logger.info("content => " + query)
        reply = Reply()
        reply.type = ReplyType.TEXT
        if query.startswith(f'music '):
            query_list = query.split(" ", 1)
            query = query_list[1]
            if query.startswith(f'点歌：') or query.startswith(f'点歌:'):
                msg = query.replace("点歌:", "")
                msg = query.replace("点歌：", "")
                msg = msg.strip()
                url, name, ar = self.search_song(msg)
                if url != "":
                    reply.content = "{} - {} \n点击下面的🔗即可播放:\n{}".format(name, ar, url)
                else:
                    reply.content = "找不到歌曲😮‍💨"
                logger.info("点歌 reply --> {}, url:{}".format(reply, url))
            else:
                chat = Bridge().get_bot("chat")
                all_sessions = chat.sessions
                msgs = all_sessions.session_query(query, e_context["context"]["session_id"]).messages

                reply = chat.reply("以歌名 - 歌手的格式回复", e_context["context"])
                logger.info("music receive => query:{}, messages:{}, reply:{}".format(query, msgs, reply))
                logger.info("")
                url, name, ar = self.search_song(reply.content)
                if url == "":
                    reply.content = reply.content + "\n----------\n找不到相关歌曲😮‍💨"
                else:
                    reply.content = reply.content + "\n----------\n" + "{} - {} \n点击下面的🔗即可播放:\n{}".format(name,
                                                                                                                   ar,
                                                                                                                   url)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

            return

            # dir = "/Users/nautilis/myspace/project/ai/chatgpt-on-wechat/plugins/music/test.xlsx"
            # reply = Reply(ReplyType.FILE, dir)
            # e_context["reply"] = reply
            # e_context.action = EventAction.BREAK_PASS

    def get_help_text(self, verbose=False, **kwargs):
        help_text = "推荐音乐\n"
        help_text += "music 推荐:一首粤语经典歌曲"
        help_text += "点歌\n"
        help_text += "music 点歌: 可惜我是水瓶座-杨千嬅"
        return help_text

    def search_song(self, song_info):
        regex = r"\W?(?P<so>\w+)\W?\s?-\s?(?P<ar>\w+)"
        res = re.search(regex, song_info)
        if res:
            song = res.group("so")
            ar = res.group("ar")
            print(song)
            print(ar)
            resp = requests.get(url="http://127.0.0.1:3000/cloudsearch?type=1&keywords={}".format(song))
            if resp.status_code == 200:
                resp = resp.json()
                if resp["code"] == 200:
                    result = resp["result"]
                    if result:
                        songs = result["songs"]
                        songid, name, ar = pick_song(songs, song, ar)
                        if songid > 0:
                            url = query_song_url(songid)
                            return url, name, ar
                        else:
                            logger.info("song not found")
                else:
                    logger.info("search buss code not 200, code:{}".format(resp["code"]))
            else:
                logger.info("search http code not 200, code:{}".format(resp.status_code))
        else:
            logger.info("regex not match song and ar")
        return "", "", ""


def pick_song(songs, req_name, req_ar):
    sid, name, ar = pick_song_with_accuracy(songs, req_name, req_ar, "all")
    if sid < 0:
        sid, name, ar = pick_song_with_accuracy(songs, req_name, req_ar, "only_name")
    return sid, name, ar


def pick_song_with_accuracy(songs, req_name, req_ar, accuracy):
    for song in songs:
        name = song["name"]
        ars = song["ar"]
        id = song["id"]
        ar = ""
        if len(ars) > 0:
            ar = ars[0]["name"]
        if accuracy == "all":
            if contain(req_name, name) and contain(req_ar, ar):
                return id, name, ar
        elif accuracy == "only_name":
            if contain(req_name, name):
                return id, name, ar
    return -1, "", ""


def query_song_url(id):
    urlResp = requests.get(url="http://127.0.0.1:3000/song/url?id={}".format(id))
    if urlResp.status_code == 200:
        urlRes = urlResp.json()
        if urlRes["code"] == 200:
            data = urlRes["data"]
            if len(data) > 0:
                url = data[0]["url"]
                print("url => {}".format(url))
                return url
            else:
                logger.info("query url data length is zero")
        else:
            logger.info("query url buss code not 200, code:{}".format(urlRes["code"]))
    else:
        logger.info("query url http code not 200, code:{}".format(urlResp.status_code))
    return ""


def contain(a, b):
    if len(a) > len(b):
        return a.find(b) >= 0
    else:
        return b.find(a) >= 0
