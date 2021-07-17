import requests
import csv
import time
import json


def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Referer": "https://weibo.com"
    }
    cookies = {
        "cookie": "你的cookie"
    }
    response = requests.get(url, headers=headers, cookies=cookies)
    time.sleep(3)   # 加上3s 的延时防止被反爬
    return response.text


def save_data(data):
    title = ['text_raw', 'created_at', 'attitudes_count', 'comments_count', 'reposts_count']
    with open("data.csv", "a", encoding="utf-8", newline="")as fi:
        fi = csv.writer(fi)
        fi.writerow([data[i] for i in title])


if __name__ == '__main__':

    uid = 1669879400
    url = 'https://weibo.com/ajax/statuses/mymblog?uid={}&page={}&feature=0'
    # url = 'https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value=2101822767&containerid=1005052101822767'
    page = 1
    while 1:
        print(page)
        url = url.format(uid, page)
        print(url)
        html = get_html(url)
        responses = json.loads(html)
        blogs = responses['data']['list']
        if len(blogs) == 0:
            break
        data = {}   # 新建个字典用来存数据
        for blog in blogs:
            data['attitudes_count'] = blog['attitudes_count']   # 点赞数量
            data['comments_count'] = blog['comments_count']     # 评论数量(超过100万的只会显示100万)
            data['created_at'] = blog['created_at']     # 发布时间
            data['reposts_count'] = blog['reposts_count']     # 转发数量(超过100万的只会显示100万)
            data['text_raw'] = blog['text_raw']     # 博文正文文字数据
            print(data)
            save_data(data)
        page += 1
