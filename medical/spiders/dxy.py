# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from medical.items import MedicalItem


class DxySpider(scrapy.Spider):
    name = 'dxy'
    # allowed_domains = ['drugs.dxy.cn']
    # start_urls = ['http://drugs.dxy.cn/']

    # def __init__(self):
    #     self.broswer = webdriver.Chrome(
    #         executable_path='/usr/local/bin/chromedriver')

    def start_requests(self):
        """[summary]
        该方法必须返回一个可迭代对象(iterable)。该对象包含了spider用于爬取的第一个Request。
        """
        url = "http://drugs.dxy.cn/"
        yield scrapy.Request(url,
                             headers=self.settings.get(
                                 "DEFAULT_REQUEST_HEADERS"),
                             dont_filter=True,
                             callback=self.parse,
                             )

    def parse(self, response):
        '''
        皮肤科药物当前分类页面的分页分发（非内容处理），取到各分页的url，封装成request对象，分发到download。
        '''
        # print('-----------parse')
        css_li = response.css(
            '#cate_1386 > ul > li')
        cate_list = []
        for i in css_li:
            key = i.css('h3 > a::text').extract_first()
            value = 'http://' + i.css(
                'h3 > a::attr(href)').re(
                '(?:drugs.dxy.cn/category/)[0-9]+(?:.htm)')[0]
            tmp = {}
            tmp[key] = value
            yield scrapy.Request(
                url=value, callback=self.parse_pagination, meta={'cate': key})
            cate_list.append(tmp)
            break
        # print(ret_list)
        # print('-----------')

    def parse_pagination(self, response):
        '''
        皮肤科药物当前分类页面的分页分发（非内容处理），取到各分页的url，封装成request对象，分发到download。
        '''
        # print('-----------parse_pagination')
        num_list = response.css(
            '#container > div.pagination').re(
            '(?!<a href="?page=)([0-9]+)(?:" title="最后一页">)')
        # print(num_list, type(num_list))
        cate_page = {
            'url': response.url,
            'num': num_list[0] if num_list else '1'
        }
        # print(cate_page)

        for i in range(1, int(cate_page['num']) + 1):
            url = response.url + '?page=' + str(i)
            # print(url)
            yield scrapy.Request(
                url=url, callback=self.parse_drug, meta={
                    'cate': response.meta.get('cate')
                })
            break

    def parse_drug(self, response):
        '''
        皮肤科药物分类页面的 当前分页的 drug页面分发（非内容处理），取到各drug页面的url，封装成request对象，分发到download。
        '''
        # print('-----------parse_drug')
        drug = {}
        drug['cate'] = response.meta.get('cate')
        a_list = response.css(
            '#container > div.common_bd.clearfix > div > div > div > ul > li > div.fl > h3 > a')
        for i in a_list:
            # title = i.css('::text').extract_first()
            info = i.css('::text').re(
                '(.*)(?:\t\t\t\t\t\t\t\t\t\t\t - )(.*)(?:\t\t\t\t\t\t\t\t\t\t)')

            url = 'http:' + i.css('::attr(href)').extract_first()
            drug['title'] = info[0]
            drug['producer'] = info[1]

            print(drug, url)
            yield scrapy.Request(url=url, callback=self.get_content, meta={'drug': drug})
            # break

    def get_content(self, response):
        print('-----------get_content')
        # page = response.css(
        #     '#container > div.common_bd.clearfix > div.common_mainwrap.fl > div > div > dl')
        drug = response.meta.get('drug')
        drug['ingredient'] = response.css(
            '#container > div.common_bd.clearfix > div.common_mainwrap.fl > div > div > dl > dd:nth-child(4)::text').extract_first().strip()

        drug = MedicalItem(drug)
        print(drug, type(drug))
        yield drug
