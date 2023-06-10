import hashlib
import json
import random
from base64 import b64encode

import requests
from Crypto.Cipher import AES
from binascii import hexlify
from Crypto.PublicKey import RSA
from base64 import b64decode
from os import urandom
import urllib.parse

uas = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
    "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89;GameHelper",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1",
    "Mozilla/5.0 (iPad; CPU OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/13.10586",
]


def aes(text, key, method={}):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    if "iv" in method:
        encryptor = AES.new(key, AES.MODE_CBC, b"0102030405060708")
    else:
        encryptor = AES.new(key, AES.MODE_ECB)
    ciphertext = encryptor.encrypt(text)
    if "base64" in method:
        return b64encode(ciphertext)
    return hexlify(ciphertext).upper()


def rsa(text):
    keyDER = b64decode(
        "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDgtQn2JZ34ZC28NWYpAUd98iZ37BUrX/aKzmFbt7clFSs6sXqHauqKWqdtLkF2KexO40H1YTX8z2lSgBBOAxLsvaklV8k4cBFK9snQXE9/DDaFt6Rr7iVZMldczhC0JNgTz+SHXT6CBHuX3e9SdB1Ua44oncaTWz7OBGLbCiK45wIDAQAB")
    keyPub = RSA.importKey(keyDER)
    # print(keyPub.n)
    # print(keyPub.e)

    # text = text[::-1]
    rs = pow(int(hexlify(text), 16),
             keyPub.e, keyPub.n)
    return format(rs, "x").zfill(256)


def create_key(size):
    return hexlify(urandom(size))[:16]


def weapi_encrypt(jsonbyte: bytes):
    preset_key = b'0CoJUm6Qyw8W8jud'
    secret = create_key(16)
    method = {"iv": True, "base64": True}
    params = aes(aes(jsonbyte, preset_key, method), secret, method)
    encseckey = rsa(secret[::-1])
    return "params={}&encSecKey={}".format(urllib.parse.quote(params, safe=" "),
                                           urllib.parse.quote(encseckey, safe=" "))
    # return {"params": params, "encSecKey": encseckey}


def eapi_encrypt(url: str, json_byte: bytes):
    message = "nobody{}use{}md5forencrypt".format(url, json_byte.decode("utf-8"))
    digest = hexlify(hashlib.md5(message.encode("utf-8")).digest()).decode("utf-8")
    data = "{}-36cd479b6b5-{}-36cd479b6b5-{}".format(url, json_byte.decode("utf-8"), digest)
    encrypt = aes(data.encode("utf-8"), b'e82ckenh8dichen8', {})
    return "params={}".format(encrypt.upper().decode("utf-8"))


def merge_cookie(cookies):
    cookie_list = []
    for k, v in cookies.items():
        cookie_list.append("{}={}".format(k, v))
    return ";".join(cookie_list)


def get_user_agent():
    return random.choice(uas)


if __name__ == "__main__":
    res = aes('hello你好'.encode("utf-8"), b'0CoJUm6Qyw8W8jud', {"iv": b"0102030405060708", "base64": ""})
    print(res)
    res = aes('hello你好'.encode("utf-8"), b'0CoJUm6Qyw8W8jud', {})
    print(res)
    # res = rsa("hello你好".encode("utf-8"), pubkey=PUBKEY, modulus=n)
    # print(res)
    # print(hexlify(b64decode("MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDgtQn2JZ34ZC28NWYpAUd98iZ37BUrX/aKzmFbt7clFSs6sXqHauqKWqdtLkF2KexO40H1YTX8z2lSgBBOAxLsvaklV8k4cBFK9snQXE9/DDaFt6Rr7iVZMldczhC0JNgTz+SHXT6CBHuX3e9SdB1Ua44oncaTWz7OBGLbCiK45wIDAQAB`")))
    # print(USE_RSA("hello你好"))
    print(rsa("hello你好".encode("utf-8")))

    json_bts = '''{"username":"bevanpf@163.com","password":"a6979486d8684a9721bf6f939855803a","rememberLogin":"true","csrf_token":""}`'''
    print(weapi_encrypt(json_bts.encode("utf-8")))

    print(eapi_encrypt("/api/song/enhance/player/url",
                       '''{"ids":"[33894312]","br":999000,"header":{"appver":"8.7.01","versioncode":"140","buildver":"1668842016","resolution":"1920x1080","__csrf":"","os":"pc","requestId":"1668842016582_0788","MUSIC_A":"bf8bfeabb1aa84f9c8c3906c04a04fb864322804c83f5d607e91a04eae463c9436bd1a17ec353cf780b396507a3f7464e8a60f4bbc019437993166e004087dd32d1490298caf655c2353e58daa0bc13cc7d5c198250968580b12c1b8817e3f5c807e650dd04abd3fb8130b7ae43fcc5b"}}'''.encode(
                           "utf-8")))
