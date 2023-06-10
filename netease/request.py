import logging
import os.path
import time

from plugins.plugin_music.netease.encrypt import *


def request(url, data, cookie):
    data_bts = json.dumps(data)
    body = weapi_encrypt(data_bts.encode("utf-8"))
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": get_user_agent(),
        "Referer": "https://music.163.com",
        "Cookie": merge_cookie(cookie),
    }
    # {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1', 'Referer': 'https://music.163.com', 'Cookie': 'os=pc;appver=2.9.7'}
    session = requests.session()
    resp = session.post(url, data=body.encode("utf-8"), headers=headers)

    print(resp.status_code)
    if resp.status_code != 200:
        return None, None, "http code {}".format(resp.status_code)

    return resp.json(), resp.cookies, 200


def request_eapi(url: str, data: dict, cookie: dict, option: dict):
    header = {
        "osver": cookie.get("osver", ""),
        "deviceId": cookie.get("deviceId", ""),
        "appver": "8.7.01",
        "versioncode": "140",
        "mobilename": cookie.get("mobilename", ""),
        "buildver": str(int(time.time())),
        "resolution": "1920x1080",
        "__csrf": cookie.get("__csrf", ""),
        "os": "android",
        "channel": cookie.get("channel", ""),
        "requestId": str(int(time.time() * 1000)) + "_0" + str(random.randint(0, 999)),
        "MUSIC_U": cookie.get("MUSIC_U", "")
    }
    data_bts = json.dumps(data)
    body = eapi_encrypt(option["url"], data_bts.encode("utf-8"))
    if option["realIP"] != "":
        header["X-Real-IP"] = option["realIP"]
        header["X-Forwarded-For"] = option["realIP"]
    user_agent = get_user_agent()
    header["Content-Type"] = "application/x-www-form-urlencoded"
    header["User-Agent"] = user_agent
    if url.find("music.163.com") >= 0:
        header["Referer"] = "https://music.163.com"
    header["Cookie"] = merge_cookie(cookie)

    session = requests.session()
    resp = session.post(url, data=body, headers=header)
    if resp.status_code != 200:
        return None, None, "http code {}".format(resp.status_code)

    return resp.json(), resp.cookies, 200


class NetEaseApi():
    def __init__(self, username: str, passwd_md5: str):
        logging.info("new net ease api, username:{}, passwd_md5: {}".format(username, passwd_md5))
        self.cookie = {}
        cd = self.login(username, passwd_md5)
        if len(cd) > 0:
            self.cookie = cd

    def login(self, username: str, passwd_md5: str, force=False):
        cookie_file = "./login_cookie.txt"
        cd = {}
        if os.path.exists(cookie_file):
            with open(cookie_file, "r") as f:
                cd = json.loads(f.read())
            if len(cd) > 0:
                if not force:
                    return cd
        url = "https://music.163.com/weapi/login/"
        # cookie = {"os": "pc", "appver": "2.9.7"}
        cookie = {}
        data = {
            "username": username,
            "password": passwd_md5,
            "rememberLogin": "true",
            "csrf_token": ""
        }
        resp, cookie, buss_code = request(url, data, cookie)
        if buss_code == 200:
            if resp["code"] == 200:
                logging.info("login success, resp:{}".format(resp))
                cd = cookie.get_dict()
                with open("../login_cookie.txt", "w") as f:
                    f.write(json.dumps(cd))
            else:
                logging.error("login error, resp:{}".format(resp))

        return cd

    def search(self, s: str):
        data = {
            "s": s,
            "type": 1,
            "limit": 20,
            "offset": 0,
        }
        url = "https://music.163.com/weapi/cloudsearch/get/web"
        resp, cookie, buss_code = request(url, data, self.cookie)
        if buss_code == 200:
            if resp["code"] == 200:
                return resp
            else:
                logging.error("search song buss code:{}, resp:{}".format(resp["code"], resp))
        else:
            logging.error("search song http code:{}".format(buss_code))

    def song_url(self, ids):
        url = "https://interface3.music.163.com/eapi/song/enhance/player/url"
        data = {
            "ids": ids,
            "br": 999000,
        }
        opt = {
            "url": "/api/song/enhance/player/url",
            "realIP": "27.46.131.60",
        }
        resp, cookie, tips = request_eapi(url, data, self.cookie, opt)
        return resp


if __name__ == "__main__":
    # test login
    api = NetEaseApi("xx@163.com", "684a9721bf6f939855803a")
    # resp = api.search("可惜我是水瓶座")
    # print("resp ==> {}".format(resp))
    resp = api.song_url(["1984475097"])
    print("resp ==> {}".format(resp))
