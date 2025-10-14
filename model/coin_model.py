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
    def __init__(self, collection_name="coin"):
        try:
            self.collection = db.collection(collection_name)
        except Exception as e:
            st.error(f"❌ Lỗi khi kết nối Firestore collection '{collection_name}': {e}")
            self.collection = None

    # ================= Firestore CRUD =================
    def add_coin(self, coin_data):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            doc_ref = self.collection.add(coin_data)
            st.success("✅ Thêm coin thành công.")
            return doc_ref
        except Exception as e:
            st.error(f"❌ Lỗi khi thêm coin: {e}")
            return None

    def get_coins(self):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            docs = self.collection.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            st.error(f"❌ Lỗi khi lấy danh sách coin: {e}")
            return []

    def get_coin_by_id(self, coin_id):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            doc = self.collection.document(coin_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            st.error(f"❌ Lỗi khi lấy coin theo ID: {e}")
            return None

    def update_coin(self, coin_id, data):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            self.collection.document(coin_id).update(data)
            st.success(f"✅ Cập nhật coin {coin_id} thành công.")
        except Exception as e:
            st.error(f"❌ Lỗi khi cập nhật coin {coin_id}: {e}")

    def delete_coin(self, coin_id):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            self.collection.document(coin_id).delete()
            st.warning(f"❌ Đã xóa coin {coin_id}.")
        except Exception as e:
            st.error(f"❌ Lỗi khi xóa coin {coin_id}: {e}")
      

    def get_klines_binance(self, symbol="BTCUSDT", interval="15m", limit=200, max_retries=2):
        """
        Lấy dữ liệu nến từ Binance, có fallback qua nhiều endpoint.
        Trả về DataFrame với cột: time, open, high, low, close, volume
        """
        headers = {"User-Agent": "Mozilla/5.0 (compatible; my-rsi-app/1.0)"}
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        last_err = None

        for base in BINANCE_ENDPOINTS:
            url = base
#            st.write(f"🔄 Thử gọi Binance API: {url}")
            for attempt in range(max_retries):
                try:
                    resp = requests.get(url, params=params, headers=headers, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()

                    if isinstance(data, list) and len(data) > 0:
                        st.success(f"✅ Lấy dữ liệu thành công từ endpoint: {url}")

                        # Convert sang DataFrame
                        df = pd.DataFrame(data, columns=[
                            "time", "open", "high", "low", "close", "volume",
                            "close_time", "qav", "trades", "taker_base", "taker_quote", "ignore"
                        ])
                        df["time"] = pd.to_datetime(df["time"], unit="ms")
                        df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)
                        return df

                    else:
                        last_err = f"Bad payload {data}"
                        break

                except requests.exceptions.Timeout:
                    last_err = "⏰ Timeout"
                    st.warning(f"⏰ Lỗi timeout {url} (attempt {attempt+1})")
                    time.sleep(1)

                except requests.exceptions.RequestException as e:
                    last_err = str(e)
                    st.warning(f"⚠️ Request error {url} (attempt {attempt+1}): {e}")
                    time.sleep(1)

                except Exception as e:
                    last_err = str(e)
                    st.error(f"⚠️ Lỗi không xác định tại {url}: {e}")
                    break

        st.error(f"❌ Tất cả endpoint Binance đều thất bại. Lỗi cuối: {last_err}")
        return pd.DataFrame()



    def get_klines_bybit(self, symbol="BTCUSDT", interval="15", limit=200, category="spot"):
        url = "https://api.bybit.com/v5/market/kline"
        params = {
            "category": category,   # "spot" hoặc "linear"
            "symbol": symbol,
            "interval": interval,   # "1"=1m, "5"=5m, "15"=15m, "60"=1h, "240"=4h, "D"=1d
            "limit": limit
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "result" not in data or "list" not in data["result"]:
                raise ValueError(f"Phản hồi API Bybit không hợp lệ: {data}")

            # Bybit trả list theo thứ tự mới nhất → cũ nhất, ta đảo ngược lại
            kline_data = data["result"]["list"][::-1]

            df = pd.DataFrame(kline_data, columns=[
                "time", "open", "high", "low", "close", "volume", "turnover"
            ])

            # Convert kiểu dữ liệu
            df["time"] = pd.to_datetime(df["time"].astype(int), unit="s")
            df[["open", "high", "low", "close", "volume"]] = df[
                ["open", "high", "low", "close", "volume"]
            ].astype(float)

            return df, data   # ✅ luôn trả 2 giá trị

        except requests.exceptions.Timeout:
            return pd.DataFrame(), {"error": "⏰ Kết nối API Bybit quá thời gian chờ"}

        except requests.exceptions.RequestException as e:
            return pd.DataFrame(), {"error": f"❌ Lỗi khi gọi API Bybit: {e}"}

        except Exception as e:
            return pd.DataFrame(), {"error": f"⚠️ Lỗi không xác định: {e}"}
    # ================= EMA =================
    def analyze_ema(self, coin_pair, interval, short_period=12, long_period=26):
        """
        Phân tích EMA (Exponential Moving Average) cho 1 cặp coin.
        """
        try:
            df = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
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
    # ================= MACD =================        
    def analyze_macd(self, coin_pair, interval, short_period=12, long_period=26, signal_period=9):
        """
        Phân tích MACD (Moving Average Convergence Divergence)
        giúp xác định sức mạnh, hướng và thời điểm đảo chiều xu hướng.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
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

    # ================= ichimoku =================
    def analyze_ic(self, coin_pair, interval):
        """
        Phân tích Ichimoku Cloud cho 1 cặp coin.
        Giúp xác định xu hướng, hỗ trợ/kháng cự và tín hiệu mua/bán.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=200)
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
            
    # ================= parabolic sar =================
    def analyze_psar(self, coin_pair, interval, step=0.02, max_step=0.2):
        """
        Phân tích Parabolic SAR cho 1 cặp coin.
        Giúp xác định xu hướng và điểm đảo chiều.
        """
        try:
            # --- 1️. Lấy dữ liệu giá ---
            df = self.get_klines_binance(symbol=coin_pair, interval=interval, limit=500)
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
