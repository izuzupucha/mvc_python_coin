import os
import streamlit as st
from model.base_analyze_model import BaseAnalyzeModel
class AnalyzePSARModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)
    # ================= parabolic sar =================#    
    def analyze_psar(self, coin_pair, interval, step=0.02, max_step=0.2):
        """
        Phân tích Parabolic SAR cho 1 cặp coin.
        Giúp xác định xu hướng và điểm đảo chiều.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df,info = self.data_model.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
            if df.empty:
                return "Không lấy được dữ liệu Binance."

            st.info(f"Tính Parabolic SAR cho: {coin_pair}, khung: {interval}, step={step}, max_step={max_step}")

            high = df["high"]
            low = df["low"]
            close = df["close"]

            # --- 2️. Tính Parabolic SAR ---
            sar = pd.Series([0] * len(df))
            long = True  # giả sử bắt đầu xu hướng tăng
            af = step
            ep = low[0]  # extreme point (điểm cực trị)

            sar.iloc[0] = low[0]

            for i in range(1, len(df)):
                prev_sar = sar.iloc[i - 1]

                if long:
                    sar.iloc[i] = prev_sar + af * (ep - prev_sar)
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + step, max_step)
                    if low[i] < sar.iloc[i]:
                        # đảo chiều xuống
                        long = False
                        sar.iloc[i] = ep
                        ep = low[i]
                        af = step
                else:
                    sar.iloc[i] = prev_sar - af * (prev_sar - ep)
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + step, max_step)
                    if high[i] > sar.iloc[i]:
                        # đảo chiều lên
                        long = True
                        sar.iloc[i] = ep
                        ep = high[i]
                        af = step

            # --- 3️. Phân tích tín hiệu cơ bản ---
            last_close = close.iloc[-1]
            last_sar = sar.iloc[-1]

            if last_close > last_sar:
                signal = "🟢 Giá trên SAR → Xu hướng **tăng**, tín hiệu **mua**."
            elif last_close < last_sar:
                signal = "🔴 Giá dưới SAR → Xu hướng **giảm**, tín hiệu **bán**."
            else:
                signal = "⚪ Giá gần SAR → Thị trường **sideway**, nên quan sát thêm."

            # --- 4️. Trả kết quả ---
            result = (
                f"**Kết quả Parabolic SAR ({coin_pair})**\n"
                f"- SAR hiện tại: {last_sar:.4f}\n"
                f"{signal}"
            )
            return result

        except KeyError:
            return "❌ Dữ liệu không hợp lệ — thiếu cột 'high', 'low' hoặc 'close'."
        except Exception as e:
            return f"⚠️ Lỗi khi tính Parabolic SAR: {e}"