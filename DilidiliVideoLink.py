# coding:utf-8

from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re
import os
import configparser
import json

CONFIG_FILE = 'config.cfg'

class DiliDiliAnalysis:

    url = 'http://www.dilidili.wang/'

    def __init__(self):
        self.bangumiList = self.getBangumiList()
        self.weekday = datetime.today().isoweekday() - 1
        self.animeNum = 0
        self.animeInfo = {
            'name'      : '',
            'url'       : '',
            'sections'  : []
        }
        
    def getBangumiList(self):
        html = requests.get(DiliDiliAnalysis.url).content
        ul = BeautifulSoup(html, 'lxml').find_all(attrs={'class','sldr'})[2].contents[1]
        ul = [it for it in ul if it.find('</li>') != -1]
        bangumiList = []
        for li in ul:
            animesLi = li.ul.find_all('li')
            animes = []
            for animeItem in animesLi:
                tmp = animeItem.find_all('a')
                if len(tmp) == 1:
                    animes.append({
                        'name'  : tmp[0].text,
                        'url'   : tmp[0]['href'],
                        'new'   : '',
                        'nurl'  : ''
                    })
                elif len(tmp) == 2:
                    animes.append({
                        'name'  : tmp[0].text,
                        'url'   : tmp[0]['href'],
                        'new'   : tmp[1].text,
                        'nurl'  : tmp[1]['href']
                    })
            bangumiList.append(animes)
            # print(len(animes))

        return bangumiList

    def listBangumi(self):
        for num in range(len(self.bangumiList[self.weekday])):
            print(num, '.  ', self.bangumiList[self.weekday][num]['name'], '  ', 
                self.bangumiList[self.weekday][num]['new'] if self.bangumiList[self.weekday][num]['new'] else '', 
                sep = '')

    def listSection(self):
        self.animeInfo['sections'].clear()

        try:
            animeUrl = self.animeInfo['url']
            html = requests.get(animeUrl).content
            secLi = BeautifulSoup(html, 'lxml').find(attrs={'class', 'time_con'}).ul.find_all('li')
        except:
            print('Something happened.')
            return

        for secS in secLi:
            self.animeInfo['sections'].append({
                'name'  : secS.em.span.text,
                'url'   : secS.a['href']
            })

        for num in range(len(self.animeInfo['sections'])):
            print(num, '.  ', self.animeInfo['sections'][num]['name'], sep = '', end = '\t\t')
            if (num+1)%4 == 0:
                print()
        if (len(self.animeInfo['sections']))%4 != 0:
            print()

    def playAnime(self, secNum):
        if secNum.isdigit() and int(secNum) > -1 and int(secNum) < len(self.animeInfo['sections']):
            secNum = int(secNum)
        else:
            secNum = len(self.animeInfo['sections']) - 1

        videoLink = []

        try:
            secUrl = self.animeInfo['sections'][secNum]['url']
            html = requests.get(secUrl).content
        except:
            print('Get video page failed.')

        # 方法1（适用于iframe中的src并非为js添加）
        videoIframe = BeautifulSoup(html, 'lxml').find('iframe')
        if videoIframe != None:
            print('Method 1')
            if videoIframe['src'].find('.mp4') != -1:
                videoLink.append(re.search('http://(((?!http://).)+?)mp4', videoIframe['src']).group())
            elif videoIframe['src'].find('.m3u8') != -1:
                videoLink.append(re.search('http://(((?!http://).)+?)m3u8', videoIframe['src']).group())
            elif videoIframe['src'].find('.html') != -1:
                mUrl1 = videoIframe['src']
                mUrl2 = mUrl1.replace('?url=', 'player.php?url=')
                mPage = requests.get(mUrl2, headers = {'Referer':mUrl1}).content
                datas = json.loads(re.search(r'{.*}', [line for line in mPage.decode('utf-8').split('\n') if line.find('$.post') != -1][0]).group())
                res = json.loads(requests.post('http://www.skyfollowsnow.pro/api.php',
                    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                    data = datas).text)
                xmlStr = requests.get('http://www.skyfollowsnow.pro/api.php'+ res['url']).text
                videoLink = re.findall(r'\<\!\[CDATA\[(.*?)\]\]\>', xmlStr)

        
        # 方法2
        if BeautifulSoup(html, 'lxml').find(id='player') != None:
            print('Method 2')
            for line in html.decode('utf-8').split('\n'):
                if line.find('var sourceUrl') != -1:
                    link = re.search(r'http://.*?mp4', line)
                    if link != None:
                        videoLink.append(link.group())
                    break
        

        print(videoLink)
        if len(videoLink) == 0:
            print('解析失败')
            return
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        os.popen('"' + config.get('Config', 'PlayerPath') + '" "' + '" "'.join(videoLink) + '"')

    def selWeekday(self, weekday):
        if weekday.isdigit() and int(weekday) > 0 and int(weekday) < 8:
            self.weekday = int(weekday) - 1
        else:
            self.weekday = datetime.today().isoweekday() - 1
        # print(self.weekday)

        self.animeNum = 0
        self.animeInfo = {
            'name'      : '',
            'url'       : '',
            'sections'  : []
        }

        self.listBangumi()

    def selAnime(self, animeNum):
        if animeNum.isdigit() and int(animeNum) > -1 and int(animeNum) < len(self.bangumiList[self.weekday]):
            self.animeNum = int(animeNum)

        self.animeInfo['name'] = self.bangumiList[self.weekday][self.animeNum]['name']
        self.animeInfo['url'] = self.bangumiList[self.weekday][self.animeNum]['url']

        self.listSection()

def main():
    analyzer = DiliDiliAnalysis()
    weekday = '月火水木金土日'
    helpInfo = {
        'sw'    : ['选择星期', ''],
        'sa'    : ['选择番剧', ''],
        'la'    : ['列出番剧', ''],
        'ls'    : ['列出番剧单话', ''],
        'play'  : ['播放选定集', ''],
        'cfg'   : ['设置或查看配置']
    }

    if not os.path.exists(CONFIG_FILE):
        conf = configparser.ConfigParser()
        cfgFile = open(CONFIG_FILE, 'w', encoding='UTF-8')
        
        conf.add_section('Config')
        conf.set('Config', 'PlayerPath', 'C:\Program Files\PotPlayer\PotPlayerMini64.exe')

        conf.write(cfgFile)
        cfgFile.close()

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    for cmd, info in helpInfo.items():
        print(cmd, info)

    while True:
        print('咕嚕靈波:/', weekday[analyzer.weekday], '曜日', sep = '', end = '')
        print('/' if analyzer.animeInfo['name'] else '', analyzer.animeInfo['name'], '$ ', sep = '', end = '')
        command = input().split()
        if not command:
            continue
        # print(command)
        if command[0] == 'sw':
            analyzer.selWeekday('-1' if len(command) == 1 else command[1])
        elif command[0] == 'sa':
            analyzer.selAnime('-1' if len(command) == 1 else command[1])
        elif command[0] == 'la':
            analyzer.listBangumi()
        elif command[0] == 'ls':
            analyzer.listSection()
        elif command[0] == 'play':
            analyzer.playAnime('-1' if len(command) == 1 else command[1])
        elif command[0] == 'cfg':
            if len(command) == 1:
                for it in config.options('Config'):
                    print(it, '\t', config.get('Config', it), sep = '')
            elif command[1] == 'set':
                config.set('Config', command[2], ' '.join(command[3:]))
                config.write(open(CONFIG_FILE, 'w'))
        elif command[0] == 'exit' or command[0] == 'quit' or command[0] == 'q':
            print('See you next time.')
            break
        else:
            print('Unknown command.')
            pass

if __name__ == '__main__':
    main()
