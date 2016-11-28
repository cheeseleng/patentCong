# -*- coding: utf-8 -*-
'''
Created on 2016/11/25

@author: leng

'''





with open('log.txt', 'rb') as f:
    log = f.read()
    f.close()

# print len(log.split('\r'))
#
# companyName = ''
# patentType = ''
# for i in range(0, 1006662):
#     print i
#     contentLog = log.split('\r')[i]
#     if '正在爬取：' in contentLog:
#         companyName = contentLog.split('正在爬取：')[1]
#         patentType = ''
#         page = ''
#     if '发明授权一共有' in contentLog:
#         patentType = 'pig'
#     elif '发明公布一共有' in contentLog:
#         patentType = 'pip'
#     elif '实用新型一共有' in contentLog:
#         patentType = 'pug'
#     elif '外观设计一共有' in contentLog:
#         patentType = 'pdg'
#     if '正在爬取第' in contentLog:
#         if '正在爬取' in log.split('\r')[i+1]:
#             page = contentLog.split('正在爬取第')[1].split('页')[0]
#             result = companyName + '-' + patentType + '-' + page
#             with open('unfinish1125V3.txt', 'a+') as f:
#                 f.write(result)
#                 f.close()








companyLength = len(log.split('正在爬取：'))
# 3343
for i in range(0, 3343):
    print i
    companyContentOne = log.split('正在爬取：')[i+1].split('正在爬取：')[0]
    companyName = companyContentOne.split('\r')[0]
    patentLength = len(companyContentOne.split('\r'))
    patentType = '无'
    for j in range(0, patentLength-1):
        str1 = companyContentOne.split('\r')[j].strip()
        if '发明授权一共有' in str1:
            patentType = 'pig'
        elif '发明公布一共有' in str1:
            patentType = 'pip'
        elif '实用新型一共有' in str1:
            patentType = 'pug'
        elif '外观设计一共有' in str1:
            patentType = 'pdg'
        if '正在爬取第' in str1:
            str2 = companyContentOne.split('\r')[j+1].strip()
            if '正在更新专利月份数据' in str2:
                continue
            elif '正在添加专利月份数据' in str2:
                continue
            patentPage = str1.split('正在爬取第')[1].split('页')[0]
            result = companyName + '-' + patentType + '-' + patentPage + '\r'
            with open('unfinish1125V3.txt', 'a+') as f:
                f.write(result)
                f.close()