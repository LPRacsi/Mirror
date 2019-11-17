import json

import requests

ERD_ID = 3053281
SMART_MIRROR_API_KEY = '4768a8f224f2e3842d8b9459c2197a65'


class WeatherData:
    def __init__(self):
        self.actualUrl = "http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&lang=hu&APPID={}".format(
            ERD_ID, SMART_MIRROR_API_KEY)
        self.forecastUrl = "http://api.openweathermap.org/data/2.5/forecast?id={}&units=metric&lang=hu&APPID={}".format(
            ERD_ID, SMART_MIRROR_API_KEY)
        print("Actual URL: ", self.actualUrl)
        print("Forecast URL: ", self.forecastUrl)

    def refreshActualWeatherData(self):
        r = requests.get(self.actualUrl)
        responseText = json.loads(r.text)
        r.close()

        return responseText

    def refreshForecastWeatherData(self):
        '''
        Refrest the forecast weather data and filters the necesarry information from eaw response.
        :return: A list of 3 hourly forecast weather data.
        '''
        r = requests.get(self.forecastUrl)
        responseText = json.loads(r.text)
        r.close()
        # with open('weather_response.json', 'r') as read:
        #    fileContent = json.load(read)
        weatherDictList = []
        weatherDict = {"temp_max": 0,
                       "temp_min": 0,
                       "weather": [],
                       "snow": 0,
                       "rain": 0,
                       "clouds": 0,
                       "wind": 0,
                       "year": 0,
                       "month": 0,
                       "day": 0,
                       "time": 0
                       }
        for threeHourly in responseText['list']:
            year, month, day = threeHourly['dt_txt'].split("-")
            day, time = day.split(" ")
            weatherDict['temp_min'] = threeHourly['main']['temp_min']
            weatherDict['temp_max'] = threeHourly['main']['temp_max']
            if threeHourly['weather'][0]['description'] == "szórványos felhőzet":
                threeHourly['weather'][0]['description'] = "elszórt felhők"
            weatherDict['weather'].append(threeHourly['weather'][0]['description'])
            try:
                weatherDict['snow'] = threeHourly['snow']['3h']
            except KeyError:
                weatherDict['snow'] = ""
            try:
                weatherDict['rain'] = threeHourly['rain']['3h']
            except KeyError:
                weatherDict['rain'] = ""
            weatherDict['clouds'] = threeHourly['clouds']['all']
            weatherDict['wind'] = threeHourly['wind']['speed']
            weatherDict['year'] = year
            weatherDict['month'] = month
            weatherDict['day'] = day
            weatherDict['time'] = time.split(":")[0]
            weatherDictList.append(weatherDict)
            # Set weatherDict to init values
            weatherDict = {"temp_max": 0, "temp_min": 0, "weather": [], "snow": 0, "rain": 0, "clouds": 0, "wind": 0,
                           "year": 0, "month": 0, "day": 0, "time": 0}

        return weatherDictList

    def _createWeatherSumByDayTime(self, sum, summable):
        '''
        Summarises the weather data.
        :param sum: A list of weather data where the merge will be done.
        :param summable: A list of weather data that will be merged with sum.
        :return: Merged weather data
        '''
        if sum["temp_max"] < summable["temp_max"]:
            sum["temp_max"] = summable["temp_max"]
        if sum["temp_min"] > summable["temp_min"]:
            sum["temp_min"] = summable["temp_min"]
        sum["weather"].extend(summable["weather"])
        sum["weather"] = list(set(sum["weather"]))
        if sum["snow"] == "" and summable["snow"] == "":
            sum["snow"] = ""
        else:
            try:
                float(sum["snow"])
            except ValueError:
                sum["snow"] = summable["snow"]
            else:
                try:
                    sum["snow"] = sum["snow"] + float(summable["snow"])
                except ValueError:
                    sum["snow"] = sum["snow"]

        if sum["rain"] == "" and summable["rain"] == "":
            sum["rain"] = ""
        else:
            try:
                float(sum["rain"])
            except ValueError:
                sum["rain"] = summable["rain"]
            else:
                try:
                    sum["rain"] = sum["rain"] + float(summable["rain"])
                except ValueError:
                    sum["rain"] = sum["rain"]
        return sum

    def prepareDayliForecast(self, weatherDictList):
        '''
        Prepares
        :param weatherDictList: A list of 3 hourly forecast weather data.
        :return:
        '''
        firstDataTime = int(weatherDictList[0]['time'])
        days = 5
        firstDay = True
        firstDayIndex = 0
        morningWeather = []
        morningWeatherSum = {}
        dayTimeWeather = []
        dayTimeWeathersum = {}
        nightWeather = []
        nightWeathersum = {}
        fiveDayWeather = []
        for j in range(days):  # max days
            if firstDay:
                firstDayIndex = int(8 - (firstDataTime / 3))
                toIndex = firstDayIndex
                fromIndex = 0
                firstDay = False
            else:
                toIndex = firstDayIndex + j * 8
                fromIndex = firstDayIndex + (j - 1) * 8

            for i in range(fromIndex, toIndex):
                if int(weatherDictList[i]['time']) <= 6:
                    morningWeather.append(weatherDictList[i])
                elif int(weatherDictList[i]['time']) <= 15:
                    dayTimeWeather.append(weatherDictList[i])
                elif int(weatherDictList[i]['time']) <= 21:
                    nightWeather.append(weatherDictList[i])

            if len(morningWeather) != 0:
                for morning in morningWeather:
                    if len(morningWeatherSum) == 0:
                        morningWeatherSum = morning
                    else:
                        morningWeatherSum = self._createWeatherSumByDayTime(morningWeatherSum, morning)

            if len(dayTimeWeather) != 0:
                for dayly in dayTimeWeather:
                    if len(dayTimeWeathersum) == 0:
                        dayTimeWeathersum = dayly
                    else:
                        dayTimeWeathersum = self._createWeatherSumByDayTime(dayTimeWeathersum, dayly)

            if len(nightWeather) != 0:
                for night in nightWeather:
                    if len(nightWeathersum) == 0:
                        nightWeathersum = night
                    else:
                        nightWeathersum = self._createWeatherSumByDayTime(nightWeathersum, night)

            fiveDayWeather.append(morningWeatherSum)
            fiveDayWeather.append(dayTimeWeathersum)
            fiveDayWeather.append(nightWeathersum)
            morningWeather = []
            morningWeatherSum = {}
            dayTimeWeather = []
            dayTimeWeathersum = {}
            nightWeather = []
            nightWeathersum = {}

        return fiveDayWeather
