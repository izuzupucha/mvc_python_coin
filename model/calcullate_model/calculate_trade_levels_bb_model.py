import os
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import time
from model.get_data_model import GetDataModel
from model.base_analyze_model import BaseAnalyzeModel
class CalculateTradeLevelsBBModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    #======Tính toán Entry / Stoploss / TakeProfit dựa theo Bollinger Bands========#
    def calculate_trade_levels_bb(self, symbol, interval, direction="long", period=20, mult=2):
        """
        Tính toán Entry / Stoploss / TakeProfit dựa theo Bollinger Bands.
        """
        try:
            df = self.data_model.get_klines_binance(symbol=symbol, interval=interval, limit=period + 5)
            if df.empty:
                return None

            df["ma"] = df["close"].rolling(period).mean()
            df["std"] = df["close"].rolling(period).std()
            df["upper"] = df["ma"] + mult * df["std"]
            df["lower"] = df["ma"] - mult * df["std"]

            last = df.iloc[-1]
            entry = last["close"]

            if direction == "long":
                stoploss = last["lower"]
                takeprofit = entry + (entry - stoploss) * 1.5
            else:
                stoploss = last["upper"]
                takeprofit = entry - (stoploss - entry) * 1.5

            return {
                "symbol": symbol,
                "interval": interval,
                "direction": direction,
                "entry": round(entry, 4),
                "stoploss": round(stoploss, 4),
                "takeprofit": round(takeprofit, 4),
                "bb_upper": round(last["upper"], 4),
                "bb_lower": round(last["lower"], 4),
                "timestamp": pd.Timestamp.now()
            }
        except Exception as e:
            st.error(f"Lỗi tính Bollinger SL/TP: {e}")
            return None

model = CoinModel()
print(dir(model))
