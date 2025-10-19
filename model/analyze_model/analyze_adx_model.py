import os
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import time
from model.base_analyze_model import BaseAnalyzeModel
class AnalyzeADXModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    # ================= ADX =================#
    def analyze_adx(self, coin_pair, interval, period=14):
        """
        Phân tích ADX cho 1 cặp coin.
        Giúp xác định sức mạnh xu hướng và tín hiệu mua/bán.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df,info = self.data_model.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
            if df.empty:
                return "Không lấy được dữ liệu Binance."

            st.info(f"Tính ADX cho: {coin_pair}, khung: {interval}, chu kỳ: {period}")

            high = df["high"]
            low = df["low"]
            close = df["close"]

            # --- 2️. Tính +DM, -DM, TR ---
            up_move = high.diff()
            down_move = low.diff().abs()

            plus_dm = pd.Series(0, index=df.index)
            minus_dm = pd.Series(0, index=df.index)

            plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
            minus_dm[(down_move > up_move) & (down_move > 0)] = down_move

            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # --- 3️. Tính smoothed TR, +DI, -DI ---
            atr = tr.rolling(window=period).mean()
            plus_di = 100 * (plus_dm.rolling(window=period).sum() / atr)
            minus_di = 100 * (minus_dm.rolling(window=period).sum() / atr)

            # --- 4️. Tính DX và ADX ---
            dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
            adx = dx.rolling(window=period).mean()

            # --- 5️. Lấy giá trị cuối cùng ---
            last_adx = adx.iloc[-1]
            last_plus_di = plus_di.iloc[-1]
            last_minus_di = minus_di.iloc[-1]

            # --- 6️. Phân tích tín hiệu cơ bản ---
            if last_adx > 25:
                if last_plus_di > last_minus_di:
                    signal = "🟢 ADX mạnh +DI>−DI → Xu hướng tăng, tín hiệu **mua**."
                else:
                    signal = "🔴 ADX mạnh −DI>+DI → Xu hướng giảm, tín hiệu **bán**."
            else:
                signal = "⚪ ADX < 25 → Xu hướng yếu, thị trường **sideway**."

            # --- 7️. Trả kết quả ---
            result = (
                f"**Kết quả ADX ({coin_pair})**\n"
                f"- +DI: {last_plus_di:.2f}\n"
                f"- -DI: {last_minus_di:.2f}\n"
                f"- ADX: {last_adx:.2f}\n"
                f"{signal}"
            )
            return result

        except KeyError:
            return "❌ Dữ liệu không hợp lệ — thiếu cột 'high', 'low' hoặc 'close'."
        except Exception as e:
            return f"⚠️ Lỗi khi tính ADX: {e}"   
