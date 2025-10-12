import streamlit as st
from config import constants as cons
class RSIView:
    @staticmethod
    def show(controller):
        st.header(" Phân tích RSI Indicator")
        with st.form("rsi_form"):
            coin_pair = st.text_input("Nhập cặp coin cần phân tích", value="BTCUSDT")
            interval = st.selectbox(
                "Chọn khung thời gian",
                ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
                index=2
            )
            period = st.number_input(
                "Nhập chu kỳ RSI (period)", min_value=5, max_value=100, value=14, step=1
            )

            submitted = st.form_submit_button("🔍 Phân tích RSI")

        # Xử lý sau khi bấm submit
        if submitted:
            if not coin_pair.strip():
                st.warning("⚠️ Vui lòng nhập cặp coin trước khi phân tích.")
            else:
                try:
                    # Gọi controller theo chuẩn MVC: key "rsi" + params
                    result = controller.handle_strategy(cons.RSI, coin_pair, interval, period)
                    st.write("DEBUG result:", result)
                    # Nếu controller trả về chuỗi kết quả thì hiển thị
                    if result is None:
                    st.warning("⚠️ Không có dữ liệu trả về từ hàm phân tích RSI.")
                    elif isinstance(result, str):
                        st.success(result)
                    elif hasattr(result, "to_dict"):   # pandas DataFrame
                        st.dataframe(result)
                    elif hasattr(result, "to_json"):   # plotly Figure
                        st.plotly_chart(result, use_container_width=True)
                    else:
                        st.write(result)
                except Exception as e:
                    st.info(f"Hàm phân tích RSI có lỗi {e}")
        st.divider()
       