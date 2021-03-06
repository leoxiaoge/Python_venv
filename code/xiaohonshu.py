from gevent import monkey
# 猴子补丁
monkey.patch_all()
from gevent.pool import Pool
from queue import Queue
import requests
import json
from lxml import etree


class RedBookSpider():
    """小红书爬虫"""

    def __init__(self, pages):
        """初始化"""
        self.url = 'https://www.xiaohongshu.com/web_api/sns/v2/trending/page/brand?page={}&page_size=20'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36"
        }
        self.url_queue = Queue()
        self.pool = Pool(5)
        self.pages = pages
        pass

    def get_url(self):
        """获取url"""
        for page in range(1, self.pages):
            url = self.url.format(page)
            self.url_queue.put(url)

    def save_data(self, items):
        """数据保存"""
        with open('./redbook.txt', 'a', encoding='utf-8') as f:
            f.write(str(items) + '\n')

    def deal_detail(self, detail_url, items, data):
        """详情页内容提取"""

        resp = requests.get(url=detail_url, headers=self.headers)
        eroot = etree.HTML(resp.text)
        items['fans'] = eroot.xpath('//div[@data-v-64bff0ce]/div[@class="extra"]/text()')
        items['articles'] = eroot.xpath('//div/span[@class="stats"]/text()')
        items['introduce'] = eroot.xpath('//div[@class="desc"]/div[@class="content"]/text()')
        items['detail_url'] = detail_url
        items['image'] = data['page_info']['banner']
        print(items)
        self.save_data(items)

    def deal_response(self, resp):
        """数据提取"""
        dict_data = json.loads(resp.text)
        dict_data = dict_data['data']
        for data in dict_data:
            items = {}
            items['name'] = data['page_info']['name']
            detail_url = 'https://www.xiaohongshu.com/page/brands/' + data['page_id']
            self.deal_detail(detail_url, items, data)

    def execute_task(self):
        """处理响应"""

        url = self.url_queue.get()
        resp = requests.get(url=url, headers=self.headers)
        # print(resp.text)
        self.deal_response(resp)
        self.url_queue.task_done()

    def execute_task_finished(self, result):
        """任务回调"""

        self.pool.apply_async(self.execute_task, callback=self.execute_task_finished)

    def run(self):
        """启动程序"""

        self.get_url()
        for i in range(3):
            self.pool.apply_async(self.execute_task, callback=self.execute_task_finished)
        self.url_queue.join()

        pass


if __name__ == '__main__':
    user = RedBookSpider(4)
    # 需要爬取几页数据  就改为多少
    user.run()
