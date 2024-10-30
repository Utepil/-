# coding=utf-8
from Crypto.Cipher import AES
import base64
import requests
import json

headers = {
    'Cookie': 'appver=1.5.0.75771;',
    'Referer': 'https://music.163.com/weapi/comment/resource/comments/get?csrf_token=d5b7e365dd0cdf7315a9688eb41096f7'
}

second_param = "010001"
third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
forth_param = "0CoJUm6Qyw8W8jud"


def get_params(offset):
    iv = "0102030405060708"
    first_param = json.dumps({
        "rid": "",
        "offset": str(offset),
        "total": "true" if offset == 0 else "false",
        "limit": "20",
        "csrf_token": ""
    })
    first_key = forth_param
    second_key = 16 * 'F'
    h_encText = AES_encrypt(first_param.encode('utf-8'), first_key.encode('utf-8'), iv.encode('utf-8'))
    h_encText = AES_encrypt(h_encText, second_key.encode('utf-8'), iv.encode('utf-8'))
    return h_encText


def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    return encSecKey


def AES_encrypt(text, key, iv):
    # PKCS7 padding
    pad = 16 - len(text) % 16
    text += bytes([pad] * pad)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_bytes = cipher.encrypt(text)
    encrypted_text = base64.b64encode(encrypted_bytes)
    return encrypted_text


def get_json(url, params, encSecKey):
    data = {
        "params": params.decode('utf-8'),
        "encSecKey": encSecKey
    }
    response = requests.post(url, headers=headers, data=data)
    return response.content


if __name__ == "__main__":
    url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_30953009/?csrf_token="
    all_comments = []
    offset = 0
    while True:
        params = get_params(offset)
        encSecKey = get_encSecKey()
        json_text = get_json(url, params, encSecKey)
        json_dict = json.loads(json_text)

        comments = json_dict.get('comments', [])
        if not comments:
            break  # No more comments to fetch

        all_comments.extend(comments)
        offset += 20  # Move to the next page

    print("Total comments fetched:", len(all_comments))
    for item in all_comments:
        print(item['content'])
