import sys, os
sys.path.append(os.path.dirname(__file__))
import streamlit as st
from controller.coin_controller import CoinController
from controller.user_controller import UserController
from view.admin.menu_view import MenuView
from view.user.login_view import LoginView
from view.user.profile_view import ProfileView
from view.indicators.order_form_view import OrderFormView
from view.indicators.ema_view import EMAView
import datetime

st.set_page_config(page_title="Crypto Analyzer", page_icon="💹", layout="centered")

def is_running_on_streamlit_cloud() -> bool:
    return st.secrets.get("env", {}).get("mode") == "cloud"

def main():
    params = st.query_params
    if "ping" in params:
        st.write(f"OK - {datetime.datetime.utcnow().isoformat()} UTC")
        st.stop()
    
    user_controller = UserController()
    controller = CoinController()

    # 🧠 Kiểm tra môi trường
    running_on_cloud = is_running_on_streamlit_cloud()

    # ✅ LOCAL: tạo user giả để test
    # ✅ CLOUD: bắt buộc login
    if "user" not in st.session_state:
        if running_on_cloud:
            LoginView.show_login(user_controller)
            return
        else:
            st.session_state["user"] = {
                "id": 1,
                "email": "test@example.com",
                "role": "user",
                "username": "local_dev"
            }

    # 🧭 Khởi tạo trang mặc định
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "admin"

    # 🧭 Khởi tạo view mặc định (menu)
    if "current_view" not in st.session_state:
        st.session_state["current_view"] = "menu"

    user = st.session_state["user"]

    # 🔀 Điều hướng hiển thị view
    current_view = st.session_state.get("current_view", "menu")

    if current_view == "menu":
        MenuView.show_main_menu(controller, user_controller, user)

    elif current_view == "ema":
        EMAView.show(controller)

    elif current_view == "order_form":        
        order_type, coin_pair_to_order = st.session_state["show_order_form"]
        OrderFormView.show(order_type, coin_pair_to_order)

    elif current_view == "profile":
        ProfileView.show_profile(user_controller, user)

    else:
        st.warning("⚠️ View không xác định, quay lại menu chính.")
        st.session_state["current_view"] = "menu"
        st.rerun()


if __name__ == "__main__":
    main()
