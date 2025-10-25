# file: model/calculate_entry_model.py  (hoặc tương tự)
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
                        # cho phép direction optional; nếu None -> model sẽ quyết định
                        direction: str = None,
                        ema_period: int = 20,
                        rsi_period: int = 14,
                        atr_period: int = 14,
                        atr_mult_sl: float = 1.0,
                        rr_ratio: float = 1.5,
                        lookback: int = 200):
        """
        Tính entry theo chiến lược RSI + EMA Pullback + ATR.
        Nếu direction is None -> model sẽ suy ra dựa trên EMA20 vs price.
        Nếu direction được truyền ("long" hoặc "short") -> model sẽ tuân theo đó.
        Trả về dict giống cấu trúc:
        {
            "symbol": symbol,
            "interval": interval,
            "direction": "long" / "short",
            "entry": ...,
            "stoploss": ...,
            "takeprofit": ...,
            "atr_value": ...,
            "ema": ...,
            "rsi": ...,
            "timestamp": ...
        }
        Trả về None nếu không có tín hiệu.
        """
        try:
            df, info = self.data_model.get_klines_binance(symbol=symbol, interval=interval, limit=lookback)
            if df.empty:
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

            # Nếu caller không truyền direction, suy luận từ EMA vs price
            inferred_direction = None
            if last["close"] > last["ema"]:
                inferred_direction = "long"
            elif last["close"] < last["ema"]:
                inferred_direction = "short"

            # final direction: param overrides inference (if provided)
            final_dir = direction.lower() if isinstance(direction, str) else inferred_direction

            # Nếu vẫn không rõ direction -> không có tín hiệu
            if final_dir not in ("long", "short"):
                st.info("Không xác định được hướng (long/short).")
                return None

            # Logic RSI + Pullback confirmation:
            # - Long: RSI < 40 và RSI đang bật tăng (prev.rsi < last.rsi)
            # - Short: RSI > 60 và RSI đang bật giảm (prev.rsi > last.rsi)
            rsi_ok = False
            if final_dir == "long":
                rsi_ok = (last["rsi"] < 40) and (prev["rsi"] < last["rsi"])
                st.info(f"RSI Pullback (LONG) — prev: {prev['rsi']:.2f}, last: {last['rsi']:.2f}, ok={rsi_ok}")
            else:
                rsi_ok = (last["rsi"] > 60) and (prev["rsi"] > last["rsi"])
                st.info(f"RSI Pullback (SHORT) — prev: {prev['rsi']:.2f}, last: {last['rsi']:.2f}, ok={rsi_ok}")

            if not rsi_ok:
                # Không thỏa điều kiện pullback
                st.info("Không thỏa điều kiện RSI pullback cho hướng: " + final_dir)
                return None

            entry = float(last["close"])
            atr = float(last["atr"])

            if np.isnan(atr) or atr <= 0:
                st.warning("ATR không hợp lệ, không thể tính SL/TP.")
                return None

            if final_dir == "long":
                stoploss = entry - atr * atr_mult_sl
                takeprofit = entry + (atr * atr_mult_sl * rr_ratio)
            else:
                stoploss = entry + atr * atr_mult_sl
                takeprofit = entry - (atr * atr_mult_sl * rr_ratio)

            return {
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

        except Exception as e:
            st.error(f"Lỗi trong calculate_entry: {e}")
            return None
