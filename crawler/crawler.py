# -*- coding: utf-8 -*-
import os
import sys
import urllib
import urllib2
import base64
import json
import re
import time
import sqlite3
import time
import datetime

#import pymongo
from lxml import etree
from bson import json_util

from py_util.compress import ungzip
from py_util.secure import gen_md5

retr_text = lambda nodes, pipe='': pipe.join([''.join(i.itertext()) for i in nodes])
retr_one = lambda nodes: nodes.text if len(nodes)==0 else nodes[0].text

amazon_url = 'http://www.amazon.co.jp'
base_url = 'http://www.amazon.co.jp/gp/product/4778314220/'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'ja,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,en-US;q=0.2',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'www.amazon.co.jp',
    'Pragma': 'no-cache',
}

namespace = {
    #u'単行本（ソフトカバー）': 1,
    u'出版社': 'publisher',
    u'言語': 'language',
    u'ISBN-10': 'ISBN_10',
    u'ISBN-13': 'ISBN_13',
    u'発売日': 'publish_date_string',
    #u'Amazon ベストセラー商品ランキング': 1,
    u'商品パッケージの寸法': 'package_type',
    #u'おすすめ度': 1,
    u'単行本': 'book_sale_type',
    u'コミック': 'comic',
}


books_urls = {
    'comic_and_navel': 'http://www.amazon.co.jp/%E6%BC%AB%E7%94%BB%EF%BC%88%E3%83%9E%E3%83%B3%E3%82%AC%EF%BC%89%EF%BC%8D%E3%82%B3%E3%83%9F%E3%83%83%E3%82%AF%EF%BC%8DBL%EF%BC%88%E3%83%9C%E3%83%BC%E3%82%A4%E3%82%BA%E3%83%A9%E3%83%96%EF%BC%89-%E6%9C%AC/b/ref=sv_b_4?ie=UTF8&node=466280',
}
done_dict = {}

pat_find_id = re.compile(r'.*\/dp\/([\w]{10})\/.*')
pat_find_domain = re.compile(r'http:\/\/www\.amazon\.co\.jp\/.*')
pat_find_author_type = re.compile(ur'\(著\).*')

## format : 2014/02 
pat_date_format1 = re.compile(r'^[\d]{4}\/[\d]{2}$')
## format : 2014/02/21
pat_date_format2 = re.compile(r'^[\d]{4}\/[\d]{2}\/[\d]{2}$')




def load_prev_done_list():
    done_list = []

    with open('output/done_lists.txt', 'w+') as f:
        done_list = f.read().split('\n')

    global done_dict
    for i in done_list:
        done_dict[i] = 1


def is_done(url_string):
    k = gen_md5(url_string)

    if k in done_dict:
        return True
    else:
        return False


def add_into_done_dict(key_string):
    k = gen_md5(key_string)

    global done_dict
    done_dict[k] = 1

    with open('output/done_lists.txt', 'a+') as f:
        f.write(k + '\n')


"""
    @return:
        dict
"""
def parse_html(data):
    tree = etree.HTML(data)

    ## a new docs
    all_attrs = {}


    ## product title
    title_element = tree.xpath('//*/span[@id="productTitle"]')
    if len(title_element) == 1:
        all_attrs['product_name'] = retr_text(title_element)
    else:
        all_attrs['product_name'] = ''


    all_attrs['author'] = []

    authors_elem = tree.xpath('//*/a[@class="a-link-normal contributorNameID"]')
    powerby_elem = tree.xpath('//*[@id="byline"]/span/span/span')
    for author, tps in zip(authors_elem, powerby_elem):
        author_name = retr_one(author)
        author_type = retr_one(tps)
        #print author_name, author_type

        if pat_find_author_type.match(author_type):
            all_attrs['author'].append(author_name)
            #print 'author =>', author_name


    ## parse attrs. (ex: ISBN-10 ...)
    content = tree.xpath('//*[@id="detail_bullets_id"]/table/tr/td/div/ul/li')
    for a in content:
        content_str = retr_text([a])
        c = (content_str.strip().split(u' ', 1) + [''])[0:2]

        cat_title = c[0].replace(u':', '').replace(u'：', '').strip()
        cat_content = c[1].strip()
        #print '>', cat_title

        if cat_title in namespace:
            #print cat_content
            all_attrs[namespace[cat_title]] = cat_content


    if 'ISBN_10' not in all_attrs or 'ISBN_13' not in all_attrs:
        print '** NO ISBN **'
        return {}


    if 'publish_date_string' in all_attrs:
        parse_format = '%Y/%m/%d'

        if pat_date_format1.match(all_attrs['publish_date_string']):
            parse_format = '%Y/%m'

        elif pat_date_format2.match(all_attrs['publish_date_string']):
            parse_format = '%Y/%m/%d'
    
        pd_date = datetime.datetime.strptime(all_attrs['publish_date_string'], parse_format)
        all_attrs['publish_date'] = pd_date


    all_attrs['createdAt'] = datetime.datetime.now()
    all_attrs['updatedAt'] = datetime.datetime.now()


    if 'package_type' in all_attrs:
        sizes = all_attrs['package_type'].split(' ')
        if len(sizes) >= 1:
            all_attrs['package_size_x'] = float(sizes[0].strip())

        if len(sizes) >= 3:
            all_attrs['package_size_y'] = float(sizes[2].strip())

        if len(sizes) >= 5:
            all_attrs['package_size_z'] = float(sizes[4].strip())


    ## save info into json
    with open('output/docs.json', 'a+') as f:
        doc_str = json_util.dumps(all_attrs)
        f.write(doc_str + '\n')

    for k in all_attrs:
        print repr(k), repr(all_attrs[k])


    ## find other links in html
    other_url = {}
    all_href = tree.xpath('//*/a')

    for i in all_href:
        if 'href' in i.attrib:
            m = pat_find_id.match(i.attrib['href'])
            n = pat_find_domain.match(i.attrib['href'])
            if m:
                md5_k = m.group(1).strip()

                if is_done(md5_k):
                    pass
                else:
                    if n:
                        other_url[m.group(1).strip()] = i.attrib['href']
                    else:
                        other_url[m.group(1).strip()] = amazon_url + i.attrib['href']

    return other_url


def q(url):
    req = urllib2.Request(url, None, headers)
    resp = urllib2.urlopen(req)
    data = ungzip(resp)

    return data


"""
    python xxx.py local
"""
if __name__=="__main__":
    ## load prev done list
    load_prev_done_list()

    ## set init
    queues = {
        #'4778314220' : 'http://www.amazon.co.jp/gp/product/4778314220/',
        #'4569816533': 'http://www.amazon.co.jp/%E4%BB%96%E4%BA%BA%E3%82%92%E6%94%BB%E6%92%83%E3%81%9B%E3%81%9A%E3%81%AB%E3%81%AF%E3%81%84%E3%82%89%E3%82%8C%E3%81%AA%E3%81%84%E4%BA%BA-PHP%E6%96%B0%E6%9B%B8-%E7%89%87%E7%94%B0%E7%8F%A0%E7%BE%8E/dp/4569816533/ref=sr_1_2?s=books&ie=UTF8&qid=1412217086&sr=1-2',
        #'4801800491': 'http://www.amazon.co.jp/%E8%AA%85%E9%9F%93%E8%AB%96-%E6%99%8B%E9%81%8A%E8%88%8E%E6%96%B0%E6%9B%B8-S18-%E6%97%A5%E6%9C%AC%E6%88%A6%E7%95%A5%E3%83%96%E3%83%AC%E3%82%A4%E3%83%B3/dp/4801800491/ref=pd_ts_zgc_b_2189049051_6?ie=UTF8&s=books&pf_rd_p=146890049&pf_rd_s=right-7&pf_rd_t=101&pf_rd_i=466300&pf_rd_m=AN1VRQENFRJN5&pf_rd_r=0RTS0DYC98CV5Q78A1B2',
        '0299200744': 'http://www.amazon.co.jp/Brown-Morning-Franck-Pavloff/dp/0299200744/ref=pd_cp_fb_3/375-1379840-0045505',
        '4883928179': 'http://www.amazon.co.jp/%E3%83%8A%E3%83%81%E3%82%B9%E3%81%AE%E7%99%BA%E6%98%8E-%E6%AD%A6%E7%94%B0-%E7%9F%A5%E5%BC%98/dp/4883928179/ref=pd_cp_b_2/377-4319162-0447121',
        '4286070409': 'http://www.amazon.co.jp/%E6%88%90%E5%8A%9F%E3%81%99%E3%82%8B%E7%94%B7%E3%81%AF%E3%81%BF%E3%81%AA%E3%80%81%E3%80%8C%E5%A5%B3%E5%AD%90%E5%8A%9B%E3%80%8D%E3%82%92%E4%BD%BF%E3%81%86-%E5%A5%B3%E6%80%A7%E7%A4%BE%E5%93%A1%E3%81%AB%E5%A5%BD%E3%81%8B%E3%82%8C%E3%82%8B24%E3%81%AE%E6%B3%95%E5%89%87-%E8%A7%92%E5%B7%9D-%E3%81%84%E3%81%A4%E3%81%8B/dp/4286070409/ref=pd_sim_b_3/375-1325899-1437424?ie=UTF8&refRID=0FD430XDCJAN16NH6HBM',
    }

    while len(queues) > 0:
        time.sleep(5)

        key, value = queues.popitem()
        print key, value

        if is_done(key):
            print 'is done...'

        else:
            add_into_done_dict(key)
            data = q(value)
            queues.update(parse_html(data))

        print 'Here has queues =>', len(queues)
        print '-' * 20



