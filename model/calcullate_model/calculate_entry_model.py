import pandas as pd
import numpy as np
import streamlit as st
from model.base_analyze_model import BaseAnalyzeModel

class CalculateEntryModel(BaseAnalyzeModel):
    def __init__(self, data_model):
        super().__init__(data_model)

    def calculate_entry(self,
                        symbol,
                        interval,
                        direction: str = None,
                        ema_period: int = 20,
                        rsi_period: int = 14,
                        atr_period: int = 14,
                        atr_mult_sl: float = 1.0,
                        rr_ratio: float = 1.5,
                        lookback: int = 200,
                        rsi_threshold_long=45.0,
                        rsi_threshold_short=55.0):
        """
        Tính entry theo chiến lược RSI + EMA Pullback + ATR, có log chi tiết ra màn hình.
        """
        try:
            st.markdown("### 🧩 **THÔNG TIN ĐẦU VÀO**")
            st.json({
                "Cặp coin (symbol)": symbol,
                "Khung thời gian (interval)": interval,
                "Hướng vào lệnh": direction,
                "Chu kỳ EMA": ema_period,
                "Chu kỳ RSI": rsi_period,
                "Chu kỳ ATR": atr_period,
                "Hệ số ATR (SL)": atr_mult_sl,
                "Tỷ lệ RR (TP/SL)": rr_ratio,
                "Số nến phân tích": lookback,
                "Ngưỡng RSI Long": rsi_threshold_long,
                "Ngưỡng RSI Short": rsi_threshold_short
            })

            df, info = self.data_model.get_klines_binance(symbol=symbol, interval=interval, limit=lookback)
            if df.empty:
                st.warning("⚠️ Dữ liệu trống, không thể tính toán.")
                return None

            # --- Tính EMA ---
            df["ema"] = df["close"].ewm(span=ema_period, adjust=False).mean()

            # --- Tính RSI ---
            delta = df["close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(rsi_period).mean()
            avg_loss = loss.rolling(rsi_period).mean()
            rs = avg_gain / avg_loss
            df["rsi"] = 100 - (100 / (1 + rs))

            # --- Tính ATR ---
            high = df["high"]
            low = df["low"]
            close = df["close"]
            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            df["atr"] = tr.rolling(atr_period).mean()

            last = df.iloc[-1]
            prev = df.iloc[-2]

            # --- Xác định hướng giao dịch ---
            inferred_direction = None
            if last["close"] > last["ema"]:
                inferred_direction = "long"
            elif last["close"] < last["ema"]:
                inferred_direction = "short"

            final_dir = direction.lower() if isinstance(direction, str) else inferred_direction

            st.markdown("### 📊 **THÔNG TIN KỸ THUẬT CUỐI CÙNG**")
            st.json({
                "Giá đóng nến hiện tại (last_close)": round(last["close"], 4),
                "Giá đóng nến trước đó (prev_close)": round(prev["close"], 4),
                "EMA hiện tại": round(last["ema"], 4),
                "RSI hiện tại (rsi_last)": round(last["rsi"], 2),
                "RSI trước đó (rsi_prev)": round(prev["rsi"], 2),
                "ATR hiện tại": round(last["atr"], 4),
                "Hướng suy luận từ EMA (direction_inferred)": inferred_direction,
                "Hướng giao dịch cuối cùng (direction_final)": final_dir,
                "Ngưỡng RSI cho Long": rsi_threshold_long,
                "Ngưỡng RSI cho Short": rsi_threshold_short
            })
            # --- Kiểm tra hướng ---
            if final_dir not in ("long", "short"):
                st.info("⚠️ Không xác định được hướng (long/short).")
                return None

            # --- Kiểm tra RSI Pullback động theo ngưỡng người dùng ---
            if final_dir == "long":
                rsi_ok = True
                #rsi_ok = (last["rsi"] < rsi_threshold_long) and (prev["rsi"] < last["rsi"])
                st.info(
                    f"RSI Pullback (LONG) — "
                    f"RSI trước đó (prev_rsi)={prev['rsi']:.2f}, RSI hiện tại (last_rsi)={last['rsi']:.2f}, "
                    f"Ngưỡng RSI cho Long={rsi_threshold_long}, ok={rsi_ok}. "
                    f"Không thỏa điều kiện: last_rsi({last['rsi']:.2f}) < ngưỡng RSI Long({rsi_threshold_long}) "
                    f"và prev_rsi ({prev['rsi']:.2f}) < last_rsi ({last['rsi']:.2f})."
                )
            else:
                rsi_ok = True
                #rsi_ok = (last["rsi"] > rsi_threshold_short) and (prev["rsi"] > last["rsi"])
                st.info(
                    f"RSI Pullback (SHORT) — "
                    f"RSI trước đó (prev_rsi)={prev['rsi']:.2f}, RSI hiện tại (last_rsi)={last['rsi']:.2f}, "
                    f"Ngưỡng RSI cho Short={rsi_threshold_short}, ok={rsi_ok}. "
                    f"Không thỏa điều kiện: last_rsi({last['rsi']:.2f}) > ngưỡng RSI short({rsi_threshold_short}) "
                    f"và prev_rsi({prev['rsi']:.2f}) > last_rsi ({last['rsi']:.2f})."
                )
            if not rsi_ok:
                st.warning(f"❌ Không thỏa điều kiện RSI pullback cho hướng {final_dir.upper()}")
                return None

            entry = float(last["close"])
            atr = float(last["atr"])

            if np.isnan(atr) or atr <= 0:
                st.warning("⚠️ ATR không hợp lệ, không thể tính SL/TP.")
                return None

            if final_dir == "long":
                stoploss = entry - atr * atr_mult_sl
                takeprofit = entry + (atr * atr_mult_sl * rr_ratio)
            else:
                stoploss = entry + atr * atr_mult_sl
                takeprofit = entry - (atr * atr_mult_sl * rr_ratio)

            result = {
                "symbol": symbol,
                "interval": interval,
                "direction": final_dir,
                "entry": round(entry, 8),
                "stoploss": round(stoploss, 8),
                "takeprofit": round(takeprofit, 8),
                "atr_value": round(atr, 8),
                "ema": round(last["ema"], 8),
                "rsi": round(last["rsi"], 4),
                "timestamp": pd.Timestamp.now()
            }

            st.markdown("### ✅ **KẾT QUẢ CUỐI CÙNG**")
            st.json(result)

            return result

        except Exception as e:
            st.error(f"💥 Lỗi trong calculate_entry: {e}")
            return None
