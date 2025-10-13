import streamlit as st
from config import constants as cons
from view.order_form_view import OrderFormView

class EMAView:
    @staticmethod
    def show(controller):
        st.header("📊 Phân tích EMA Indicator")
        
        # 1. Khai báo biến trạng thái cho kết quả phân tích
        if "ema_result" not in st.session_state:
            st.session_state["ema_result"] = None
        
        # --- Form Phân tích EMA ---
        with st.form("ema_form"):
            coin_pair = st.text_input("Nhập cặp coin cần phân tích", value=st.session_state.get("last_coin_pair", "BTCUSDT"))
            interval = st.selectbox(
                "Chọn khung thời gian", 
                ["1m", "5m", "15m", "30m", "1h", "4h", "1d"], 
                index=["1m", "5m", "15m", "30m", "1h", "4h", "1d"].index(st.session_state.get("last_interval", "15m"))
            )
            submitted = st.form_submit_button("🔍 Phân tích EMA")

            if submitted:
                if not coin_pair.strip():
                    st.warning("⚠️ Vui lòng nhập cặp coin trước khi phân tích.")
                    st.session_state["ema_result"] = None # Xóa kết quả cũ nếu có lỗi
                else:
                    try:
                        # Lưu coin_pair và interval vào session_state để dùng cho lần sau
                        st.session_state["last_coin_pair"] = coin_pair
                        st.session_state["last_interval"] = interval

                        result = controller.handle_strategy(cons.EMA, coin_pair, interval)
                        st.session_state["ema_result"] = result # Lưu kết quả vào session_state
                        
                        # ⚠️ Quan trọng: Xóa trạng thái form đặt lệnh để chuẩn bị cho tín hiệu mới
                        if "show_order_form" in st.session_state:
                            del st.session_state["show_order_form"]
                            
                        # Buộc rerun để hiển thị kết quả và các nút đặt lệnh
                        st.rerun() 
                        
                    except Exception as e:
                        st.error(f"Hàm phân tích EMA có lỗi: {e}")
                        st.session_state["ema_result"] = None

        # --- Hiển thị kết quả và các nút Đặt lệnh (Nằm ngoài khối form) ---
        result = st.session_state["ema_result"]
        
        if result:
            st.divider()
            st.success(result)
            
            # --- Kiểm tra tín hiệu ---
            if "mua" in result.lower() or "tăng" in result.lower():
                # Dùng key duy nhất cho button để Streamlit có thể phân biệt
                if st.button("🟢 Đặt lệnh Mua (Long)", key="btn_long"):
                    # Thiết lập trạng thái và buộc rerun
                    st.session_state["show_order_form"] = ("long", st.session_state["last_coin_pair"])
                    st.rerun() # Rerun để hiển thị form đặt lệnh

            elif "bán" in result.lower() or "giảm" in result.lower():
                # Dùng key duy nhất cho button để Streamlit có thể phân biệt
                if st.button("🔴 Đặt lệnh Bán (Short)", key="btn_short"):
                    # Thiết lập trạng thái và buộc rerun
                    st.session_state["show_order_form"] = ("short", st.session_state["last_coin_pair"])
                    st.rerun() # Rerun để hiển thị form đặt lệnh
            else:
                st.info("⚪ Không có tín hiệu rõ ràng để đặt lệnh.")
        elif result is not None:
             st.info("Không có dữ liệu trả về từ hàm phân tích EMA.")

        # --- ✅ Hiển thị form đặt lệnh (Không đổi) ---
        if "show_order_form" in st.session_state:
            order_type, coin_pair_to_order = st.session_state["show_order_form"]
            OrderFormView.show(order_type, coin_pair_to_order)