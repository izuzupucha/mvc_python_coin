import os
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import time
from model.base_analyze_model import BaseAnalyzeModel
class AnalyzeOBVModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    #================= OBV =================#        
    def analyze_obv(self, coin_pair, interval, period=14):
        """
        Tính OBV (On-Balance Volume) và phân tích xác nhận Volume.
        df: DataFrame phải có cột ['close', 'volume']
        """
        try:
            df,info = self.data_model.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
            if df.empty or "close" not in df or "volume" not in df:
                return "❌ Dữ liệu không hợp lệ — cần cột 'close' và 'volume'."

            close = df["close"]
            volume = df["volume"]

            # --- Tính OBV ---
            obv = pd.Series(index=df.index, dtype=float)
            obv.iloc[0] = 0  # OBV ban đầu

            for i in range(1, len(df)):
                if close.iloc[i] > close.iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
                elif close.iloc[i] < close.iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
                else:
                    obv.iloc[i] = obv.iloc[i-1]

            # --- Tín hiệu cơ bản ---
            last_close = close.iloc[-1]
            last_obv = obv.iloc[-1]
            last_volume = volume.iloc[-1]
            prev_close = close.iloc[-2]
            prev_obv = obv.iloc[-2]

            # Xác nhận xu hướng tăng/giảm
            if last_close > prev_close and last_obv > prev_obv:
                signal = "🟢 Giá tăng + OBV tăng → Xu hướng tăng, tín hiệu mua."
            elif last_close < prev_close and last_obv < prev_obv:
                signal = "🔴 Giá giảm + OBV giảm → Xu hướng giảm, tín hiệu bán."
            else:
                signal = "⚪ Không đồng bộ giữa giá và OBV → Cần quan sát thêm."

            # Kết quả
            result = (
                f"**Kết quả OBV/Volume ({len(df)} nến)**\n"
                f"- Close hiện tại: {last_close:.4f}\n"
                f"- Volume hiện tại: {last_volume:.4f}\n"
                f"- OBV hiện tại: {last_obv:.4f}\n"
                f"{signal}"
            )

            return result

        except Exception as e:
            return f"⚠️ Lỗi khi tính OBV: {e}", pd.Series()      
