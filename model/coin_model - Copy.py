from config.firebase_config import db
from binance.client import Client
import os
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import time

BINANCE_ENDPOINTS = [
    "https://data-api.binance.vision/api/v3/klines",
    "https://api1.binance.com/api/v3/klines",
    "https://api2.binance.com/api/v3/klines",
    "https://api3.binance.com/api/v3/klines",
    "https://api.binance.com/api/v3/klines",
    ]
class CoinModel:
    # ================= ADX =================
    def analyze_adx(self, coin_pair, interval, period=14):
        """
        Phân tích ADX cho 1 cặp coin.
        Giúp xác định sức mạnh xu hướng và tín hiệu mua/bán.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
            if df.empty:
                return "Không lấy được dữ liệu Binance."

            st.info(f"Tính ADX cho: {coin_pair}, khung: {interval}, chu kỳ: {period}")

            high = df["high"]
            low = df["low"]
            close = df["close"]

            # --- 2️. Tính +DM, -DM, TR ---
            up_move = high.diff()
            down_move = low.diff().abs()

            plus_dm = pd.Series(0, index=df.index)
            minus_dm = pd.Series(0, index=df.index)

            plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
            minus_dm[(down_move > up_move) & (down_move > 0)] = down_move

            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # --- 3️. Tính smoothed TR, +DI, -DI ---
            atr = tr.rolling(window=period).mean()
            plus_di = 100 * (plus_dm.rolling(window=period).sum() / atr)
            minus_di = 100 * (minus_dm.rolling(window=period).sum() / atr)

            # --- 4️. Tính DX và ADX ---
            dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
            adx = dx.rolling(window=period).mean()

            # --- 5️. Lấy giá trị cuối cùng ---
            last_adx = adx.iloc[-1]
            last_plus_di = plus_di.iloc[-1]
            last_minus_di = minus_di.iloc[-1]

            # --- 6️. Phân tích tín hiệu cơ bản ---
            if last_adx > 25:
                if last_plus_di > last_minus_di:
                    signal = "🟢 ADX mạnh +DI>−DI → Xu hướng tăng, tín hiệu **mua**."
                else:
                    signal = "🔴 ADX mạnh −DI>+DI → Xu hướng giảm, tín hiệu **bán**."
            else:
                signal = "⚪ ADX < 25 → Xu hướng yếu, thị trường **sideway**."

            # --- 7️. Trả kết quả ---
            result = (
                f"**Kết quả ADX ({coin_pair})**\n"
                f"- +DI: {last_plus_di:.2f}\n"
                f"- -DI: {last_minus_di:.2f}\n"
                f"- ADX: {last_adx:.2f}\n"
                f"{signal}"
            )
            return result

        except KeyError:
            return "❌ Dữ liệu không hợp lệ — thiếu cột 'high', 'low' hoặc 'close'."
        except Exception as e:
            return f"⚠️ Lỗi khi tính ADX: {e}"
    # ================= BB =================
    def analyze_bb(self, coin_pair, interval, period=20, std_dev=2):
        """
        Phân tích Bollinger Bands cho 1 cặp coin.
        Giúp xác định mức hỗ trợ/kháng cự và biến động giá.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
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
            
    # ================= OBV =================        
    def analyze_obv(self, coin_pair, interval, period=14):
        """
        Tính OBV (On-Balance Volume) và phân tích xác nhận Volume.
        df: DataFrame phải có cột ['close', 'volume']
        """
        try:
            df = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
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
            
    # ================= RSI =================
    def analyze_rsi(self, coin_pair, interval, period=14):
        try:
            df = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
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
            
    # ================= KDJ =================        
    def analyze_kdj(self, coin_pair, interval, period=9, k_smooth=3, d_smooth=3):
        """
        Tính chỉ báo KDJ cho DataFrame nến.
        df: DataFrame phải có cột ['high','low','close']
        period: chu kỳ tính RSV (thường 9)
        k_smooth: làm mịn K (thường 3)
        d_smooth: làm mịn D (thường 3)
        """
        try:
            df = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
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
            
    #==============================Tính toán Entry / Stoploss / TakeProfit dựa theo ATR.================================
    def calculate_trade_levels_atr(self, symbol, interval, direction="long", atr_period=14, atr_mult_sl=1.0, rr_ratio=1.5):
        """
        Tính toán Entry / Stoploss / TakeProfit dựa theo ATR.
        - atr_period: số nến dùng để tính ATR
        - atr_mult_sl: hệ số nhân ATR cho stoploss
        - rr_ratio: tỉ lệ RR (takeprofit = stop_distance * rr_ratio)
        """
        try:
            df = self.get_klines_binance(symbol=symbol, interval=interval, limit=atr_period + 2)
            if df.empty:
                return None

            # --- Tính ATR ---
            high = df["high"]
            low = df["low"]
            close = df["close"]
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(atr_period).mean().iloc[-1]

            entry = close.iloc[-1]
            if direction == "long":
                stoploss = entry - atr * atr_mult_sl
                takeprofit = entry + (atr * atr_mult_sl * rr_ratio)
            else:
                stoploss = entry + atr * atr_mult_sl
                takeprofit = entry - (atr * atr_mult_sl * rr_ratio)

            return {
                "symbol": symbol,
                "interval": interval,
                "direction": direction,
                "entry": round(entry, 4),
                "stoploss": round(stoploss, 4),
                "takeprofit": round(takeprofit, 4),
                "atr_value": round(atr, 4),
                "timestamp": pd.Timestamp.now()
            }
        except Exception as e:
            st.error(f"Lỗi tính ATR SL/TP: {e}")
            return None
    #===================Tính toán Entry / Stoploss / TakeProfit dựa theo Bollinger Bands============================
    def calculate_trade_levels_bb(self, symbol, interval, direction="long", period=20, mult=2):
        """
        Tính toán Entry / Stoploss / TakeProfit dựa theo Bollinger Bands.
        """
        try:
            df = self.get_klines_binance(symbol=symbol, interval=interval, limit=period + 5)
            if df.empty:
                return None

            df["ma"] = df["close"].rolling(period).mean()
            df["std"] = df["close"].rolling(period).std()
            df["upper"] = df["ma"] + mult * df["std"]
            df["lower"] = df["ma"] - mult * df["std"]

            last = df.iloc[-1]
            entry = last["close"]

            if direction == "long":
                stoploss = last["lower"]
                takeprofit = entry + (entry - stoploss) * 1.5
            else:
                stoploss = last["upper"]
                takeprofit = entry - (stoploss - entry) * 1.5

            return {
                "symbol": symbol,
                "interval": interval,
                "direction": direction,
                "entry": round(entry, 4),
                "stoploss": round(stoploss, 4),
                "takeprofit": round(takeprofit, 4),
                "bb_upper": round(last["upper"], 4),
                "bb_lower": round(last["lower"], 4),
                "timestamp": pd.Timestamp.now()
            }
        except Exception as e:
            st.error(f"Lỗi tính Bollinger SL/TP: {e}")
            return None
    
            
model = CoinModel()
print(dir(model))
