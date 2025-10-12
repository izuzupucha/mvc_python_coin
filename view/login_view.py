import streamlit as st
from config.security import hash_password


class LoginView:
    @staticmethod
    def show_login(user_controller):
        # --- Quản lý trạng thái màn hình ---
        if "screen" not in st.session_state:
            st.session_state["screen"] = "login"

        # ================================
        # MÀN HÌNH 1: ĐĂNG NHẬP
        # ================================
        if st.session_state["screen"] == "login":
            st.title("🔐 Đăng nhập hệ thống")

            email = st.text_input("Email hoặc Username")
            password = st.text_input("Mật khẩu", type="password")

            # --- Hai nút nằm cùng hàng ---
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Đăng nhập"):
                    if not email or not password:
                        st.warning("⚠️ Vui lòng nhập đầy đủ Email và Mật khẩu!")
                        return
                    try:
                        user = user_controller.login(email, password)
                        if user:
                            st.session_state["user"] = user
                            st.success("✅ Đăng nhập thành công!")
                            st.rerun()
                        else:
                            st.error("❌ Sai email hoặc mật khẩu!")
                    except Exception as e:
                        st.error(f"🚨 Lỗi khi đăng nhập: {e}")

            with col2:
                if st.button("Quên mật khẩu"):
                    st.session_state["screen"] = "reset_password"
                    st.rerun()

        # ================================
        # MÀN HÌNH 2: QUÊN MẬT KHẨU
        # ================================
        elif st.session_state["screen"] == "reset_password":
            st.title("🔑 Đặt lại mật khẩu")

            reset_email = st.text_input("Nhập email của bạn")
            new_password = st.text_input("Mật khẩu mới", type="password")

            if st.button("Cập nhật mật khẩu"):
                if not reset_email or not new_password:
                    st.warning("⚠️ Vui lòng nhập đầy đủ thông tin!")
                else:
                    try:
                        user = user_controller.get_user_by_email(reset_email)
                        if user:
                            user_controller.update_user(
                                user["id"],
                                {"password": hash_password(new_password)}
                            )
                            st.success("✅ Mật khẩu đã được cập nhật thành công!")

                            # 🕒 Quay lại đăng nhập sau khi reset thành công
                            st.session_state["screen"] = "login"
                            st.rerun()
                        else:
                            st.error("❌ Không tìm thấy người dùng với email này!")
                    except Exception as e:
                        st.error(f"🚨 Lỗi khi đặt lại mật khẩu: {e}")

            if st.button("⬅️ Quay lại đăng nhập"):
                st.session_state["screen"] = "login"
                st.rerun()
