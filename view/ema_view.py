import streamlit as st
from config import constants as cons
class EMAView:
    @staticmethod
    def show(controller):
        st.header(" Phân tích EMA Indicator")
        with st.form("ema_form"):
            coin_pair = st.text_input("Nhập cặp coin cần phân tích", value="BTCUSDT")
            interval = st.selectbox(
                "Chọn khung thời gian",
                ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
                index=2
            )
            #period = st.number_input(
            #    "Nhập chu kỳ EMA (period)", min_value=5, max_value=100, value=14, step=1
            #)

            submitted = st.form_submit_button("🔍 Phân tích EMA")

        # Xử lý sau khi bấm submit
        if submitted:
            if not coin_pair.strip():
                st.warning("⚠️ Vui lòng nhập cặp coin trước khi phân tích.")
            else:
                try:
                    result = controller.handle_strategy(cons.EMA, coin_pair, interval)
                    if result is not None:
                        st.success(result)
                    else: 
                        st.info(f"Không có dữ liệu trả về từ hàm phân tích EMA {result}")
                except Exception as e:
                    st.error(f"Hàm phân tích EMA có lỗi {e}")
        st.divider()
       