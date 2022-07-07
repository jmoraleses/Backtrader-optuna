# -*- coding: utf-8 -*-

# !pip install backtrader
# !pip install optuna
# !pip install optunity
# !pip install backtrader_plotting
# !pip install requests
# !pip install dask-optuna
# !pip install pandas
# !pip install --upgrade sqlalchemy

from __future__ import (absolute_import, division, print_function, unicode_literals)
import argparse
import datetime as dt
import decimal
import json
import time
from functools import partial
import backtrader as bt
import backtrader.feeds as btfeed
import numpy as np
import optunity.metrics
import pandas as pd
import requests
import matplotlib
from backtrader_plotting import Bokeh, OptBrowser
from backtrader_plotting.schemes import Tradimo
import optunity
import pickle
import os.path
import tkinter
import optuna as optuna
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from optuna import Trial
from optuna.multi_objective import trial
from optunity import maximize
from optunity.solvers import GridSearch
import dask_optuna
import joblib

optuna.logging.set_verbosity(optuna.logging.WARNING)



client = Client(api_key, api_secret)


def parse_args():
    parser = argparse.ArgumentParser(description='CCXT Market')

    parser.add_argument('-s', '--symbol',
                        type=str,
                        required=True,
                        help='The Symbol of the Instrument/Currency Pair To Download')

    parser.add_argument('-e', '--exchange',
                        type=str,
                        required=False,
                        help='The exchange to download from')

    parser.add_argument('-t', '--timeframe',
                        type=str,
                        required=False,
                        default='1m',
                        choices=['1m', '3m', '5m', '15m', '30m', '45m', '1h', '2h', '3h', '4h', '6h', '12h', '1d', '1M',
                                 '1s', '5s', '30s', '1y'],
                        help='The timeframe to download')

    parser.add_argument('-hora', '--horadecomienzo',
                        type=str,
                        required=True,
                        default='20/07/2021 00:00:00"',
                        help='Hour begin "02/05/2021 22:00:00"')

    parser.add_argument('-a', '--apikey',
                        type=str,
                        required=False,
                        help='The exchange api key')

    parser.add_argument('-k', '--secretkey',
                        type=str,
                        required=False,
                        help='The exchange secret key')

    parser.add_argument('-cash', '--cash',
                        type=float,
                        required=False,
                        default=100.0,
                        help='The exchange secret key')

    parser.add_argument('-cycle', '--cycle',
                        type=int,
                        required=False,
                        default=100,
                        help='The exchange secret key')

    parser.add_argument('--debug',
                        action='store_true',
                        help='Print Sizer Debugs')

    return parser.parse_args()


def timeFrame(tf):

    if tf == '1mth':
        compression = 1
        timeframe = bt.TimeFrame.Months
    elif tf == '1s':
        compression = 1
        timeframe = bt.TimeFrame.Seconds
    elif tf == '5s':
        compression = 5
        timeframe = bt.TimeFrame.Seconds
    elif tf == '30s':
        compression = 30
        timeframe = bt.TimeFrame.Seconds
    elif tf == '1m':
        compression = 1
        timeframe = bt.TimeFrame.Minutes
    elif tf == '45m':
        compression = 45
        timeframe = bt.TimeFrame.Minutes
    elif tf == '12h':
        compression = 720
        timeframe = bt.TimeFrame.Minutes
    elif tf == '15m':
        compression = 15
        timeframe = bt.TimeFrame.Minutes
    elif tf == '30m':
        compression = 30
        timeframe = bt.TimeFrame.Minutes
    elif tf == '1d':
        compression = 1
        timeframe = bt.TimeFrame.Days
    elif tf == '1h':
        compression = 60
        timeframe = bt.TimeFrame.Minutes
    elif tf == '3m':
        compression = 3
        timeframe = bt.TimeFrame.Minutes
    elif tf == '2h':
        compression = 120
        timeframe = bt.TimeFrame.Minutes
    elif tf == '3d':
        compression = 3
        timeframe = bt.TimeFrame.Days
    elif tf == '1w':
        compression = 1
        timeframe = bt.TimeFrame.Weeks
    elif tf == '3h':
        compression = 180
        timeframe = bt.TimeFrame.Minutes
    elif tf == '180m':
        compression = 180
        timeframe = bt.TimeFrame.Minutes
    elif tf == '4h':
        compression = 240
        timeframe = bt.TimeFrame.Minutes
    elif tf == '5m':
        compression = 5
        timeframe = bt.TimeFrame.Minutes
    elif tf == '6h':
        compression = 360
        timeframe = bt.TimeFrame.Minutes
    elif tf == '8h':
        compression = 480
        timeframe = bt.TimeFrame.Minutes
    elif tf == '12h':
        compression = 720
        timeframe = bt.TimeFrame.Minutes
    else:
        print('dataframe not recognized')
        exit()

    return compression, timeframe

def interval_klines(tf):
    if tf == '1mth':
        return Client.KLINE_INTERVAL_1MONTH
    elif tf == '1m':
        return Client.KLINE_INTERVAL_1MINUTE
    elif tf == '12h':
        return Client.KLINE_INTERVAL_12HOUR
    elif tf == '15m':
        return Client.KLINE_INTERVAL_15MINUTE
    elif tf == '30m':
        return Client.KLINE_INTERVAL_30MINUTE
    elif tf == '1d':
        return Client.KLINE_INTERVAL_1DAY
    elif tf == '1h':
        return Client.KLINE_INTERVAL_1HOUR
    elif tf == '3m':
        return Client.KLINE_INTERVAL_3MINUTE
    elif tf == '2h':
        return Client.KLINE_INTERVAL_2HOUR
    elif tf == '3d':
        return Client.KLINE_INTERVAL_3DAY
    elif tf == '1w':
        return Client.KLINE_INTERVAL_1WEEK
    elif tf == '4h':
        return Client.KLINE_INTERVAL_4HOUR
    elif tf == '5m':
        return Client.KLINE_INTERVAL_5MINUTE
    elif tf == '6h':
        return Client.KLINE_INTERVAL_6HOUR
    elif tf == '8h':
        return Client.KLINE_INTERVAL_8HOUR
    elif tf == '12h':
        return Client.KLINE_INTERVAL_12HOUR
    else:
        print('dataframe not recognized')
        exit()


def get_binance_bars(symbol_data, interval, starttime, endtime):
    url = "https://api.binance.com/api/v3/klines"

    starttime = str(int(starttime.timestamp() * 1000))
    endtime = str(int(endtime.timestamp() * 1000))
    limit = '1000'

    # req_params = {"symbol": symbol_data, 'interval': interval, 'startTime': starttime, 'endTime': endtime,
    #               'limit': limit}
    #
    # df_data = pd.DataFrame(json.loads(requests.get(url, params=req_params).text))


    klines = client.get_historical_klines(symbol_data, interval_klines(interval), starttime, endtime)

    if len(klines) == 0:
        return None

    df_data = pd.DataFrame(klines)

    if len(df_data.index) == 0:
        return None

    df_data = df_data.iloc[:, 0:6]
    df_data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']

    df_data.open = df_data.open.astype("float")
    df_data.high = df_data.high.astype("float")
    df_data.low = df_data.low.astype("float")
    df_data.close = df_data.close.astype("float")
    df_data.volume = df_data.volume.astype("float")

    df_data['adj_close'] = df_data['close']

    df_data.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df_data.datetime]

    return df_data


def round_down(value, decimals):
    with decimal.localcontext() as ctx:
        d = decimal.Decimal(value)
        ctx.rounding = decimal.ROUND_FLOOR
        return round(d, decimals)


class Bits(bt.Strategy):
    params = (
        ('perprofitA', 1),
        # ('perlostA', 1),
        ('pausaconst', 5),
        ('perprofitB', 1),
        # ('perlostB', 1),
    )

    def __init__(self):
        self.porcentajeBeneficioA = self.params.perprofitA
        # self.porcentajePerdidaA = self.params.perlostA
        self.pausaconstante = self.params.pausaconst
        self.porcentajeBeneficioB = self.params.perprofitB
        # self.porcentajePerdidaB = self.params.perlostB
        # self.pausaconstante = 0
        self.order = None
        self.resultadoTendencia = bt.ind.EMA(period=int(self.pausaconstante))
        # self.ma_fast = bt.ind.EMA(period=int(self.params.fast))
        # self.ma_slow = bt.ind.EMA(period=int(self.params.slow))
        # self.crossover = bt.ind.CrossOver(self.ma_fast, self.ma_slow)
        self.prevClose = 1.0
        self.euros = 1.0
        self.coins = self.euros
        self.precioBit = self.broker.get_value() / self.prevClose
        self.y = self.precioBit
        self.tendenciaBajista = False
        self.short = False
        self.long = False
        self.empieza = True
        self.price = 1.0
        self.longTakeprofit = self.data.open[0] * (self.porcentajeBeneficioA)
        # self.longStoploss = self.data.open[0] * (self.porcentajePerdidaA)
        self.shortTakeprofit = self.data.open[0] * (self.porcentajeBeneficioB) #B
        # self.shortStoploss = self.data.open[0] * (self.porcentajePerdidaB) #B
        # self.btc = 0.0 #self.coins
        self.eur = 0.0
        self.abierto = False
        self.pausa = 0
        # self.capital = 100.0
        self.capital_bits = 0.0
        self.prevCloseAnt = 0.0
        global last_datetime_format
        global precioactual

    def next(self):
        self.prevClose = self.data.open[0]
        self.auxdatetime = dt.datetime.strptime(last_datetime_format, '%d-%m-%Y %H:%M:%S')
        self.nowdatetime = dt.datetime.strptime(self.data.datetime.datetime().strftime('%d-%m-%Y %H:%M:%S'),
                                                '%d-%m-%Y %H:%M:%S')

        # self.resultadoTendencia = bt.ind.EMA(period=int(self.pausaconstante))
        if self.nowdatetime > self.auxdatetime:

            # if self.abierto is False:
            self.capital_bits = self.broker.get_cash() / self.data.open[0]

            # if self.abierto is False and self.prevClose <= self.shortTakeprofit:
            #     self.abierto = False

            #si el precio en 50 velas anteriores es mayor, es que está a la baja, y por tanto
            if self.pausa >= self.pausaconstante:
                if self.resultadoTendencia > self.data.open[0]:
                    self.tendenciaBajista = True
                else:
                    self.tendenciaBajista = False

                if self.tendenciaBajista is True and self.abierto is True:  # and self.pausa >= self.pausaconstante:
                    self.pausa = 0
                    self.y = self.broker.get_cash() / self.data.open[0]
                    self.close(exectype=bt.Order.Market, size=self.y)
                    self.y = self.broker.get_cash() / self.data.open[0]
                    self.order = self.sell(size=self.y, price=self.data.open[0])
                    self.shortTakeprofit = self.prevClose * (self.porcentajeBeneficioB)  # B
                    if self.abierto is False:
                        self.abierto = True
                    else:
                        self.abierto = False

                elif self.tendenciaBajista is False and self.abierto is False:  # and self.pausa >= self.pausaconstante:
                    self.pausa = 0
                    self.y = self.broker.get_cash() / self.data.open[0]
                    self.close(exectype=bt.Order.Market, size=self.y)
                    self.y = self.broker.get_cash() / self.data.open[0]
                    self.order = self.buy(size=self.y, price=self.data.open[0])
                    self.longTakeprofit = self.prevClose * (self.porcentajeBeneficioA)
                    if self.abierto is False:
                        self.abierto = True
                    else:
                        self.abierto = False
                    # self.begin = True

                ###

            # if ((self.prevClose <= self.shortTakeprofit or self.prevClose >= self.shortStoploss) and self.abierto is False) or self.empieza is True:
            if ((self.prevClose <= self.shortTakeprofit and self.abierto is False) or (self.tendenciaBajista is True and self.pausa > 50)) or self.empieza is True:
                self.longTakeprofit = self.prevClose * (self.porcentajeBeneficioA)
                # self.longStoploss = self.prevClose * (self.porcentajePerdidaA)
                self.y = self.broker.get_cash() / self.data.open[0]
                self.order = self.buy(size=self.y, price=self.data.open[0])
                self.empieza = False
                self.abierto = True
                self.pausa = 0

                # if self.prevClose >= self.shortStoploss:
                #     self.capital_bits = self.capital_bits - (self.capital_bits * abs(self.prevClose - self.prevCloseAnt))
                #
                # if self.prevClose <= self.shortTakeprofit:
                #     self.capital_bits = self.capital_bits + (self.capital_bits * abs(self.prevClose - self.prevCloseAnt))

            # if ((self.prevClose >= self.longTakeprofit or self.prevClose <= self.longStoploss) and self.abierto is True) and self.empieza is False and self.pausa <= 0:
            if ((self.prevClose >= self.longTakeprofit and self.abierto is True) and self.empieza is False) or (self.tendenciaBajista is False and self.pausa > 50): # and self.pausa <= 0:
                self.shortTakeprofit = self.prevClose * (self.porcentajeBeneficioB) #B
                # self.shortStoploss = self.prevClose * (self.porcentajePerdidaB) #B
                self.y = self.broker.get_cash() / self.data.open[0]
                self.order = self.sell(size=self.y, price=self.data.open[0])
                self.abierto = False
                self.prevCloseAnt = self.prevClose
                self.pausa = 0

            self.pausa = self.pausa + 1

            ####




    def stop(self):
        global precioactual
        self.order = self.close()
        precioactual = self.prevClose
        # calculate the actual returns
        # print('Ganancias :{:.2f}'.format(self.broker.get_value()))
        print('value: {}, cash: {}'.format(str(self.broker.get_value()), str(self.broker.get_cash())))
        print('pbeneficioA: {}, pbeneficioB: {}, pausa: {}, Capital Bits: {}\n'.format(self.porcentajeBeneficioA, self.porcentajeBeneficioB, self.pausaconstante, self.capital_bits)) # , self.porcentajePerdidaA, self.porcentajePerdidaB
        # return self.capital_bits

    # def getvalue(self, datas=None):
    # #     """ Broker value = Cash + Value of the open positions
    # #         https://community.backtrader.com/topic/1178/how-is-the-value-calculated/4
    # #     """
    # #     # if datas:
    # #     #     # Return the value of open positions (@last price) plus cash.
    # #     #     # Using Total cash here, as that represents account value accurately.
    # #     #     return (self.getposition(datas[0]).size * datas[0].close[0]) + self.wallet_balance["total"]
    # #     # else:
    # #     #     # Return the wallet total
    # #     #     return self.wallet_balance["total"]
    #     return self.capital_bits

cash = 1
datos = 1
precioactual = 1.0
def opt_objective(trial):
    global datos
    global cash
    global precioactual

    perprofitA = trial.suggest_float('perprofitA', 1.00, 1.25)
    # perlostA = trial.suggest_float('perlostA', 1.0, 2.0)
    pausaconst = trial.suggest_int('pausaconst', 1, 10)
    perprofitB = trial.suggest_float('perprofitB', 0.90, 1.00)
    # perlostB = trial.suggest_float('perlostB', 1.0, 2.0)

    cerebro = bt.Cerebro()
    cerebro.broker.set_coc(True)
    cerebro.broker.set_coo(True)
    cerebro.broker.setcash(cash=cash)
    # cerebro.addwriter(bt.WriterFile, out='analisis.txt')
    # cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    cerebro.addstrategy(Bits, perprofitA=perprofitA, perprofitB=perprofitB, pausaconst=pausaconst) # , perlostA=perlostA, perlostB=perlostB)
    cerebro.adddata(datos)
    cerebro.run()
    return float(cerebro.broker.get_value())


if __name__ == '__main__':

    # Pasando argumento
    # -s CAKE/BUSD -hora "02/01/2021 00:00:00" -cash 70.0 -t 4h -cycle 100
    args = parse_args()
    horadecomienzo = str(args.horadecomienzo)
    symbol = str(args.symbol)
    cash = float(args.cash)
    timeframe = str(args.timeframe)
    cycle = int(args.cycle)
    # horadecomienzo = str("02/01/2021 00:00:00")
    # symbol = str("CAKE/BUSD")
    # cash = float(70.0)
    # timeframe = str("4h")
    # cycle = 100

    exchange = str("binance")
    horadecomienzo = horadecomienzo.replace("/", "-")
    simbolos = symbol.split(sep='/')
    first_symbol = simbolos[0]
    second_symbol = simbolos[1]
    symbol_out = symbol.replace("/", "")
    filename = '{}-{}.csv'.format(symbol_out, timeframe)

    # Tiempo
    # last_date = dt.datetime(2021, 1, 10, 0, 0, 0)
    last_date = dt.datetime.strptime(horadecomienzo, '%d-%m-%Y %H:%M:%S') - dt.timedelta(days=1)
    last_datetime_ticker = dt.datetime.strptime(last_date.strftime('%d-%m-%Y %H:%M:%S'),
                                                '%d-%m-%Y %H:%M:%S')  # (2021, 1, 13)
    last_datetime = dt.datetime.strptime(horadecomienzo, '%d-%m-%Y %H:%M:%S')
    last_datetime_format = last_datetime.strftime('%d-%m-%Y %H:%M:%S')
    time_actual_ticker = dt.datetime.now()  # dt.datetime(2021, 7, 23)
    time_actual = dt.datetime.now().date()  # dt.datetime(2021, 7, 23)

    # intervalos = ['1d', '12h', '3h', '2h', '1h', '30m', '15m', '5m', '3m', '1m']
    resultados = []
    resultadosOpt = []
    i = timeframe
    # for i in intervalos:

    # Recuperar los valores de la gráfica desde binance y guardarlos en el csv
    if not os.path.isfile(filename):
        df_list = []
        while True:
            new_df = get_binance_bars(symbol_out, i, last_datetime_ticker, time_actual_ticker)  # timeframe

            if new_df is None:
                break
            df_list.append(new_df)
            last_datetime_ticker = max(new_df.index) + dt.timedelta(0, 1)
        df = pd.concat(df_list)
        df.columns
        # data = bt.feeds.PandasData(dataname=df)
        df.to_csv(filename)
        df = pd.read_csv(filename, sep=',', header=0,
                         names=['time', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'adj_close'],
                         low_memory=False)
        df.to_csv(filename)

    # time.sleep(5)
    print('Intervalo: {}'.format(i))
    # print('Intervalo: {}'.format(timeframe))

    # timeframe y compresión
    compression_actual, timeframe_actual = timeFrame(i)  # (timeframe)

    # Cargar csv
    data = btfeed.GenericCSVData(
        dataname=filename,
        fromdate=last_datetime_ticker,
        todate=time_actual,
        nullvalue=0.0,
        dtformat='%Y-%m-%d %H:%M:%S',
        datetime=1,
        open=3,
        high=4,
        low=5,
        close=6,
        volume=7,
        adj_close=8,
        openinterest=-1,
        timeframe=timeframe_actual,
        compression=compression_actual,
    )
    datos = data

    # print('precio actual: {}'.format(precioactual))
    ######

    # optuna
    study = optuna.create_study(direction="maximize")
    study.optimize(opt_objective, n_trials=cycle)

    # print(study.best_params)
    parametros_optimos = study.best_params
    trial = study.best_trial
    print('Saldo máximo: {}'.format(trial.value))
    print(parametros_optimos)
    print()