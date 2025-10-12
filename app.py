import streamlit as st
from controller.coin_controller import CoinController
from controller.user_controller import UserController
from view.menu_view import MenuView
from view.login_view import LoginView
from view.profile_view import ProfileView

st.set_page_config(page_title="Crypto Analyzer", page_icon="💹", layout="centered")

def main():
    user_controller = UserController()
    if "user" not in st.session_state:
            st.session_state["user"] = {
                "id": 1,
                "email": "test@example.com",
                "role": "user",
                "username": "truo"
            }
    # 🧭 Nếu chưa đăng nhập thì hiển thị trang Login
    if "user" not in st.session_state:
        LoginView.show_login(user_controller)
        return

    # 🧭 Khởi tạo trang mặc định
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "admin"

    user = st.session_state["user"]
    controller = CoinController()

    # 🔀 Điều hướng theo active_page
    if st.session_state["active_page"] == "home":
        MenuView.go_home()
    elif st.session_state["active_page"] == "profile":
        ProfileView.show_profile(user_controller, user)
    else:
        MenuView.show_main_menu(controller, user_controller, user)

if __name__ == "__main__":
    main()
