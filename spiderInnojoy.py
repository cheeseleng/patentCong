# -*- coding: utf-8 -*-
'''
Created on 16/10/14

@author: leng

'''

# 程序所需要的依赖包导入

from pymongo import MongoClient
import requests
import json
import math
import xlrd
import time


class Spider:
    def __init__(self):    # 初始化全局变量
        self.param = {
            "patentSearchConfig": {
                "Action": "Search",
                "AddOnes": "",
                "DBOnly": 0,
                "Database": "nzpat,aupat,ttpat,dopat,copat,crpat,svpat,nipat,hnpat,gtpat,ecpat,papat,arpat,mxpat,capat,cupat,"
                            "pepat,clpat,brpat,appat,oapat,zwpat,dzpat,tnpat,zmpat,mwpat,mapat,kepat,egpat,zapat,gcpat,uzpat,"
                            "kzpat,tjpat,kgpat,idpat,mypat,ampat,trpat,phpat,sgpat,ilpat,mnpat,thpat,vnpat,jopat,inpat,inapp,"
                            "bapat,ddpat,cspat,eapat,mepat,sipat,bypat,bgpat,cypat,eepat,gepat,hrpat,lvpat,mdpat,rspat,ropat,"
                            "smpat,skpat,yupat,supat,ltpat,lupat,mcpat,mtpat,ptpat,atpat,uypat,uapat,espat,itpat,hupat,bepat,"
                            "iepat,sepat,plpat,nlpat,fipat,nopat,czpat,grpat,dkpat,ispat,chpat,frpat,deuti,depat,deapp,kruti,"
                            "krpat,krapp,jputi,jppat,jpapp,wopat,usdes,uspat,uspat1,usapp,gbpat,eppat,epapp,rupat,hkpat,twpat,"
                            "fmsq,wgzl,syxx,fmzl",
                "DelOnes": "",
                "GUID": "",
                "Page": "1",
                "PageSize": "10",
                "Query": "",
                "RemoveOnes": "",
                "SmartSearch": "",
                "Sortby": "-IDX,PNM",
                "TreeQuery": "",
                "TrsField": "",
                "Verification": None
            },
            "requestModule": "PatentSearch",
            "userId": ""
        }
        self.header = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Content-Length": "1008",
            "Content-Type": "application/json",
            "Host": "www.innojoy.com",
            "Origin": "http://www.innojoy.com",
            "Referer": "http://www.innojoy.com/searchresult/default.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.9 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        self.PatentType = {
            "中国发明专利": ["china_invent", 0],
            "中国实用新型": ["china_use", 1],
            "中国外观专利": ["china_appearance", 2],
            "中国发明授权": ["china_authorize", 3],
            "中国台湾": ["taiwan", 4],
            "中国香港": ["hongkong", 5],
            "美国专利申请": ["usa_patent", 6],
            "美国授权专利": ["usa_authorize", 7],
            "美国外观设计": ["usa_appearance", 8],
            "EP专利申请": ["ep_patent", 9],
            "EP授权专利": ["ep_authorize", 10],
            "WO专利申请": ["wo_patent", 11],
            "日本专利申请": ["japan_patent", 12],
            "日本授权专利": ["japan_authorize", 13],
            "日本实用新型": ["japan_appearance", 14],
            "韩国专利申请": ["korea_patent", 15],
            "韩国授权专利": ["korea_authorize", 16],
            "韩国实用新型": ["korea_use", 17],
            "德国专利申请": ["german_patent", 18],
            "德国授权专利": ["german_authorize", 19],
            "德国实用新型": ["german_use", 20],
            "俄罗斯": ["russia", 21],
            "英国": ["uk", 22],
            "法国": ["france", 23]
        }

    def get_company(self):   # 从excel中读取公司信息
        xlsx = xlrd.open_workbook("patent_for_RA.xlsx")
        with open('finishedCompany.txt', 'rb') as f:   # 这个txt存储的是已完成公司的名单
            content = f.read()
            f.close()
        for i in range(1, 2440):
            self.__init__()
            infos = xlsx.sheet_by_index(0).row_values(i)
            alliance_ID = str(infos[0])[:3]
            member_ID = infos[1]
            company = infos[2].strip()
            if company in content.decode('utf-8'):    # 如果发现已爬取过，跳下一个公司
                continue
            self.get_count(alliance_ID, member_ID, company)

    def get_count(self, alliance_ID, member_ID, company):  # 获取公司需要爬取的专利总数
        self.log(u'正在爬取：' + company)
        try:
            self.param["patentSearchConfig"]["Query"] = company
            # 通过post请求在网站上获取专利信息
            content = requests.post("http://www.innojoy.com/client/interface.aspx", data=json.dumps(self.param),
                                    headers=self.header, timeout=60).text
            print content
            # 解析返回的json格式信息
            count = json.loads(content)["Option"]["Count"]
            # 对没有专利的公司进行处理
            if int(count) == 0:
                self.file('', alliance_ID + member_ID + '.txt', company + u'没有查询到专利')
                return None
            # 获取页数
            pagenum = int(math.ceil(count / 10.0))
            # 获取GUID
            GUID = json.loads(content)["Option"]["GUID"]
            self.param["patentSearchConfig"]["GUID"] = GUID
            self.log(u'一共有' + str(count) + u'条专利，共' + str(pagenum) + u'页')
            self.log(u'正在爬取第1页')
            self.file('', 'finishedCompany.txt', company)
            self.get_data(alliance_ID, member_ID, company, content)
            # 开始根据页数爬取
            for i in range(1, pagenum + 1):
                self.log(u'正在爬取第' + str(i + 1) + u'页')
                self.param["patentSearchConfig"]["Page"] = str(i)
                try:
                    content_paging = requests.post("http://www.innojoy.com/client/interface.aspx",
                                                   data=json.dumps(self.param),
                                                   headers=self.header, timeout=60).text
                    self.get_data(alliance_ID, member_ID, company, content_paging)
                # 异常处理
                except Exception as e:
                    self.file('', 'errorCompany.txt', company + u'爬取数据发生错误：' + str(e))
                    self.log(company + u'爬取数据发生错误：' + str(e))
                    return 'error'
        # 异常处理
        except Exception as e:
            self.file('', 'errorCompany.txt', company + u'解析专利数发生错误：' + str(e))
            self.log(company + u'解析专利数发生错误：' + str(e))
            return 'error'

    def get_data(self, alliance_ID, member_ID, company, content):
        print content
        # 对获取的专利数据进行处理，整合
        patent_list = json.loads(content)["Option"]["PatentList"]
        for patent in patent_list:
            IDX = patent["IDX"]
            if int(IDX) >= 80:
                DPI_index = 3.5
            else:
                DPI_index = 3
            data = alliance_ID + ',' + member_ID + ',' + self.PatentType[patent["DBName"].encode('utf-8')][
                0] + ',' + str(
                DPI_index) + ',' + patent["AN"] + ',' + patent["AD"].replace(".", "") + "," + patent["PNM"] + ',' + \
                   patent["PD"].replace(".", "") + ',' + patent["PATMS"] + ',' + str(patent["PIC"]) + ',' + \
                   patent["CO"].split(";")[0] + ',' + patent["AS"] + ',' + patent["GRNT"] + ',' + patent["BYZS"] + ',' + \
                   str(patent["CHQ"]) + ',' + str(patent["CLMN"]) + ',' + company
            self.file('flag', 'data/' + alliance_ID + member_ID + '.txt', data)
            self.mongo(alliance_ID, member_ID, patent["DBName"].encode('utf-8'),
                       patent["AD"].replace(".", ""), company)

    def mongo(self, alliance_ID, member_ID, patent_type, apply_time, company):
        # firm专利数据进行处理，存入数据库
        key = alliance_ID + member_ID + apply_time[:6]
        data = {
            "key": key,
            "company": company,
            "alliance_ID": alliance_ID,
            "member_ID": member_ID,
            "apply_time": apply_time[:6],
            "china_invent": 0,
            "china_use": 0,
            "china_appearance": 0,
            "china_authorize": 0,
            "taiwan": 0,
            "hongkong": 0,
            "usa_patent": 0,
            "usa_authorize": 0,
            "usa_appearance": 0,
            "ep_patent": 0,
            "ep_authorize": 0,
            "wo_patent": 0,
            "japan_patent": 0,
            "japan_authorize": 0,
            "japan_appearance": 0,
            "korea_patent": 0,
            "korea_authorize": 0,
            "korea_use": 0,
            "german_patent": 0,
            "german_authorize": 0,
            "german_use": 0,
            "russia": 0,
            "uk": 0,
            "france": 0
        }
        # 连接本地数据库
        client = MongoClient('localhost', 27017)
        db = client["patentCong"]
        try:
            # 判断数据库中是否有改月份信息，如有，在数目后加1
            content = db.patent.find({"key": key})[0]
            count = content[self.PatentType[patent_type][0]]
            db.patent.update({"key": key}, {"$set": {self.PatentType[patent_type][0]: count + 1}})
            self.log(u'正在更新专利月份数据')
        except:
            # 如无，插入新数据
            data[self.PatentType[patent_type][0]] = 1
            db.patent.insert(data)
            self.log(u'正在添加专利月份数据')

    def file(self, flag, filename, data):
        # 将部分写文件的操作函数化
        with open(filename, 'a+') as f:
            if flag == 'empty':   # 如传入标志带有empty,清空文件，重新写入数据
                f.truncate()
            elif flag == 'repeat': # 如传入标志带有repeat,检查文件中是否有改公司，如有，不再重复写入
                content = f.read()
                if data in content:
                    f.close()
                    return 'Repeat'
            f.write(data.encode('utf-8') + '\n')
            f.close()
            return 'Success'

    def log(self, data):
        # 日志函数，将日志打印出来并写入log.txt
        print data
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open('log.txt', 'a+') as f:
            f.write(str(nowtime) + '->' + data.encode('utf-8') + '\n')
            f.close()

# 主函数
if __name__ == '__main__':
    l = Spider()
    l.get_company()
