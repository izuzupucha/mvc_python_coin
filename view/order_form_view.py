import streamlit as st
from common.session_utils import reset_order_form_state
from common.session_utils import reset_all_states
class OrderFormView:
    @staticmethod
    def calculate_sl_tp(order_type: str, current_price: float):
        if order_type == 'long':
            stop_loss = current_price * 0.99
            take_profit = current_price * 1.02
        else:
            stop_loss = current_price * 1.01
            take_profit = current_price * 0.98
        return round(stop_loss, 2), round(take_profit, 2)

    @staticmethod
    def show(order_type: str, coin_pair: str):
        st.subheader(f"💰 Đặt lệnh {'MUA (Long)' if order_type == 'long' else 'BÁN (Short)'} cho {coin_pair}")

        # 👇 Reset form cũ khi vào view này
        reset_order_form_state()

        if "calculated_entry" not in st.session_state:
            st.session_state["calculated_entry"] = 100.0
        if "calculated_sl" not in st.session_state:
            st.session_state["calculated_sl"] = 95.0
        if "calculated_tp" not in st.session_state:
            st.session_state["calculated_tp"] = 110.0
        if "auto_calculate_prices" not in st.session_state:
            st.session_state["auto_calculate_prices"] = False

        with st.form("order_form"):
            col1, col2 = st.columns(2)
            with col1:
                capital = st.number_input("💵 Tổng vốn (USD)", min_value=10.0, value=1000.0, step=10.0)
                risk_percent = st.number_input("⚠️ Tỷ lệ rủi ro (%)", min_value=0.1, max_value=100.0, value=2.0, step=0.5)
            with col2:
                entry_price = st.number_input("🎯 Entry", min_value=0.0, value=st.session_state["calculated_entry"], step=0.1)
                auto_calc = st.checkbox("✨ Tự động tính SL/TP", value=st.session_state["auto_calculate_prices"])

            if auto_calc:
                sl, tp = OrderFormView.calculate_sl_tp(order_type, entry_price)
                stop_loss = st.number_input("🛑 SL (auto)", value=sl, disabled=True)
                take_profit = st.number_input("🏁 TP (auto)", value=tp, disabled=True)
            else:
                stop_loss = st.number_input("🛑 SL", value=st.session_state["calculated_sl"])
                take_profit = st.number_input("🏁 TP", value=st.session_state["calculated_tp"])

            submitted = st.form_submit_button("✅ Xác nhận")

        if submitted:
            st.success(f"Lệnh {order_type.upper()} cho {coin_pair} đã tính toán xong.")

        # 🔙 Quay lại EMA (và xóa dữ liệu cũ)
        if st.button("🔙 Quay lại EMA"):
            reset_order_form_state()
            st.session_state["current_view"] = "ema"
            st.rerun()
