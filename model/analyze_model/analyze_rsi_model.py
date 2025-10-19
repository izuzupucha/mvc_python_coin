import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import time
import os
import streamlit as st
from model.base_analyze_model import BaseAnalyzeModel
class AnalyzeRSIModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    # ================= RSI =================#
    def analyze_rsi(self, coin_pair, interval, period=14):
        try:
            df,info = self.data_model.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
            if df.empty:
                return "Không lấy được dữ liệu Binance."

            st.info(f"Tính RSI cho: {coin_pair}, khung: {interval}, chu kỳ: {period} nến")

            close = df["close"]
            delta = close.diff()

            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)

            gain = pd.Series(gain)
            loss = pd.Series(loss)

            # ✅ Dùng RSI (hoặc Wilder’s smoothing) thay vì RSI
            avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            last_rsi = round(rsi.iloc[-1], 2)

            # Gợi ý tín hiệu
            if last_rsi > 70:
                signal = "🔴 RSI cao → có thể quá mua → khả năng đảo chiều giảm."
            elif last_rsi < 30:
                signal = "🟢 RSI thấp → có thể quá bán → khả năng đảo chiều tăng."
            else:
                signal = "⚪ RSI trung tính → thị trường đi ngang."

            return f"RSI hiện tại ({coin_pair}): {last_rsi}\n{signal}"
        except KeyError:
            return "❌ Dữ liệu không hợp lệ — thiếu cột 'close'."
        except Exception as e:
            return f"⚠️ Lỗi khi tính RSI: {e}"            
