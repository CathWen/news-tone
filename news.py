import re
import os
import requests
from openpyxl import Workbook 
from openpyxl import load_workbook
#import xlsxwriter
import pandas as pd
from retry import retry
#from lxml import etree
from bs4 import BeautifulSoup
from aip import AipNlp
from pprint import pprint

APP_ID = '17237009'
API_KEY = 'i1RVfu7Bazbf6zD22cbERKP0'
SECRET_KEY = 'ccesNDkICGhj5lLkNbdvzdobnMR9pDbP'

client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

origin_path = os.getcwd()

@retry(tries = 5, delay = 2)
def getcontent(url):
    response = requests.get(url)
    web = BeautifulSoup(response.text,"html.parser")
    #pagetype = web.find_all("meta"）
    for a in web.find_all("meta",rel = True):
        if "roll" in str(a["href"]): 
            pagetype = 1
            articletype = "快讯"
        elif "morning" in str(a["href"]): 
            pagetype = 2
            articletype = "内参"
        else:
            pagetype = 3
            articletype = "深度"
        #print(pagetype)
        #print(articletype)

    '''    
    if pagetype:
        heads = web.find_all("div",attrs = {"class":"jsx-1016208558 title fontBold"})
    else: 
        heads = web.find_all("div",attrs = {"class":"jsx-1016208558 title fontBold"})
    for a in heads:
        title = a.string
        print(title)
    '''
    if pagetype != 1:
        title = web.title.string
        sent_title = client.sentimentClassify(title)
    #keyword = client.keyword(title)    

    else:
        title = "电报：无标题"
        sent_title = {'positive_prob': 0, 'confidence': 0, 'negative_prob': 0, 'sentiment': 0}
        #print(title)

        
    '''
    if pagetype:
        depths = web.find_all("a", attrs = {"href" : "/depth"})
    else:
        depths = web.find_all("a", attrs = {"href" : "/telegraph"})
        
    for a in depths:
        depth = a.string
        print(depth)
        break
    '''

    times = web.find_all("div",attrs = {"class":"jsx-1016208558 ctime"})
    for a in times:
        dateandtime = a.string
        date = dateandtime[0:10]
        time = dateandtime[-8:]
        #print(date,time)

    if pagetype == 3:
        writers = web.find_all("span",attrs = {"class":"jsx-1016208558 writer"})
        for a in writers:
            #print(a)
            if "|" not in a.string:
                writer = "/"
                media = a.string
            else:
                writerandfirm = a.string.split("|")
                writer = writerandfirm[0]
                media = writerandfirm[1]
            #print(writer,media)
    else:
        writer = "／"
        media = "财联社"
        #print(writer,media)


    reads = web.find_all("div",attrs = {"class":"jsx-1016208558 readNum"})
    for a in reads:
        a= str(a)
        take = re.compile("-->"+'(.*?)'+"</",re.S)
        b = take.findall(a) #取字符串中的阅读数量，findall结果为列表
        readnum = int(b[0]) #取列表的数字
        #print(readnum)

    if pagetype != 1:
        origins = web.find_all("span",attrs = {"class":"jsx-1016208558 tag"})
        if origins == []:
            origin = "/"
        else:    
            for a in origins:
                origin = a.string
                #print(origin)
    else:
        origin = "原创"
        #print(origin)

    Bigcontents = web.find_all("div",attrs = {"class":"jsx-1016208558 thisContent c-000"})
    content = ""
    writer_k = 1
    writer_list = []
    for a in Bigcontents:
        if pagetype == 1:
            content = a.string     
        else:
            ptag = a.find_all("p")
            for b in ptag:
                c = b.string
                if c == None :
                    c = "/n"
                getwrtier_list = ["作者","本报记者","特约作者","记者"]
                if writer_k == 1:
                    for i in getwrtier_list:
                        if i in c:
                            d = re.compile(i+' (.*?)' + "/n",re.S).findall(c)
                            e = re.compile(i+' (.*?)' + "报道",re.S).findall(c)
                            f = re.compile(i+' (.*?)' + "  ",re.S).findall(c)
                            g = re.compile(i+' (.*?)' + "）",re.S).findall(c)
                            h = re.findall("(?<=" +i + ")(.*?)", c)
                            print(d,e,f,g,h)
                            #print(len(d),len(e),len(f),len(g),len(h))
                            if  d:
                                writer_list.append(d[0])
                            if  e:
                                writer_list.append(e[0])
                            if  f :
                                writer_list.append(f[0])
                            if  g :
                                writer_list.append(g[0])
                            #if  h :
                            #    writer_list.append(h[0])
                            if not writer_list:
                                writer = c
                               # print(writer)
                            #print(writer_list)
                            else :
                                writer = min(writer_list,key = len)
                            writer.replace(" ","") 
                                #print(writer)
                            break                        
                writer_k += 1
                content = content + c
        #keyword = client.keyword(content)    
        sent_content = client.sentimentClassify(content)
        #sent_content_list = list(sent_content.values()) 字典转列表
        #print(content)

    list_content = [url,articletype, title, date, time, writer, media, origin, readnum, content, sent_title["positive_prob"], sent_title["confidence"], sent_title["negative_prob"], sent_title["negative_prob"], sent_title["sentiment"], sent_content["positive_prob"],sent_content["confidence"],sent_content["negative_prob"],sent_content["sentiment"]]
    print(list_content)
    return list_content
    #return articletype, title, date, time, writer, media, readnum, content

def savexlsx(r,list_content):
    wb = load_workbook("财联社新闻汇总.xlsx")
    sheet = wb["Sheet"]
    c = 1
    for item in list_content:
        sheet.cell(row = r, column = c).value = item
        c += 1
    
    wb.save("财联社新闻汇总.xlsx")


def main():
    url_head = "https://www.cls.cn/depth/"
    wb = Workbook() 
    sheet = wb.active
    label_list =["url","articletype", "title", "date", "time", "writer", "media", "origin", "readnum", "content", "sent_title_positive_prob", "sent_title_confidence", "sent_title_negative_prob", "sent_title_negative_prob", "sent_title_sentiment", "sent_content_positive_prob","sent_content_confidence","sent_content_negative_prob","sent_content_sentiment"]
    c = 1
    for item in label_list:
        sheet.cell(row = 1, column = c).value = item 
        c += 1
    wb.save("财联社新闻汇总.xlsx")

    r = 2
    for i in range(229,400) : 
        url_tail = "%06d" %i #补齐前面的0
        url_tail = str(url_tail)
        url = url_head + url_tail    
        list_content = getcontent(url)
        if list_content == []:
            continue
        else:
            savexlsx(r,list_content)
            r += 1

if __name__ == "__main__":
    main()