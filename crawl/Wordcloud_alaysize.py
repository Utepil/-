import json
import requests
from Crypto.Cipher import AES
import base64
import re
from collections import Counter
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 请求头信息
headers = {
    'Cookie': 'appver=1.5.0.75771;',
    'Referer': 'https://music.163.com/weapi/comment/resource/comments/get?csrf_token=d5b7e365dd0cdf7315a9688eb41096f7'
}


# 加密函数
def get_params(offset, comment_type="normal"):
    if comment_type == "hot":
        first_param = f"{{rid:\"\", offset:\"{offset}\", total:\"false\", limit:\"20\", csrf_token:\"\"}}"
    else:
        first_param = f"{{rid:\"\", offset:\"{offset}\", total:\"true\", limit:\"20\", csrf_token:\"\"}}"
    second_param = "010001"
    third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    forth_param = "0CoJUm6Qyw8W8jud"

    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    encText = AES_encrypt(first_param.encode(), first_key, iv)
    encText = AES_encrypt(encText, second_key, iv)
    return encText


def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    return encSecKey


def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad).encode('utf-8')
    encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text


def get_json(url, params, encSecKey):
    data = {
        "params": params.decode('utf-8'),
        "encSecKey": encSecKey
    }
    response = requests.post(url, headers=headers, data=data)
    return response.content


# 爬取评论并保存到JSON文件
def fetch_comments(song_id, max_comments=1000, comment_type="normal"):
    url = f"http://music.163.com/weapi/v1/resource/comments/R_SO_4_{song_id}/?csrf_token="

    all_comments = []
    offset = 0
    limit = 20

    while len(all_comments) < max_comments:
        params = get_params(offset, comment_type)
        encSecKey = get_encSecKey()
        json_text = get_json(url, params, encSecKey)
        json_dict = json.loads(json_text)

        comments = json_dict.get('hotComments' if comment_type == "hot" else 'comments', [])
        if not comments:
            break

        all_comments.extend(comments)
        offset += limit

    # 保存到JSON文件
    with open('comments.json', 'w', encoding='utf-8') as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=4)

    print(f"Total comments fetched: {len(all_comments)}")


# 数据清洗与词频分析
def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # 移除标点符号
    text = re.sub(r'\d+', '', text)  # 移除数字
    return text


def analyze_comments():
    with open('comments.json', 'r', encoding='utf-8') as f:
        all_comments = json.load(f)

    comments = [comment['content'] for comment in all_comments]

    cleaned_comments = [clean_text(comment) for comment in comments]

    words = []
    for comment in cleaned_comments:
        words.extend(jieba.lcut(comment))

    word_counts = Counter(words)

    stopwords = set(jieba.cut('我 你 他 她 它 我们 你们 他们 她们 它们 这 那 是 在 和 的 了 不 很 都 没 有 也 就'))

    filtered_word_counts = {word: count for word, count in word_counts.items() if
                            word not in stopwords and len(word) > 1}

    # 生成词云
    wordcloud = WordCloud(
        font_path='simhei.ttf',
        width=800,
        height=400,
        background_color='white',
        max_words=200
    ).generate_from_frequencies(filtered_word_counts)

    # 显示词云
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()


# 主程序
if __name__ == "__main__":
    song_id = "2161155720"  # 替换为你想要爬取评论的歌曲ID
    fetch_comments(song_id, max_comments=500, comment_type="new")
    analyze_comments()
