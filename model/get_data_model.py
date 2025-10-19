import streamlit as st
import pandas as pd
import requests
import time

BINANCE_BASES = [
    "https://data-api.binance.vision",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
    "https://api.binance.com",
]
KLINE_PATH = "/api/v3/klines"


class GetDataModel:
    def get_klines_binance(self, symbol="BTCUSDT", interval="15m", limit=200, max_retries=2):
        """
        Lấy dữ liệu nến từ Binance, có fallback qua nhiều endpoint.
        Trả về (DataFrame, info)
        """
        headers = {"User-Agent": "Mozilla/5.0 (compatible; my-rsi-app/1.0)"}
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        last_err = None

        for base in BINANCE_BASES:
            url = base + KLINE_PATH
            for attempt in range(max_retries):
                try:
                    resp = requests.get(url, params=params, headers=headers, timeout=15)
                    resp.raise_for_status()
                    data = resp.json()

                    if isinstance(data, list) and len(data) > 0:
                        # Convert sang DataFrame
                        df = pd.DataFrame(data, columns=[
                            "time", "open", "high", "low", "close", "volume",
                            "close_time", "qav", "trades", "taker_base", "taker_quote", "ignore"
                        ])
                        df["time"] = pd.to_datetime(df["time"], unit="ms")
                        df[["open", "high", "low", "close", "volume"]] = df[
                            ["open", "high", "low", "close", "volume"]
                        ].astype(float)

                        st.success(f"✅ Lấy dữ liệu thành công từ: {url}")
                        return df, {"endpoint": url, "rows": len(df)}

                    else:
                        last_err = f"Bad payload {data}"
                        continue  # thử endpoint khác

                except requests.exceptions.Timeout:
                    last_err = f"⏰ Timeout {url}"
                    st.warning(f"⏰ Lỗi timeout (attempt {attempt+1})")
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
        return pd.DataFrame(), {"error": last_err}

    #================Gọi kết quả từ ByBit====================================#
    def get_klines_bybit(self, symbol="BTCUSDT", interval="15", limit=200, category="spot"):
        url = "https://api.bybit.com/v5/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "result" not in data or "list" not in data["result"]:
                raise ValueError(f"Phản hồi API Bybit không hợp lệ: {data}")

            kline_data = data["result"]["list"][::-1]  # đảo ngược

            df = pd.DataFrame(kline_data, columns=[
                "time", "open", "high", "low", "close", "volume", "turnover"
            ])
            df["time"] = pd.to_datetime(df["time"].astype(int), unit="s")
            df[["open", "high", "low", "close", "volume"]] = df[
                ["open", "high", "low", "close", "volume"]
            ].astype(float)

            return df, {"source": "Bybit", "rows": len(df)}

        except requests.exceptions.Timeout:
            return pd.DataFrame(), {"error": "⏰ Timeout Bybit"}

        except requests.exceptions.RequestException as e:
            return pd.DataFrame(), {"error": f"❌ Request Bybit: {e}"}

        except Exception as e:
            return pd.DataFrame(), {"error": f"⚠️ Unknown Bybit error: {e}"}
