import os
import streamlit as st
from model.base_analyze_model import BaseAnalyzeModel
class AnalyzeICModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    # ================= ichimoku =================
    def analyze_ic(self, coin_pair, interval):
        """
        Phân tích Ichimoku Cloud cho 1 cặp coin.
        Giúp xác định xu hướng, hỗ trợ/kháng cự và tín hiệu mua/bán.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df,info = self.data_model.get_klines_binance(symbol=coin_pair, interval=interval, limit=200)
            if df.empty:
                return "Không lấy được dữ liệu Binance."

            st.info(f"Tính Ichimoku Cloud cho: {coin_pair}, khung: {interval}")

            high = df["high"]
            low = df["low"]
            close = df["close"]

            # --- 2️. Tính các đường Ichimoku ---
            # Tenkan-sen (Conversion Line) 9 kỳ
            period9_high = high.rolling(window=9).max()
            period9_low = low.rolling(window=9).min()
            tenkan_sen = (period9_high + period9_low) / 2

            # Kijun-sen (Base Line) 26 kỳ
            period26_high = high.rolling(window=26).max()
            period26_low = low.rolling(window=26).min()
            kijun_sen = (period26_high + period26_low) / 2

            # Senkou Span A (Leading Span A) dịch trước 26 kỳ
            senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

            # Senkou Span B (Leading Span B) 52 kỳ, dịch trước 26 kỳ
            period52_high = high.rolling(window=52).max()
            period52_low = low.rolling(window=52).min()
            senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

            # Chikou Span (Lagging Span) lùi 26 kỳ
            chikou_span = close.shift(-26)

            # --- 3️. Phân tích tín hiệu cơ bản ---
            # Giá trên mây → xu hướng tăng, dưới mây → xu hướng giảm
            last_close = close.iloc[-1]
            last_span_a = senkou_span_a.iloc[-1]
            last_span_b = senkou_span_b.iloc[-1]

            if last_close > max(last_span_a, last_span_b):
                signal = "🟢 Giá trên mây → Xu hướng **tăng**, tín hiệu **mua**."
            elif last_close < min(last_span_a, last_span_b):
                signal = "🔴 Giá dưới mây → Xu hướng **giảm**, tín hiệu **bán**."
            else:
                signal = "⚪ Giá trong mây → Thị trường **sideway**, nên quan sát thêm."

            # --- 4️. Trả kết quả ---
            result = (
                f"**Kết quả Ichimoku Cloud ({coin_pair})**\n"
                f"- Tenkan-sen: {tenkan_sen.iloc[-1]:.4f}\n"
                f"- Kijun-sen: {kijun_sen.iloc[-1]:.4f}\n"
                f"- Senkou Span A: {last_span_a:.4f}\n"
                f"- Senkou Span B: {last_span_b:.4f}\n"
                f"- Chikou Span: {chikou_span.iloc[-1]:.4f}\n"
                f"{signal}"
            )
            return result

        except KeyError:
            return "❌ Dữ liệu không hợp lệ — thiếu cột 'high', 'low' hoặc 'close'."
        except Exception as e:
            return f"⚠️ Lỗi khi tính Ichimoku Cloud: {e}"