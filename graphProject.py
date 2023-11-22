import datetime
import sys

import matplotlib.pyplot as plt
import pandas as pd
import requests



class DataDownload:
    def __init__(self, instrument, api_key, fields, start=None, end=None):
        self._api_key = api_key
        self.baseUrl = "https://api.tiingo.com"
        self.instrument = instrument
        self.start = start
        self.end = end
        self.fields = fields

    def download_data(self):
        """Creating the URL to download data from TIINGO"""
        url = f"{self.baseUrl}/tiingo/daily/{self.instrument.symbolInstrument}/prices?columns={self.fields}&token={self._api_key}"
        if self.start is not None:
            start_str = self.start.strftime("%Y-%m-%d")
            url += f"&startDate={start_str}"
        if self.end is not None:
            end_str = self.end.strftime("%Y-%m-%d")
            url += f"&endDate={end_str}"
        response = requests.get(url)
        if response.status_code == 200:
            data_json = response.json()
            data = pd.DataFrame(data_json)
            data["date"] = data["date"].apply(
                lambda date: datetime.datetime.fromisoformat(date[:-1]).strftime(
                    "%d/%m/%Y"
                )
            )
            data.set_index("date", inplace=True)
            return data
        else:
            print("Error processing the request:", response.status_code)


class Instrument:
    def __init__(self, symbol_instument):
        self.symbolInstrument = symbol_instument


class Technical:
    def __init__(self, prices):
        self.prices = prices
        self.dataIndicator = pd.DataFrame()
        self.auxiliarCalc = pd.DataFrame()
        self.indicatorName = "indicator"

    def moving_average(self):
        window_one = int(input("1- Moving Average window: "))
        window_two = int(input("2- Moving Average window:  "))
        self.indicatorName = "Moving Averages"
        self.dataIndicator["windowOne"] = (
            self.prices["adjClose"].rolling(window=window_one).mean()
        )
        self.dataIndicator["windowTwo"] = (
            self.prices["adjClose"].rolling(window=window_two).mean()
        )

    def bollinger_bands(self):
        self.indicatorName = "Bollinger Bands"
        window_ma = int(input("Add the window for the moving average: "))
        k = int(input("Add how many standard deviations from the moving average: "))
        self.dataIndicator["MiddleBand"] = (
            self.prices["adjClose"].rolling(window=window_ma).mean()
        )
        self.auxiliarCalc["StandarDev"] = (
            self.prices["adjClose"].rolling(window=window_ma).std()
        )
        self.dataIndicator["UperBand"] = (
            self.dataIndicator["MiddleBand"] + k * self.auxiliarCalc["StandarDev"]
        )
        self.dataIndicator["LowerBand"] = (
            self.dataIndicator["MiddleBand"] - k * self.auxiliarCalc["StandarDev"]
        )


class Graph:
    def __init__(self, prices, instrument):
        self.prices = prices
        self.instrument = instrument

    def plot_price(self):
        data = self.prices
        plt.plot(data, label="Price")
        plt.xlabel("Dates")
        plt.title("Graph for " + self.instrument.symbolInstrument)
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_price_technical(self, indicator_data, indicator_name):
        merged_data = pd.merge(
            self.prices, indicator_data, left_index=True, right_index=True
        )
        plt.plot(merged_data["adjClose"], label="Price")
        if indicator_name == "Moving Averages":
            plt.plot(merged_data["windowOne"], label="MA1", linestyle="--")
            plt.plot(merged_data["windowTwo"], label="MA2", linestyle="--")
        elif indicator_name == "Bollinger Bands":
            plt.plot(merged_data["MiddleBand"], label="Middle Band")
            plt.plot(merged_data["UperBand"], label="Upper Band", linestyle="--")
            plt.plot(merged_data["LowerBand"], label="Lower Band", linestyle="--")

        plt.title(
            "Graph for "
            + self.instrument.symbolInstrument
            + " with "
            + indicator_name
            + " calculated."
        )
        plt.xlabel("Dates")
        plt.grid(True)
        plt.legend()
        plt.show()


def main():
    symbol_instrument = input("\nPlease add the Ticker: ")

    instrument_created = Instrument(symbol_instrument)

    start = input("Insert start date in the following format YYYY,MM,DD: ")
    date_parts = start.split(",")
    if len(date_parts) == 3:
        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])

        # Crear un objeto de fecha utilizando los datos ingresados por el usuario
        start_date = datetime.datetime(year, month, day)
    end = input("Insert end date in the following format YYYY,MM,DD: ")
    date_parts = end.split(",")
    if len(date_parts) == 3:
        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])

        # Crear un objeto de fecha utilizando los datos ingresados por el usuario
        end_date = datetime.datetime(year, month, day)
    data_source = DataDownload(
        instrument_created, _api_key, "adjClose", start_date, end_date
    )
    data_downloaded = data_source.download_data()
    technical_indicator = input("Would you like to add any Technical Indicator? (y/n): ")
    if technical_indicator == "y":
        metric_to_add = int(
            input(
                "The options are: \n 1. Two Moving Averages \n 2. Bollinger Bands\n What do you want to add?: "
            )
        )
        technical_object = Technical(data_downloaded)
        if metric_to_add == 1:
            technical_object.moving_average()
        elif metric_to_add == 2:
            technical_object.bollinger_bands()

    else:
        pass

    graph_created = Graph(data_downloaded, instrument_created)
    if technical_indicator == "y":
        graph_created.plot_price_technical(
            technical_object.dataIndicator, technical_object.indicatorName
        )
    elif technical_indicator == "n":
        graph_created.plot_price()

    other_graph = input("Would you like to graph another instrument? (y/n): ")
    if other_graph == "y":
        main()
    else:
        sys.exit()


if __name__ == "__main__":
    _api_key = input("Please add your Tiingo API key: ")
    main()
