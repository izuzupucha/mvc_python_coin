import os
import streamlit as st
from model.base_analyze_model import BaseAnalyzeModel
class AnalyzeMACDModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    # ================= MACD =================        
    def analyze_macd(self, coin_pair, interval, short_period=12, long_period=26, signal_period=9):
        """
        Phân tích MACD (Moving Average Convergence Divergence)
        giúp xác định sức mạnh, hướng và thời điểm đảo chiều xu hướng.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df,info = self.data_model.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
            if df.empty:
                return "Không lấy được dữ liệu Binance."

            st.info(f"Tính MACD cho: {coin_pair}, khung: {interval}, chu kỳ: {short_period}/{long_period}/{signal_period} nến")

            close = df["close"]

            # --- 2️. Tính đường EMA ngắn và EMA dài ---
            ema_short = close.ewm(span=short_period, adjust=False).mean()
            ema_long = close.ewm(span=long_period, adjust=False).mean()

            # --- 3️. Tính MACD line ---
            macd_line = ema_short - ema_long

            # --- 4️. Tính đường tín hiệu (Signal line) ---
            signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

            # --- 5️. Tính Histogram (độ chênh lệch giữa MACD và Signal) ---
            histogram = macd_line - signal_line

            # --- 6️. Lấy giá trị cuối cùng ---
            last_macd = macd_line.iloc[-1]
            last_signal = signal_line.iloc[-1]
            last_hist = histogram.iloc[-1]

            # --- 7️. Phân tích tín hiệu MACD ---
            if last_macd > last_signal and last_hist > 0:
                signal = "🟢 MACD cắt lên Signal → Xu hướng **tăng**, tín hiệu **mua**."
            elif last_macd < last_signal and last_hist < 0:
                signal = "🔴 MACD cắt xuống Signal → Xu hướng **giảm**, tín hiệu **bán**."
            else:
                signal = "⚪ MACD đang đi ngang → Thị trường **sideway**, nên quan sát thêm."

            # --- 8️. Trả kết quả ---
            result = (
                f"**Kết quả MACD ({coin_pair})**\n"
                f"- MACD line: {last_macd:.4f}\n"
                f"- Signal line: {last_signal:.4f}\n"
                f"- Histogram: {last_hist:.4f}\n"
                f"{signal}"
            )
            return result

        except KeyError:
            return "❌ Dữ liệu không hợp lệ — thiếu cột 'close'."
        except Exception as e:
            return f"⚠️ Lỗi khi tính MACD: {e}"