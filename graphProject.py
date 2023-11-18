import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import sys

class DataDownload:
    def __init__(self,instrument,apiKey,fields,start=None,end=None):
        self.apiKey = apiKey
        self.baseUrl = 'https://api.tiingo.com'
        self.instrument = instrument
        self.start = start
        self.end = end
        self.fields = fields
    def downloadData(self):
        '''
        Creating the URL to download data from TIINGO
        '''
        url = f'{self.baseUrl}/tiingo/daily/{self.instrument.symbolInstrument}/prices?columns={self.fields}&token={self.apiKey}'
        if self.start is not None:
            startStr = self.start.strftime('%Y-%m-%d')
            url += f'&startDate={startStr}'
        if self.end is not None:
            endStr = self.end.strftime('%Y-%m-%d')
            url += f'&endDate={endStr}'
        response = requests.get(url)
        if response.status_code == 200:
            data_json = response.json()
            data = pd.DataFrame(data_json)
            data['date'] = data['date'].apply(lambda date: datetime.datetime.fromisoformat(date[:-1]).strftime("%d/%m/%Y"))
            data.set_index('date', inplace=True)
            return data
        else:
            print('Error processing the request:', response.status_code)
class Instrument:
    def __init__(self,symbolInstrument):
        self.symbolInstrument = symbolInstrument
class Technical:
    def __init__(self,prices):
        self.prices = prices
        self.dataIndicator = pd.DataFrame()
        self.auxiliarCalc = pd.DataFrame()
        self.indicatorName = "indicator"
    def movingAverage(self):
        windowOne = int(input("1- Moving Average window: "))
        windowTwo = int(input("2- Moving Average window:  "))
        self.indicatorName = "Moving Averages"
        self.dataIndicator['windowOne'] = self.prices['adjClose'].rolling(window=windowOne).mean()
        self.dataIndicator['windowTwo'] = self.prices['adjClose'].rolling(window=windowTwo).mean()
    def bollingerBands(self):
        self.indicatorName = "Bollinger Bands"
        windowMA = int(input('Add the window for the moving average: '))
        k = int(input('Add how many standard deviations from the moving average: '))
        self.dataIndicator['MiddleBand'] = self.prices['adjClose'].rolling(window=windowMA).mean()
        self.auxiliarCalc['StandarDev'] = self.prices['adjClose'].rolling(window=windowMA).std()
        self.dataIndicator['UperBand'] = self.dataIndicator['MiddleBand'] + k * self.auxiliarCalc['StandarDev']
        self.dataIndicator['LowerBand'] = self.dataIndicator['MiddleBand'] - k * self.auxiliarCalc['StandarDev']

class Graph:
    def __init__(self,prices,instrument):
        self.prices = prices
        self.instrument = instrument

    def plotPrice(self):
        data = self.prices
        plt.plot(data, label='Price')
        plt.xlabel('Dates')
        plt.title('Graph for ' + self.instrument.symbolInstrument)
        plt.grid(True)
        plt.legend()
        plt.show()

    def plotPriceTechnical(self, indicatorData, indicatorName):
        merged_data = pd.merge(self.prices, indicatorData, left_index=True, right_index=True)
        plt.plot(merged_data['adjClose'], label='Price')
        if indicatorName == "Moving Averages":
            plt.plot(merged_data['windowOne'], label='MA1', linestyle='--')
            plt.plot(merged_data['windowTwo'], label='MA2', linestyle='--')
        elif indicatorName == "Bollinger Bands":
            plt.plot(merged_data['MiddleBand'], label='Middle Band')
            plt.plot(merged_data['UperBand'], label='Upper Band', linestyle='--')
            plt.plot(merged_data['LowerBand'], label='Lower Band', linestyle='--')

        plt.title('Graph for ' + self.instrument.symbolInstrument + ' with ' + indicatorName + ' calculated.')
        plt.xlabel('Dates')
        plt.grid(True)
        plt.legend()
        plt.show()

def main():
    global apiKey
    symbolInstrument = input("\nPlease add the Ticker: ")

    instrumentCreated = Instrument(symbolInstrument)

    start =  input("Insert start date in the following format YYYY,MM,DD: ")
    date_parts = start.split(',')
    if len(date_parts) == 3:
        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])

        # Crear un objeto de fecha utilizando los datos ingresados por el usuario
        startDate = datetime.datetime(year, month, day)
    end =  input("Insert end date in the following format YYYY,MM,DD: ")
    date_parts = end.split(',')
    if len(date_parts) == 3:
        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])

        # Crear un objeto de fecha utilizando los datos ingresados por el usuario
        endDate = datetime.datetime(year, month, day)
    dataSource = DataDownload(instrumentCreated,apiKey,'adjClose',startDate,endDate)
    dataDownloaded = dataSource.downloadData()
    technicalIndicator = input("Would you like to add any Technical Indicator? (y/n): ")
    if technicalIndicator == 'y':
        metricToAdd = int(input("The options are: \n 1. Two Moving Averages \n 2. Bollinger Bands\n What do you want to add?: "))
        technicalObject = Technical(dataDownloaded)
        if metricToAdd == 1:
            technicalObject.movingAverage()
        elif metricToAdd == 2:
            technicalObject.bollingerBands()

    else:
        pass

    graphCreated = Graph(dataDownloaded,instrumentCreated)
    if technicalIndicator == 'y':
        graphCreated.plotPriceTechnical(technicalObject.dataIndicator,technicalObject.indicatorName)
    elif technicalIndicator == 'n':
        graphCreated.plotPrice()

    otherGraph = input("Would you like to graph another instrument? (y/n): ")
    if otherGraph == 'y':
        main()
    else:
        sys.exit()

if __name__ == "__main__":
    apiFlag = 'n'
    apiKey = input("Please add your Tiingo API key: ")
    main()
