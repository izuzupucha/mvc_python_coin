import os
import streamlit as st
from model.base_analyze_model import BaseAnalyzeModel
class AnalyzeEMAModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    #=============== EMA =================#
    def analyze_ema(self, coin_pair, interval, short_period=12, long_period=26):
        """
        Phân tích EMA (Exponential Moving Average) cho 1 cặp coin.
        """
        try:
            df,info = self.data_model.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
            if df.empty:
                return "Không lấy được dữ liệu Binance."

            st.info(f"Tính EMA cho: {coin_pair}, khung: {interval}, chu kỳ: {short_period}/{long_period} nến")

            close = df["close"]

            ema_short = close.ewm(span=short_period, adjust=False).mean()
            ema_long = close.ewm(span=long_period, adjust=False).mean()

            last_ema_short = ema_short.iloc[-1]
            last_ema_long = ema_long.iloc[-1]

            if last_ema_short > last_ema_long:
                signal = "🟢 EMA ngắn cắt lên EMA dài → Tín hiệu **mua** (xu hướng tăng)."
            elif last_ema_short < last_ema_long:
                signal = "🔴 EMA ngắn cắt xuống EMA dài → Tín hiệu **bán** (xu hướng giảm)."
            else:
                signal = "⚪ EMA song song → Thị trường đi ngang."

            result = (
                f"**Kết quả EMA ({coin_pair})**\n"
                f"- EMA {short_period}: {last_ema_short:.2f}\n"
                f"- EMA {long_period}: {last_ema_long:.2f}\n"
                f"{signal}"
            )
            return result

        except KeyError:
            return "❌ Dữ liệu không hợp lệ — thiếu cột 'close'."
        except Exception as e:
            return f"⚠️ Lỗi khi tính EMA: {e}"