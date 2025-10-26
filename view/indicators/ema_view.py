import streamlit as st
from config import constants as cons
from common.session_utils import reset_order_form_state, reset_ema_state
from common.session_utils import reset_all_states
from model.calcullate_model.calculate_entry_model import CalculateEntryModel

class EMAView:
    @staticmethod
    def show(controller):
        st.header("📊 Phân tích EMA Indicator")

        if "ema_result" not in st.session_state:
            st.session_state["ema_result"] = None

        # --- Nút quay lại ---
        if st.button("🔙 Quay lại Trang chủ", key="ema_top"):
            st.session_state.page = "home"
            st.session_state["current_view"] = "menu"
            st.rerun()
            st.stop()

        # --- Form nhập liệu ---
        with st.form("ema_form"):
            coin_pair = st.text_input(
                "Nhập cặp coin cần phân tích",
                value=st.session_state.get("last_coin_pair", "BTCUSDT")
            )
            interval = st.selectbox(
                "Chọn khung thời gian",
                ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
                index=["1m", "5m", "15m", "30m", "1h", "4h", "1d"].index(
                    st.session_state.get("last_interval", "15m")
                )
            )
            submitted = st.form_submit_button("🔍 Phân tích EMA")
            
            if submitted:
                if not coin_pair.strip():
                    st.warning("⚠️ Vui lòng nhập cặp coin.")
                    st.session_state["ema_result"] = None
                else:
                    try:
                        st.session_state.pop("ema_result", None)
                        st.session_state.pop("trade_info", None)
                        reset_order_form_state()                        
                        st.session_state["last_coin_pair"] = coin_pair
                        st.session_state["last_interval"] = interval
                        result = controller.handle_strategy(cons.EMA, coin_pair, interval)
                        st.session_state["ema_result"] = result
                        reset_order_form_state()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi phân tích EMA: {e}")
                        st.session_state["ema_result"] = None

        result = st.session_state["ema_result"]

        if st.button("🔙 Quay lại Trang chủ", key="ema_bottom"):
            st.session_state.page = "home"
            st.session_state["current_view"] = "menu"
            st.rerun()
            st.stop()

        # --- Hiển thị kết quả ---
        if result:
            st.divider()
            st.success(result)

            # --- Cấu hình RSI Pullback ---
            st.markdown("### ⚙️ Cấu hình RSI Pullback")
            col1, col2 = st.columns(2)
            with col1:
                st.session_state["rsi_threshold_long"] = st.number_input(
                    "🔹 Ngưỡng RSI cho Long (mặc định 45):",
                    min_value=10.0, max_value=60.0,
                    value=st.session_state.get("rsi_threshold_long", 45.0),
                    step=0.5, key="rsi_long_input"
                )
            with col2:
                st.session_state["rsi_threshold_short"] = st.number_input(
                    "🔸 Ngưỡng RSI cho Short (mặc định 55):",
                    min_value=40.0, max_value=90.0,
                    value=st.session_state.get("rsi_threshold_short", 55.0),
                    step=0.5, key="rsi_short_input"
                )
            st.divider()

            # --- Logic đặt lệnh ---
            def log_trade_result(trade):
                """Hiển thị log tất cả tham số + kết quả"""
                st.markdown("### 🧾 **THÔNG TIN ĐẦU VÀO**")
                st.json({
                    "symbol": st.session_state["last_coin_pair"],
                    "interval": st.session_state["last_interval"],
                    "direction_input": trade["direction"],
                    "ema_period": 20,
                    "rsi_period": 14,
                    "atr_period": 14,
                    "atr_mult_sl": 1.0,
                    "rr_ratio": 1.8,
                    "lookback": 200,
                    "rsi_threshold_long": st.session_state.get("rsi_threshold_long", 45.0),
                    "rsi_threshold_short": st.session_state.get("rsi_threshold_short", 55.0)
                })

                st.markdown("### 📈 **THÔNG TIN KỸ THUẬT CUỐI CÙNG**")
                st.json({
                    "last_close": trade["entry"],
                    "ema": trade["ema"],
                    "rsi": trade["rsi"],
                    "atr": trade["atr_value"],
                    "direction_final": trade["direction"]
                })

                st.markdown("### ✅ **KẾT QUẢ ENTRY**")
                st.json({
                    "Entry": trade["entry"],
                    "Stoploss": trade["stoploss"],
                    "Takeprofit": trade["takeprofit"],
                    "RR": 1.8,
                    "Timestamp": str(trade["timestamp"])
                })

            # --- Nếu là tín hiệu MUA ---
            if "mua" in result.lower() or "tăng" in result.lower():
                if st.button("🟢 Đặt lệnh Mua (Long)", key="btn_long"):
                    trade = controller.calculate_entry_model.calculate_entry(
                        symbol=st.session_state["last_coin_pair"],
                        interval=st.session_state["last_interval"],
                        direction="long",
                        atr_period=14,
                        atr_mult_sl=1.0,
                        rr_ratio=1.8,
                        rsi_threshold_long=st.session_state.get("rsi_threshold_long", 45.0),
                        rsi_threshold_short=st.session_state.get("rsi_threshold_short", 55.0)
                    )
                    if trade:
                        log_trade_result(trade)
                        reset_order_form_state()
                        st.session_state["trade_info"] = trade
                        st.session_state["show_order_form"] = ("long", trade["symbol"])
                        st.session_state["current_view"] = "order_form"
                        st.rerun()

            # --- Nếu là tín hiệu BÁN ---
            elif "bán" in result.lower() or "giảm" in result.lower():
                if st.button("🔴 Đặt lệnh Bán (Short)", key="btn_short"):
                    trade = controller.calculate_entry_model.calculate_entry(
                        symbol=st.session_state["last_coin_pair"],
                        interval=st.session_state["last_interval"],
                        direction="short",
                        atr_period=14,
                        atr_mult_sl=1.0,
                        rr_ratio=1.8,
                        rsi_threshold_long=st.session_state.get("rsi_threshold_long", 45.0),
                        rsi_threshold_short=st.session_state.get("rsi_threshold_short", 55.0)
                    )
                    if trade:
                        log_trade_result(trade)
                        reset_order_form_state()
                        st.session_state["trade_info"] = trade
                        st.session_state["show_order_form"] = ("short", trade["symbol"])
                        st.session_state["current_view"] = "order_form"
                        st.rerun()

        elif result is not None:
            st.info("Không có dữ liệu trả về.")
