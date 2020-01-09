# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 11:02:01 2019

@author: dell
"""
    
#D：电影推荐系统

#导入爬虫需要的库
import requests
from lxml import etree
import time
import csv
#import sys
import urllib.request
import pymysql
import numpy as np
 
#第一步：爬虫获取数据

#用Spyder函数来爬取电影的相关数据
#包括电影名，电影类型，上映年代，英文名、导演信息、电影评分、电影简介、电影图片链接

def spyder(start):
  #打开网页查看网页首页的URL
  url = 'http://www.imdb.cn/nowplaying/{}'.format(start)
  data = requests.get(url)
  
  html = etree.HTML(data.text)
  #headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
  #proxies = {'http':'http://10.10.10.10:8765','https':'https://10.10.10.10:8765'}
  
  #获取电影名
  try:
    res = html.xpath('//div[@class="honghe-4 clear"]/p[1]/i[1]/text()')
    #print(res)
    #建csvrow来存电影名信息
    csvrow=[]
    #将电影名写入csvrow
    for i in range(0,len(res)):
      if res[i]==0:
        pass
      else:
        #print(res[i])
        csvrow.append(res[i])
    # 休眠1秒
    time.sleep(1)
  except OSError:
    pass
    
  #获取电影类型
  try:
    res1 = html.xpath('//div[@class="honghe-4 clear"]/p[4]/i[1]/text()')
    #建csvrow1来存电影类型
    csvrow1=[]
    #将电影类型写入csvrow1
    for i in range(0,len(res1)):
      if res1[i]==0:
        pass
      else:
        #print(res1[i])
        csvrow1.append(res1[i])
    # 休眠1秒
    time.sleep(1)
  except OSError:
    pass
  
  #获取上映年代
  try:
    res2 = html.xpath('//div[@class="honghe-4 clear"]/p[4]/i[3]/text()')
    #建csvrow2来存上映年代
    csvrow2=[]
    #将上映年代写入csvrow2
    for i in range(0,len(res2)):
      if res2[i] not in res2:
        continue
      else:
        #print(res2[i])
        csvrow2.append(res2[i])
    # 休眠1秒
    time.sleep(1)
  except OSError:
    pass
    
  #获取英文名
  try:
    res3 = html.xpath('//div[@class="honghe-4 clear"]/p[2]/text()')
    #建csvrow3来存电影的英文名
    csvrow3=[]
    #将英文名写入csvrow3
    for i in range(0,len(res3)):
      if res3[i] not in res3:
        continue
      else:
        #print(res3[i])
        csvrow3.append(res3[i])
    # 休眠1秒
    time.sleep(1)
  except OSError:
    pass
  
  #获取导演信息
  try:
    res4 = html.xpath('//div[@class="honghe-4 clear"]/p[3]/span/text()')
    #建csvrow4来存电影的导演信息
    csvrow4=[]
    #将导演信息写入csvrow4
    for i in range(0,len(res4)):
      if res4[i] not in res4:
        continue
      else:
        #print(res4[i])
        csvrow4.append(res4[i])
    # 休眠1秒
    time.sleep(1)
  except OSError:
    pass
  
  #获取电影评分
  try:
    res5 = html.xpath('//div[@class="honghe-2"]/span/i/text()')
    #建csvrow5来存电影的评分
    csvrow5=[]
    #将电影评分写入csvrow5
    for i in range(0,len(res5)):
      if res5[i] not in res5:
        continue
      else:
        #print(res5[i])
        csvrow5.append(res5[i])
    # 休眠1秒
    time.sleep(1)
  except OSError:
    pass

  #获取电影简介
  try:
    res6 = html.xpath('//div[@class="honghe-5"]/text()')
    #建csvrow6来存电影的简介
    csvrow6=[]
    #将电影简介写入csvrow6
    for i in range(0,len(res6)):
      if res6[i] not in res6:
        continue
      else:
        #print(res6[i])
        csvrow6.append(res6[i])
    # 休眠1秒
    time.sleep(1)
  except OSError:
    pass

  #获取电影图片链接
  try:
    res7 = html.xpath('//div[@class="hong"]//img/@src')
    #建csvrow7来存电影的图片链接
    csvrow7=[]
    #将电影图片链接写入csvrow7
    for i in range(0,len(res7)):
      if res7[i] not in res7:
        continue
      else:
        #print(res7[i])
        csvrow7.append(res7[i])
    # 休眠1秒
    time.sleep(1)
  except OSError:
    pass
  
  #数据存储：将爬取到的数据存储到csv文件
  #csvfile = open('test.csv', 'w', newline='')#打开一个goods.csv的文件进行数据写入，没有则自动新建
  #writer = csv.writer(csvfile)
  #writer.writerow(['电影名', '类型', '年代', '英文名', '导演', '评分', '简介','图片链接']) #写入一行作为表头  
  #csvfile.close() #循环结束，数据爬取完成，关闭文件
 
 
  with open('data1.csv', 'a', encoding='utf-8',newline='') as f:
    writer=csv.writer(f)
    #writer.writerow(['电影名', '类型', '年代', '英文名', '导演', '评分', '简介','图片链接'])
    
    #利用writer.writerows向文件写入多行数据
    writer.writerows(zip(csvrow,csvrow1,csvrow2,csvrow3,csvrow4,csvrow5,csvrow6,csvrow7))
    
  #存入mysql数据库
  db = pymysql.connect("localhost","root","root","movie-message" )
  #设置游标
  cursor=db.cursor()
  #建表movie，其中，行名为name,type,year,enname,director,score,summary,picture，并设置类型
  cursor.execute('create table movie(name char(20),type char(100),year char(200),enname char(200),director char(100),score char(100),summary TEXT (65535),picture TEXT (65535))')
  #将一页数据循环插入movie表中
  for a1,a2,a3,a4,a5,a6,a7,a8 in zip(csvrow,csvrow1,csvrow2,csvrow3,csvrow4,csvrow5,csvrow6,csvrow7):
    sql="INSERT movie(name,type,year,enname,director,score,summary,picture) VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(a1,a2,a3,a4,a5,a6,a7,a8)
    cursor.execute(sql)
    #每次增加完均提交一次，确保每个数据存入数据库
    db.commit()

  
  #获取电影图片
def pictures(start):
    n=1
    url = 'http://www.imdb.cn/nowplaying/{}'.format(start)
    data = requests.get(url)
    html = etree.HTML(data.text)
    #将图片网址存入res8
    res8 = html.xpath('//div[@class="hong"]//img/@src')
    #循环遍历res8，并为每个图片命名区分
    for i in range(0,len(res8)):
      #print(res8[i])
      urllib.request.urlretrieve(res8[i],filename="D:/python代码/movie1/"+str(start)+'-'+str(n)+".jpg")
      n=n+1
      #for j in range(1,20):
        #print(str(n)+".jpg")
    
#第二步：数据预处理
#jupyter

if __name__ == '__main__':
  #设置想要爬取的页面
  for i in range(1):#14623
    #爬取'电影名', '类型', '年代', '英文名', '导演', '评分', '简介','图片链接'
    spyder(start=i+1)
    #爬取图片
    pictures(start=i+1)
    #防止封号，设置休眠
    time.sleep(1)
    #设置单个页面结束提示
    print("end!")
    print("单页内容数据库已存储")
  #设置整个爬虫结束提示
  print("数据爬取结束！")