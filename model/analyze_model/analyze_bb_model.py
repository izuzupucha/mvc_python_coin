import os
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import time
from model.base_analyze_model import BaseAnalyzeModel
class AnalyzeBBModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    # ================= BB =================#    
    def analyze_bb(self, coin_pair, interval, period=20, std_dev=2):
        """
        Phân tích Bollinger Bands cho 1 cặp coin.
        Giúp xác định mức hỗ trợ/kháng cự và biến động giá.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df,info = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
            if df.empty:
                return "Không lấy được dữ liệu Binance."

            st.info(f"Tính Bollinger Bands cho: {coin_pair}, khung: {interval}, period={period}, std_dev={std_dev}")

            close = df["close"]

            # --- 2️. Tính trung bình động SMA ---
            sma = close.rolling(window=period).mean()

            # --- 3️. Tính độ lệch chuẩn ---
            rolling_std = close.rolling(window=period).std()

            # --- 4️. Tính Upper Band và Lower Band ---
            upper_band = sma + std_dev * rolling_std
            lower_band = sma - std_dev * rolling_std

            # --- 5️. Lấy giá trị cuối cùng ---
            last_close = close.iloc[-1]
            last_sma = sma.iloc[-1]
            last_upper = upper_band.iloc[-1]
            last_lower = lower_band.iloc[-1]

            # --- 6️. Phân tích tín hiệu cơ bản ---
            if last_close > last_upper:
                signal = "🔴 Giá vượt Upper Band → có thể quá mua, cân nhắc bán."
            elif last_close < last_lower:
                signal = "🟢 Giá dưới Lower Band → có thể quá bán, cân nhắc mua."
            else:
                signal = "⚪ Giá trong dải Bollinger → thị trường bình thường, quan sát tiếp."

            # --- 7️. Trả kết quả ---
            result = (
                f"**Kết quả Bollinger Bands ({coin_pair})**\n"
                f"- SMA ({period}): {last_sma:.4f}\n"
                f"- Upper Band: {last_upper:.4f}\n"
                f"- Lower Band: {last_lower:.4f}\n"
                f"- Close hiện tại: {last_close:.4f}\n"
                f"{signal}"
            )
            return result

        except KeyError:
            return "❌ Dữ liệu không hợp lệ — thiếu cột 'close'."
        except Exception as e:
            return f"⚠️ Lỗi khi tính Bollinger Bands: {e}"
