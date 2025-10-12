import streamlit as st
from config.security import hash_password

class ProfileView:
    @staticmethod
    def show_profile(user_controller, user):
        st.title("👤 Thông tin cá nhân")

        st.write(f"**Email hiện tại:** {user.get('email', '(chưa có)')}")
        st.write(f"**Vai trò:** {user.get('role', 'user')}")

        st.subheader("🔧 Cập nhật thông tin")

        # --- Form cập nhật ---
        new_email = st.text_input("Email mới", value=user.get("email", ""), key="profile_new_email")
        new_password = st.text_input("Mật khẩu mới (bỏ trống nếu không đổi)", type="password", key="profile_new_password")

        # --- Nếu là admin, cho phép đổi vai trò ---
        new_role = user.get("role", "user")
        if user.get("role") == "admin":
            new_role = st.selectbox(
                "Vai trò", 
                ["user", "admin"], 
                index=0 if new_role == "user" else 1,
                key="profile_new_role"
            )

        # --- Nút cập nhật ---
        if st.button("💾 Cập nhật thông tin"):
            try:
                update_data = {}
                if new_email and new_email != user.get("email"):
                    update_data["email"] = new_email
                if new_password:
                    update_data["password"] = hash_password(new_password)
                if new_role != user.get("role"):
                    update_data["role"] = new_role

                if not update_data:
                    st.info("ℹ️ Không có thay đổi nào để cập nhật.")
                    return

                # --- Gọi controller update ---
                user_controller.update_user(user["id"], update_data)

                # --- Cập nhật session user ---
                st.session_state["user"].update(update_data)

                # --- Xóa dữ liệu trên form ---
                for key in ["profile_new_email", "profile_new_password", "profile_new_role"]:
                    if key in st.session_state:
                        del st.session_state[key]

                st.success("✅ Cập nhật thông tin thành công! Đang quay lại trang chủ...")

                # --- Chuyển về màn hình Trang chủ ---
                st.session_state["active_page"] = "home"  # tùy vào app bạn định nghĩa key này
                st.rerun()

            except Exception as e:
                st.error(f"🚨 Lỗi khi cập nhật thông tin: {e}")

        st.divider()
