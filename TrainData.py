import datetime
import re

import requests
from bs4 import BeautifulSoup

INDEXES = {"Indulás": 0,
           "Érkezés": 1,
           "Végállomás": 2,
           "Késés": 3}


class TrainData:
    def __init__(self):

        self.arrival = '<td class="l" style="text-align:left">[0-2][0-9]:[0-5][0-9] <span style="font-size:80%;white-space:nowrap">Budapest-Déli</span></td>'
        self.erdRegex = '>Érd<'
        self.departure = '<td class="l" style="text-align:left">[0-2][0-9]:[0-5][0-9] <span style="font-size:80%;white-space:nowrap"></span></td>'
        self.timeRegex = '[0-2][0-9]:[0-5][0-9]'
        self.lateRegex = '<span style=".*?color:red">[0-2][0-9]:[0-5][0-9]</span>'
        self.regex5 = self.timeRegex + ' '
        self.regex6 = self.regex5 + '.*?Budapest-Déli'
        self.regex7 = self.regex5 + '.*?Kelenföld'
        self.trains = {}
        self.allTrainInfo = []
        self.startStateFound = False
        # self.refreshTrainList()

    def refreshTrainList(self):
        now = datetime.datetime.now()
        url = "http://elvira.mav-start.hu/elvira.dll/uf?language=1&i=%C3%89rd&e=BUDAPEST*&d={}.{}.{}.&mikor=-1&u=1156&go=".format(
            now.year, now.month, now.day)
        url_ = "http://elvira.mav-start.hu/elvira.dll/x/uf?iehack=%3F&ed=5C66C35A&mikor=-1&isz=0&language=1&k=&ref=&retur=&nyit=&_charset_=UTF-8&vparam=&i=%C3%89rd&e=Budapest+D%C3%A9li+%5BBudapest-D%C3%A9li%5D&v=&d=19.02.16&u=1156&go=Menetrend"

        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find(id="timetable")  # ->get the table of timetable
        del soup
        start_found = False
        start_time_found = False
        train_info_iterator = 0
        train_info = []
        self.allTrainInfo = []
        table_tbody = table.find('tbody')  # ->The real content of the timetable
        for tableTbodyTr in table_tbody.children:  # -> Get the rows of the timetable
            try:
                for tableTbodyTrtds in tableTbodyTr.children:
                    if re.findall(self.regex5, str(tableTbodyTrtds)) and not start_time_found:
                        start_time_found = True
                        train_info.append({'Indulás': re.findall(self.regex5, str(tableTbodyTrtds))[0]})
                    if re.findall(self.regex6, str(tableTbodyTrtds)) and start_time_found:
                        start_time_found = False
                        train_info.append({'Érkezés': re.findall(self.regex5, str(tableTbodyTrtds))[0]})
                        train_info.append({'Végállomás': re.findall('Budapest-Déli', str(tableTbodyTrtds))[0]})
                    if re.findall(self.regex7, str(tableTbodyTrtds)) and start_time_found:
                        start_time_found = False
                        train_info.append({'Érkezés': re.findall(self.regex5, str(tableTbodyTrtds))[0]})
                        train_info.append({'Végállomás': re.findall('Kelenföld', str(tableTbodyTrtds))[0]})
                    if re.findall(self.erdRegex, str(tableTbodyTrtds)):
                        start_found = True
                    if start_found:
                        start_found = False
                        if re.findall(self.lateRegex, str(tableTbodyTrtds)):
                            late = re.findall(self.timeRegex, str(re.findall(self.lateRegex, str(tableTbodyTrtds))))[0]
                        else:
                            late = ''
                        train_info.append({'Késés': late})
                        train_info_iterator += 1
                        self.allTrainInfo.append(train_info)
                        train_info = []
            except AttributeError:
                pass
        r.close()

    def getPrevTrain(self):
        prev_trains = None
        for trains in self.allTrainInfo:
            try:
                hour = str(trains[INDEXES["Indulás"]]['Indulás']).split(':')[0]
            except:
                hour = 0
            try:
                minute = str(trains[INDEXES["Indulás"]]['Indulás']).split(':')[1]
            except:
                minute = 0
            now = datetime.datetime.now()
            if int(hour) * 60 + int(minute) > now.hour * 60 + now.minute:
                return prev_trains
            else:
                prev_trains = trains

    def getNextTrains(self):
        trains1 = None
        trains2 = None
        trains3 = None
        # print('self.allTrainInfo ',self.allTrainInfo)
        for trains in self.allTrainInfo:
            # print('trains:', trains)
            hour = str(trains[INDEXES["Indulás"]]['Indulás']).split(':')[0]
            minute = str(trains[INDEXES["Indulás"]]['Indulás']).split(':')[1]
            now = datetime.datetime.now()
            if int(hour) * 60 + int(minute) > now.hour * 60 + now.minute:
                if trains1 is None:
                    trains1 = trains
                elif trains2 is None:
                    trains2 = trains
                elif trains3 is None:
                    trains3 = trains
        return trains1, trains2, trains3
