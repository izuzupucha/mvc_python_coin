import streamlit as st

def reset_ema_state():
    """Xóa toàn bộ dữ liệu liên quan đến phân tích EMA."""
    for key in ["ema_result", "last_coin_pair", "last_interval", "trade_info", "show_order_form"]:
        if key in st.session_state:
            del st.session_state[key]

def reset_order_form_state():
    """Xóa dữ liệu form đặt lệnh."""
    for key in [
        "calculated_entry", "calculated_sl", "calculated_tp",
        "auto_calculate_prices", "entry_price_input", 
        "order_capital", "order_risk_percent"
    ]:
        if key in st.session_state:
            del st.session_state[key]

def reset_all_states():
    """Xóa sạch toàn bộ dữ liệu tạm (dùng khi quay lại menu chính)."""
    reset_ema_state()
    reset_order_form_state()
    for key in ["current_view"]:
        if key in st.session_state:
            del st.session_state[key]
