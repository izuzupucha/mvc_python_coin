import os
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import time
from model.get_data_model import GetDataModel
from model.base_analyze_model import BaseAnalyzeModel
class CalculateTradeLevelsAtrModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    #====Tính toán Entry / Stoploss / TakeProfit dựa theo ATR.=====#
    def calculate_trade_levels_atr(self, symbol, interval, direction="long", atr_period=14, atr_mult_sl=1.0, rr_ratio=1.5):
        """
        Tính toán Entry / Stoploss / TakeProfit dựa theo ATR.
        - atr_period: số nến dùng để tính ATR
        - atr_mult_sl: hệ số nhân ATR cho stoploss
        - rr_ratio: tỉ lệ RR (takeprofit = stop_distance * rr_ratio)
        """
        try:
            df,_ = self.data_model.get_klines_binance(symbol=symbol, interval=interval, limit=atr_period + 2)
            if df.empty:
                return None

            # --- Tính ATR ---
            high = df["high"]
            low = df["low"]
            close = df["close"]
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(atr_period).mean().iloc[-1]

            entry = close.iloc[-1]
            if direction == "long":
                stoploss = entry - atr * atr_mult_sl
                takeprofit = entry + (atr * atr_mult_sl * rr_ratio)
            else:
                stoploss = entry + atr * atr_mult_sl
                takeprofit = entry - (atr * atr_mult_sl * rr_ratio)

            return {
                "symbol": symbol,
                "interval": interval,
                "direction": direction,
                "entry": round(entry, 4),
                "stoploss": round(stoploss, 4),
                "takeprofit": round(takeprofit, 4),
                "atr_value": round(atr, 4),
                "timestamp": pd.Timestamp.now()
            }
        except Exception as e:
            st.error(f"Lỗi tính ATR SL/TP: {e}")
            return None
