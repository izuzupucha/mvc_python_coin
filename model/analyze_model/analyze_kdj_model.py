import os
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import time
from model.base_analyze_model import BaseAnalyzeModel
class AnalyzeKDJModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    #================= KDJ =================#       
    def analyze_kdj(self, coin_pair, interval, period=9, k_smooth=3, d_smooth=3):
        """
        Tính chỉ báo KDJ cho DataFrame nến.
        df: DataFrame phải có cột ['high','low','close']
        period: chu kỳ tính RSV (thường 9)
        k_smooth: làm mịn K (thường 3)
        d_smooth: làm mịn D (thường 3)
        """
        try:
            df,info = self.data_model.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
            if df.empty or not all(col in df.columns for col in ["high", "low", "close"]):
                return "❌ Dữ liệu không hợp lệ — cần cột 'high', 'low', 'close'.", pd.DataFrame()

            high = df["high"]
            low = df["low"]
            close = df["close"]

            # --- 1. Tính RSV (Raw Stochastic Value) ---
            low_min = low.rolling(window=period).min()
            high_max = high.rolling(window=period).max()
            rsv = 100 * (close - low_min) / (high_max - low_min)

            # --- 2. Tính K, D, J ---
            k = rsv.ewm(alpha=1/k_smooth, adjust=False).mean()
            d = k.ewm(alpha=1/d_smooth, adjust=False).mean()
            j = 3 * k - 2 * d

            kdj_df = pd.DataFrame({"K": k, "D": d, "J": j}, index=df.index)

            # --- 3. Phân tích tín hiệu ---
            last_k = k.iloc[-1]
            last_d = d.iloc[-1]
            last_j = j.iloc[-1]

            if last_k > last_d and last_j > last_k:
                signal = "🟢 KDJ cho tín hiệu **mua** (xu hướng tăng)."
            elif last_k < last_d and last_j < last_k:
                signal = "🔴 KDJ cho tín hiệu **bán** (xu hướng giảm)."
            else:
                signal = "⚪ KDJ trung tính → Cần quan sát thêm."

            result = (
                f"**Kết quả KDJ ({len(df)} nến)**\n"
                f"- K hiện tại: {last_k:.2f}\n"
                f"- D hiện tại: {last_d:.2f}\n"
                f"- J hiện tại: {last_j:.2f}\n"
                f"{signal}"
            )
            return result

        except Exception as e:
            return f"⚠️ Lỗi khi tính KDJ: {e}", pd.DataFrame()
