import streamlit as st
from config import constants as cons

class ADXView:
    @staticmethod
    def show(controller):
        st.header(" Phân tích ADX Indicator")
        with st.form("psar_form"):
            coin_pair = st.text_input("Nhập cặp coin cần phân tích", value="BTCUSDT")
            interval = st.selectbox(
                "Chọn khung thời gian",
                ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
                index=2
            )

            submitted = st.form_submit_button("🔍 Phân tích ADX")

        # Xử lý sau khi bấm submit
        if submitted:
            if not coin_pair.strip():
                st.warning("⚠️ Vui lòng nhập cặp coin trước khi phân tích.")
            else:
                try:
                    result = controller.handle_strategy(cons.ADX, coin_pair, interval)
                    if result is not None:
                        st.success(result)
                    else:
                        st.info(f"Không có dữ liệu trả về từ chiến lược ADX. {result}")
                except Exception as e:
                    st.error(f"❌ Lỗi khi phân tích ADX: {e}")

        st.divider()
