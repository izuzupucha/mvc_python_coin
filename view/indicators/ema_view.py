import streamlit as st
from config import constants as cons
from common.session_utils import reset_order_form_state, reset_ema_state
from common.session_utils import reset_all_states
from model.calcullate_model.calculate_trade_levels_atr_model import CalculateTradeLevelsAtrModel
class EMAView:
    @staticmethod
    def show(controller):
        st.header("📊 Phân tích EMA Indicator")

        if "ema_result" not in st.session_state:
            st.session_state["ema_result"] = None

        # --- Form ---
        with st.form("ema_form"):
            coin_pair = st.text_input("Nhập cặp coin cần phân tích", value=st.session_state.get("last_coin_pair", "BTCUSDT"))
            interval = st.selectbox("Chọn khung thời gian", ["1m","5m","15m","30m","1h","4h","1d"], 
                index=["1m","5m","15m","30m","1h","4h","1d"].index(st.session_state.get("last_interval", "15m"))
            )
            submitted = st.form_submit_button("🔍 Phân tích EMA")

            if submitted:
                if not coin_pair.strip():
                    st.warning("⚠️ Vui lòng nhập cặp coin.")
                    st.session_state["ema_result"] = None
                else:
                    try:
                        st.session_state["last_coin_pair"] = coin_pair
                        st.session_state["last_interval"] = interval
                        result = controller.handle_strategy(cons.EMA, coin_pair, interval)
                        st.session_state["ema_result"] = result
                        reset_order_form_state()  # 👈 xóa dữ liệu form cũ
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi phân tích EMA: {e}")
                        st.session_state["ema_result"] = None

        result = st.session_state["ema_result"]

        if result:
            st.divider()
            st.success(result)

            if "mua" in result.lower() or "tăng" in result.lower():
                if st.button("🟢 Đặt lệnh Mua (Long)", key="btn_long"):
                    trade = controller.calculate_trade_levels_atr_model.calculate_trade_levels_atr(
                        symbol=st.session_state["last_coin_pair"],
                        interval=st.session_state["last_interval"],
                        direction="long",
                        atr_period=14,
                        atr_mult_sl=1.0,
                        rr_ratio=1.8
                    )
                    if trade:
                        reset_order_form_state()
                        st.session_state["trade_info"] = trade
                        st.session_state["show_order_form"] = ("long", trade["symbol"])
                        st.session_state["current_view"] = "order_form"
                        st.rerun()

            elif "bán" in result.lower() or "giảm" in result.lower():
                if st.button("🔴 Đặt lệnh Bán (Short)", key="btn_short"):
                    trade = controller.calculate_trade_levels_atr_model.calculate_trade_levels_atr(
                        symbol=st.session_state["last_coin_pair"],
                        interval=st.session_state["last_interval"],
                        direction="short",
                        atr_period=14,
                        atr_mult_sl=1.0,
                        rr_ratio=1.8
                    )
                    if trade:
                        reset_order_form_state()
                        st.session_state["trade_info"] = trade
                        st.session_state["show_order_form"] = ("short", trade["symbol"])
                        st.session_state["current_view"] = "order_form"
                        st.rerun()
        elif result is not None:
            st.info("Không có dữ liệu trả về.")    
