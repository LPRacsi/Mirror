# coding=utf-8
# !/usr/bin/python

import datetime
import subprocess
import traceback
from multiprocessing import Process

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QAction
from idna import unichr

from TrainData import INDEXES, TrainData
from WeatherData import WeatherData

firstRowYChord = 500
rowOffset = 55
forecastRowOffset = 35
cellOffset = 230
fCellOffset = 180
partOfTheDayLines = 4
forecastRows = partOfTheDayLines * 3
weatherCoordOffset = 5
weatherForecastrowOffsetMultiplier = 6
weekDayList = ['Hétfõ', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap']
forecastWeatherTableYOffset = 100
temperatureXOffset = 650
trainsXOffset = 30


class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Smart mirror")
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.degree = unichr(176)
        self.redrawCount = 0
        self.setPalette(p)

        self.prevTrainLabel = QLabel(self)
        self.prevTrainLabel1 = QLabel(self)
        self.prevTrainLabel2 = QLabel(self)
        self.prevTrainLabel3 = QLabel(self)

        self.nextTrainLabel = QLabel(self)
        self.nextTrainLabel1 = QLabel(self)
        self.nextTrainLabel2 = QLabel(self)
        self.nextTrainLabel3 = QLabel(self)

        self.nextTrain1Label = QLabel(self)
        self.nextTrain1Label1 = QLabel(self)
        self.nextTrain1Label2 = QLabel(self)
        self.nextTrain1Label3 = QLabel(self)

        self.nextTrain2Label = QLabel(self)
        self.nextTrain2Label1 = QLabel(self)
        self.nextTrain2Label2 = QLabel(self)
        self.nextTrain2Label3 = QLabel(self)

        self.startTime = QLabel(self)
        self.lateTime = QLabel(self)
        self.arrivalTime = QLabel(self)
        self.arrivalStation = QLabel(self)
        self.line = QLabel(self)
        self.time = QLabel(self)
        self.date = QLabel(self)

        self.temperature = QLabel(self)
        self.weather = [QLabel(self), QLabel(self), QLabel(self)]
        self.clouds = QLabel(self)
        self.wind = QLabel(self)

        self.weatherForecastWeek = []
        self.forecastSeparatorLine = []
        self.forecastSeparatorPartOfTheDay = []
        self.forecastDayIdentify = []
        for i in range(4):
            self.forecastSeparatorLine.append(QLabel(self))
            self.forecastSeparatorPartOfTheDay.append(QLabel(self))
        for i in range(5):
            self.forecastDayIdentify.append(QLabel(self))
        for i in range(5 * forecastRows):
            self.weatherForecastWeek.append(QLabel(self))

        self.trainLabelFont = QtGui.QFont("Times", 35, QtGui.QFont.Normal)
        self.dayLabelFont = QtGui.QFont("Times", 30, QtGui.QFont.Normal)
        self.timeLabelFont = QtGui.QFont("Times", 150, QtGui.QFont.Normal)
        self.tempLabelFont = QtGui.QFont("Times", 100, QtGui.QFont.Normal)
        self.dateLabelFont = QtGui.QFont("Times", 45, QtGui.QFont.Normal)
        self.forecastLabelFont = QtGui.QFont("Times", 20, QtGui.QFont.Normal)

        exit_action = QAction("", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip('')
        exit_action.triggered.connect(self.showNormalAndExit)
        exit_full_screen = QAction("", self)
        exit_full_screen.setShortcut("Ctrl+X")
        exit_full_screen.setStatusTip('')
        exit_full_screen.triggered.connect(self.showNormal)
        return_full_screen = QAction("", self)
        return_full_screen.setShortcut("Ctrl+A")
        return_full_screen.setStatusTip('')
        return_full_screen.triggered.connect(self.showFullScreen)
        self.statusBar()
        self.setStyleSheet("""
            QMenuBar {
                background-color: rgb(0,0,0);
                color: rgb(255,255,255);
                border: 1px solid #000;
            }

            QMenuBar::item {
                background-color: rgb(0,0,0);
                color: rgb(255,255,255);
            }

            QMenuBar::item::selected {
                background-color: rgb(0,0,0);
            }

            QMenu {
                background-color: rgb(0,0,0);
                color: rgb(255,255,255);
                border: 1px solid #000;           
            }

            QMenu::item::selected {
                background-color: rgb(0,0,0);
            }
        """)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('')
        fileMenu.addAction(exit_action)
        fileMenu.addAction(exit_full_screen)
        fileMenu.addAction(return_full_screen)
        mainMenu.resize(0, 0)

        self.colorWhite = 'color: white'
        self.colorGrey = 'color: grey'
        self.colorDarkGrey = 'color: #1e1e1e'

        self.showFullScreen()
        self.trainData = TrainData()
        self.weatherData = WeatherData()
        self.setTrainTexts()
        self.initTrainsLabel()
        self.initDateTimeLabels()
        self.initWeatherLabels()
        self.initForecastWeatherLabels()
        self.setTrains()
        self.setDateTime()
        self.setWeather()
        self.setForecastWeather()
        # sensor = Process()
        # subprocess.run('python3 sensor_handler.py', shell=True, start_new_session=True)

    def initTrainsLabel(self):
        self.prevTrainLabel.setStyleSheet(self.colorWhite)
        self.prevTrainLabel.move(trainsXOffset, firstRowYChord + rowOffset)
        self.prevTrainLabel.setFont(self.trainLabelFont)
        self.prevTrainLabel.resize(270, 40)
        self.prevTrainLabel1.move(trainsXOffset + cellOffset, firstRowYChord + rowOffset)
        self.prevTrainLabel1.setStyleSheet(self.colorWhite)
        self.prevTrainLabel1.setFont(self.trainLabelFont)
        self.prevTrainLabel1.resize(270, 40)
        self.prevTrainLabel2.move(trainsXOffset + 2 * cellOffset, firstRowYChord + rowOffset)
        self.prevTrainLabel2.setStyleSheet(self.colorWhite)
        self.prevTrainLabel2.setFont(self.trainLabelFont)
        self.prevTrainLabel2.resize(270, 40)
        self.prevTrainLabel3.move(trainsXOffset + 3 * cellOffset, firstRowYChord + rowOffset)
        self.prevTrainLabel3.setStyleSheet(self.colorWhite)
        self.prevTrainLabel3.setFont(self.trainLabelFont)
        self.prevTrainLabel3.resize(270, 40)

        self.nextTrainLabel.move(trainsXOffset, firstRowYChord + 2 * rowOffset)
        self.nextTrainLabel.setStyleSheet(self.colorWhite)
        self.nextTrainLabel.setFont(self.trainLabelFont)
        self.nextTrainLabel.resize(270, 40)
        self.nextTrainLabel1.move(trainsXOffset + cellOffset, firstRowYChord + 2 * rowOffset)
        self.nextTrainLabel1.setStyleSheet(self.colorWhite)
        self.nextTrainLabel1.setFont(self.trainLabelFont)
        self.nextTrainLabel1.resize(270, 40)
        self.nextTrainLabel2.move(trainsXOffset + 2 * cellOffset, firstRowYChord + 2 * rowOffset)
        self.nextTrainLabel2.setStyleSheet(self.colorWhite)
        self.nextTrainLabel2.setFont(self.trainLabelFont)
        self.nextTrainLabel2.resize(270, 40)
        self.nextTrainLabel3.move(trainsXOffset + 3 * cellOffset, firstRowYChord + 2 * rowOffset)
        self.nextTrainLabel3.setStyleSheet(self.colorWhite)
        self.nextTrainLabel3.setFont(self.trainLabelFont)
        self.nextTrainLabel3.resize(270, 40)

        self.nextTrain1Label.move(trainsXOffset, firstRowYChord + 3 * rowOffset)
        self.nextTrain1Label.setStyleSheet(self.colorGrey)
        self.nextTrain1Label.setFont(self.trainLabelFont)
        self.nextTrain1Label.resize(270, 40)
        self.nextTrain1Label1.move(trainsXOffset + cellOffset, firstRowYChord + 3 * rowOffset)
        self.nextTrain1Label1.setStyleSheet(self.colorGrey)
        self.nextTrain1Label1.setFont(self.trainLabelFont)
        self.nextTrain1Label1.resize(270, 40)
        self.nextTrain1Label2.move(trainsXOffset + 2 * cellOffset, firstRowYChord + 3 * rowOffset)
        self.nextTrain1Label2.setStyleSheet(self.colorGrey)
        self.nextTrain1Label2.setFont(self.trainLabelFont)
        self.nextTrain1Label2.resize(270, 40)
        self.nextTrain1Label3.move(trainsXOffset + 3 * cellOffset, firstRowYChord + 3 * rowOffset)
        self.nextTrain1Label3.setStyleSheet(self.colorGrey)
        self.nextTrain1Label3.setFont(self.trainLabelFont)
        self.nextTrain1Label3.resize(270, 40)

        self.nextTrain2Label.move(trainsXOffset, firstRowYChord + 4 * rowOffset)
        self.nextTrain2Label.setStyleSheet(self.colorDarkGrey)
        self.nextTrain2Label.setFont(self.trainLabelFont)
        self.nextTrain2Label.resize(270, 40)
        self.nextTrain2Label1.move(trainsXOffset + cellOffset, firstRowYChord + 4 * rowOffset)
        self.nextTrain2Label1.setStyleSheet(self.colorDarkGrey)
        self.nextTrain2Label1.setFont(self.trainLabelFont)
        self.nextTrain2Label1.resize(270, 40)
        self.nextTrain2Label2.move(trainsXOffset + 2 * cellOffset, firstRowYChord + 4 * rowOffset)
        self.nextTrain2Label2.setStyleSheet(self.colorDarkGrey)
        self.nextTrain2Label2.setFont(self.trainLabelFont)
        self.nextTrain2Label2.resize(270, 40)
        self.nextTrain2Label3.move(trainsXOffset + 3 * cellOffset, firstRowYChord + 4 * rowOffset)
        self.nextTrain2Label3.setStyleSheet(self.colorDarkGrey)
        self.nextTrain2Label3.setFont(self.trainLabelFont)
        self.nextTrain2Label3.resize(270, 40)

    def setTrains(self):
        try:
            self.trainData.refreshTrainList()
        except:
            self.allTrainInfo = []
            print('Exception during train data request')
            traceback.print_exc()

        if self.trainData.getPrevTrain() is not None:
            # Cleat label content
            self.prevTrainLabel.setText("")
            self.prevTrainLabel1.setText("")
            self.prevTrainLabel2.setText("")
            self.prevTrainLabel3.setText("")

            self.prevTrainLabel.setText(str(self.trainData.getPrevTrain()[INDEXES["Indulás"]]["Indulás"]))
            self.prevTrainLabel1.setText(str(self.trainData.getPrevTrain()[INDEXES["Késés"]]["Késés"]))
            self.prevTrainLabel2.setText(str(self.trainData.getPrevTrain()[INDEXES["Érkezés"]]["Érkezés"]))
            self.prevTrainLabel3.setText(str(self.trainData.getPrevTrain()[INDEXES["Végállomás"]]["Végállomás"]))
        else:
            self.prevTrainLabel.setText("")
            self.prevTrainLabel1.setText("")
            self.prevTrainLabel2.setText("")
            self.prevTrainLabel3.setText("")

        if self.trainData.getNextTrains()[0] is not None:
            # Cleat label content
            self.nextTrainLabel.setText("")
            self.nextTrainLabel1.setText("")
            self.nextTrainLabel2.setText("")
            self.nextTrainLabel3.setText("")

            self.nextTrainLabel.setText(str(self.trainData.getNextTrains()[0][INDEXES["Indulás"]]["Indulás"]))
            self.nextTrainLabel1.setText(str(self.trainData.getNextTrains()[0][INDEXES["Késés"]]["Késés"]))
            self.nextTrainLabel2.setText(str(self.trainData.getNextTrains()[0][INDEXES["Érkezés"]]["Érkezés"]))
            self.nextTrainLabel3.setText(str(self.trainData.getNextTrains()[0][INDEXES["Végállomás"]]["Végállomás"]))
        else:
            self.nextTrainLabel.setText("")
            self.nextTrainLabel1.setText("")
            self.nextTrainLabel2.setText("")
            self.nextTrainLabel3.setText("")

        if self.trainData.getNextTrains()[1] is not None:
            # Cleat label content
            self.nextTrain1Label.setText("")
            self.nextTrain1Label1.setText("")
            self.nextTrain1Label2.setText("")
            self.nextTrain1Label3.setText("")

            self.nextTrain1Label.setText(str(self.trainData.getNextTrains()[1][INDEXES["Indulás"]]["Indulás"]))
            self.nextTrain1Label1.setText(str(self.trainData.getNextTrains()[1][INDEXES["Késés"]]["Késés"]))
            self.nextTrain1Label2.setText(str(self.trainData.getNextTrains()[1][INDEXES["Érkezés"]]["Érkezés"]))
            self.nextTrain1Label3.setText(str(self.trainData.getNextTrains()[1][INDEXES["Végállomás"]]["Végállomás"]))
        else:
            self.nextTrain1Label.setText("")
            self.nextTrain1Label1.setText("")
            self.nextTrain1Label2.setText("")
            self.nextTrain1Label3.setText("")

        if self.trainData.getNextTrains()[2] is not None:
            # Cleat label content
            self.nextTrain2Label.setText("")
            self.nextTrain2Label1.setText("")
            self.nextTrain2Label2.setText("")
            self.nextTrain2Label3.setText("")

            self.nextTrain2Label.setText(str(self.trainData.getNextTrains()[2][INDEXES["Indulás"]]["Indulás"]))
            self.nextTrain2Label1.setText(str(self.trainData.getNextTrains()[2][INDEXES["Késés"]]["Késés"]))
            self.nextTrain2Label2.setText(str(self.trainData.getNextTrains()[2][INDEXES["Érkezés"]]["Érkezés"]))
            self.nextTrain2Label3.setText(str(self.trainData.getNextTrains()[2][INDEXES["Végállomás"]]["Végállomás"]))
        else:
            self.nextTrain2Label.setText("")
            self.nextTrain2Label1.setText("")
            self.nextTrain2Label2.setText("")
            self.nextTrain2Label3.setText("")

    def setTrainTexts(self):
        self.startTime.setText("Indulás")
        self.startTime.setStyleSheet(self.colorWhite)
        self.startTime.setFont(self.trainLabelFont)
        self.startTime.move(trainsXOffset, firstRowYChord)
        self.startTime.resize(150, 50)
        self.lateTime.setText("Késés")
        self.lateTime.setStyleSheet(self.colorWhite)
        self.lateTime.setFont(self.trainLabelFont)
        self.lateTime.move(trainsXOffset + cellOffset, firstRowYChord)
        self.lateTime.resize(150, 50)
        self.arrivalTime.setText("Érkezés")
        self.arrivalTime.setStyleSheet(self.colorWhite)
        self.arrivalTime.setFont(self.trainLabelFont)
        self.arrivalTime.move(trainsXOffset + 2 * cellOffset, firstRowYChord)
        self.arrivalTime.resize(150, 45)
        self.arrivalStation.setText("Végállomás")
        self.arrivalStation.setStyleSheet(self.colorWhite)
        self.arrivalStation.setFont(self.trainLabelFont)
        self.arrivalStation.resize(220, 50)
        self.arrivalStation.move(trainsXOffset + 3 * cellOffset, firstRowYChord)
        self.line.setText("------------------------------------------------------------")
        self.line.move(trainsXOffset, firstRowYChord + rowOffset + 20)
        self.line.setStyleSheet(self.colorWhite)
        self.line.setFont(self.trainLabelFont)
        self.line.resize(1000, 50)

    def initDateTimeLabels(self):
        self.time.move(20, 40)
        self.time.setStyleSheet(self.colorWhite)
        self.time.setFont(self.timeLabelFont)
        self.time.resize(550, 150)
        self.date.move(20, 350)
        self.date.setStyleSheet(self.colorWhite)
        self.date.setFont(self.dateLabelFont)
        self.date.resize(550, 65)

    def setDateTime(self):
        now = datetime.datetime.now()
        toDayWeekDay = datetime.datetime.today().weekday()
        minute = now.minute

        if minute < 10:
            minute = '0' + str(minute)

        month = now.month
        if month < 10:
            month = '0' + str(month)
        day = now.day
        if day < 10:
            day = '0' + str(day)
        # print(now.hour, ":", now.minute)
        self.date.setText(str(now.year) + '.' + str(month) + '.' + str(day) + '. ' + weekDayList[toDayWeekDay])
        self.time.setText(str(now.hour) + ' : ' + str(minute))

    def initWeatherLabels(self):
        self.temperature.setStyleSheet(self.colorWhite)
        self.temperature.move(temperatureXOffset, 40)
        self.temperature.setFont(self.tempLabelFont)
        self.temperature.resize(350, 150)
        for i in range(0, 3):
            self.weather[i].setStyleSheet(self.colorWhite)
            self.weather[i].move(temperatureXOffset, 190 + i * rowOffset)
            self.weather[i].setFont(self.trainLabelFont)
            self.weather[i].resize(350, 50)
        self.clouds.setStyleSheet(self.colorWhite)
        self.clouds.move(temperatureXOffset, 190 + 3 * rowOffset)
        self.clouds.setFont(self.trainLabelFont)
        self.clouds.resize(350, 50)
        self.wind.setStyleSheet(self.colorWhite)
        self.wind.move(temperatureXOffset, 190 + 4 * rowOffset)
        self.wind.setFont(self.trainLabelFont)
        self.wind.resize(350, 50)

    def initForecastWeatherLabels(self):
        count = 0
        multi = 0
        for i in self.weatherForecastWeek:
            i.setStyleSheet(self.colorWhite)
            i.setFont(self.forecastLabelFont)
            i.resize(400, 65)
            if count % forecastRows == 0:
                multi = count / forecastRows
            i.move(100 + multi * fCellOffset,
                   firstRowYChord + forecastWeatherTableYOffset + weatherForecastrowOffsetMultiplier * rowOffset + (
                           count % forecastRows) * forecastRowOffset)
            count += 1
        partOfTheDay = ["Reggel", "Nappal", "Este", " "]
        for i in range(4):
            self.forecastSeparatorLine[i].setText(
                "------------------------------------------------------")
            self.forecastSeparatorLine[i].move(100, firstRowYChord + forecastWeatherTableYOffset +
                                               weatherForecastrowOffsetMultiplier * rowOffset + (
                                                       i * ((forecastRows / 3) * forecastRowOffset)) - 5)
            self.forecastSeparatorLine[i].setStyleSheet(self.colorWhite)
            self.forecastSeparatorLine[i].setFont(self.trainLabelFont)
            self.forecastSeparatorLine[i].resize(1000, 35)

            self.forecastSeparatorPartOfTheDay[i].setText(partOfTheDay[i])
            self.forecastSeparatorPartOfTheDay[i].move(5, firstRowYChord + 50 + forecastWeatherTableYOffset +
                                                       weatherForecastrowOffsetMultiplier * rowOffset + (
                                                               i * ((forecastRows / 3) * forecastRowOffset)))
            self.forecastSeparatorPartOfTheDay[i].setStyleSheet(self.colorWhite)
            self.forecastSeparatorPartOfTheDay[i].setFont(self.forecastLabelFont)
            self.forecastSeparatorPartOfTheDay[i].resize(100, 40)

        for i in range(5):
            self.forecastDayIdentify[i].move(100 + i * fCellOffset,
                                             firstRowYChord + forecastWeatherTableYOffset + weatherForecastrowOffsetMultiplier * rowOffset - 30)
            self.forecastDayIdentify[i].setStyleSheet(self.colorWhite)
            self.forecastDayIdentify[i].setFont(self.dayLabelFont)
            self.forecastDayIdentify[i].resize(1000, 35)

    def setWeather(self):
        weatherData = self.weatherData.refreshActualWeatherData()
        self.temperature.setText(str(round(weatherData['main']['temp'])) + self.degree + 'C')
        a = 0
        for weather in weatherData['weather']:
            self.weather[a].setText(weather['description'])
            a += 1
        for i in range(a, 3):
            self.weather[a].setText('')
        self.clouds.setText("Felhõzet: " + str(weatherData['clouds']['all']) + '%')
        self.wind.setText("Szél: " + str(weatherData['wind']['speed']) + " m/s")

    def setForecastWeather(self):
        forecastWeatherData = self.weatherData.prepareDayliForecast(self.weatherData.refreshForecastWeatherData())
        toDayWeekDay = datetime.datetime.today().weekday()
        count = 0
        for i in forecastWeatherData:
            if i != {}:
                self.weatherForecastWeek[count].setText(
                    str(round(i['temp_min'])) + "  -  " + str(round(i['temp_max'])) + self.degree + 'C')
            count += partOfTheDayLines
        count = 1
        for i in forecastWeatherData:
            if i != {}:
                for j in range(len(i['weather'])):
                    self.weatherForecastWeek[count + j].setText(str(i['weather'][j]))
            count += partOfTheDayLines
        for i in range(5):
            weekDayListIndex = toDayWeekDay + i
            if weekDayListIndex > 6:
                weekDayListIndex = weekDayListIndex - 7
            self.forecastDayIdentify[i].setText(str(weekDayList[weekDayListIndex]))
        '''count = 4
        for i in forecastWeatherData:
            if i != {}:
                try:
                    self.weatherForecastWeek[count].setText(str(round(i['snow'], 2)))
                except TypeError:
                    self.weatherForecastWeek[count].setText(str(i['snow']))
            count += increment

        count = 5
        for i in forecastWeatherData:
            if i != {}:
                try:
                    self.weatherForecastWeek[count].setText(str(round(i['rain'], 2)))
                except TypeError:
                    self.weatherForecastWeek[count].setText(str(i['rain']))
            count += increment
        '''

    def updateTrainsAndDate(self):
        # self.cleanTrains()
        self.setDateTime()
        self.setTrains()

    def setwindowSize(self):
        self.showNormal()

    @pyqtSlot()
    def exiting(self):
        print("Exit")
        self.t.cancel()
        sys.exit()

    def showNormalAndExit(self):
        self.showNormal()
        self.exiting()

    def startRefreshThread(self):
        try:
            self.setDateTime()
        except:
            print('setDateTime exception')
            traceback.print_exc()
        try:
            self.setTrains()
        except:
            print('setTrains exception')
            traceback.print_exc()
        try:
            self.setWeather()
        except:
            print('setWeather exception')
            traceback.print_exc()
        try:
            self.setForecastWeather()
        except:
            print('setForecastWeather exception')
            traceback.print_exc()
        self.redrawCount += 1
        console = subprocess.check_output('tvservice -s', shell=True).split()[1]
        if console == b'0x120002' and self.redrawCount > 10:  # For redraw purpose
            self.showNormal()
            self.showFullScreen()
            self.redrawCount = 0
        self.t = threading.Timer(30, self.startRefreshThread)
        self.t.start()


if __name__ == "__main__":
    import sys
    import threading

    app = QApplication(sys.argv)
    app.setOverrideCursor(QCursor(Qt.BlankCursor))
    GUI = Window()
    GUI.startRefreshThread()
    sys.exit(app.exec_())
