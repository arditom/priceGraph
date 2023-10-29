import requests
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class DataDownload:
    #This class will be used to backtest
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
            data['date'] = data['date'].apply(lambda fecha: datetime.datetime.fromisoformat(fecha[:-1]).strftime("%d/%m/%Y"))
            data.set_index('date', inplace=True)
            return data
        else:
            print('Error al realizar la solicitud:', response.status_code)

#End Class

class Instrument:
    def __init__(self,symbolInstrument):
        self.symbolInstrument = symbolInstrument



class Returns:
    def __init__(self,period,dataDescargada):
        self.period = period
        self.dataDescargada = dataDescargada
        self.returns = None
        self.cumReturns = None

    def calculateReturns(self):
        data = self.dataDescargada
        retornos = np.log(data/data.shift(self.period))
        retornos.dropna(inplace=True)
        self.returns = retornos
        return retornos

    def cumulativeReturns(self):
        data = self.returns
        cumulative_data  = data.cumsum().apply(np.exp)
        self.cumReturns = cumulative_data
        return cumulative_data.squeeze()

class Technical:
    def __init__(self,prices):
        self.prices = prices
        self.movingAverages = pd.DataFrame()
    def movingAverage(self):
        windowOne = int(input("1- Moving Average window: "))
        windowTwo = int(input("2- Moving Average window:  "))
        self.movingAverages['windowOne'] = self.prices['adjClose'].rolling(window=windowOne).mean()
        self.movingAverages['windowTwo'] = self.prices['adjClose'].rolling(window=windowTwo).mean()


class Grafico:
    def __init__(self,returns,instrumento,ma):
        self.returns = returns
        self.instrumento = instrumento
        self.ma = ma
    def plot(self):
        data = self.returns
        movingAverage = self.ma
        plt.plot(data)
        plt.plot(movingAverage)
        #plt.ylabel('Cumulative Returns')
        plt.xlabel('Dates')
        plt.title('Graph for ' + self.instrumento.symbolInstrument)
        plt.show()

if __name__ == "__main__":
        apiKey = input("Please add your Tiingo API key: ")
        symbolInstrument = input("Please add the Ticker: ")

        instrumento = Instrument(symbolInstrument)

        start =  input("Insert start date in the following format YYYY,MM,DD: ")
        fecha_parts = start.split(',')
        if len(fecha_parts) == 3:
            year = int(fecha_parts[0])
            month = int(fecha_parts[1])
            day = int(fecha_parts[2])

            # Crear un objeto de fecha utilizando los datos ingresados por el usuario
            startDate = datetime.datetime(year, month, day)
        end =  input("Insert end date in the following format YYYY,MM,DD: ")
        fecha_parts = end.split(',')
        if len(fecha_parts) == 3:
            year = int(fecha_parts[0])
            month = int(fecha_parts[1])
            day = int(fecha_parts[2])

            # Crear un objeto de fecha utilizando los datos ingresados por el usuario
            endDate = datetime.datetime(year, month, day)
        dataSource = DataDownload(instrumento,apiKey,'adjClose',startDate,endDate)
        periodo = int(input("What returns frequency would you like?: "))
        dataDescargada = dataSource.downloadData()
        retornos = Returns(periodo,dataDescargada)
        retornos.calculateReturns()
        mediaMovil = Technical(dataDescargada)
        mediaMovil.movingAverage()
        grafico = Grafico(retornos.dataDescargada,instrumento,mediaMovil.movingAverages)
        grafico.plot()
