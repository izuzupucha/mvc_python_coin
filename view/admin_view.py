import streamlit as st
from config.security import hash_password

st.set_page_config(page_title="Crypto Analyzer", page_icon="💹", layout="centered")

class AdminView:
    @staticmethod
    def show_user_admin(user_controller):
        st.title("👑 Quản trị người dùng")

        try:
            # --- Lưu trạng thái tab ---
            if "active_tab" not in st.session_state:
                st.session_state.active_tab = "list"

            # --- Menu tab giả lập ---
            col1, col2 = st.columns(2)
            if col1.button("📋 Danh sách người dùng"):
                st.session_state.active_tab = "list"
                st.rerun()
            if col2.button("➕ Thêm người dùng mới"):
                st.session_state.active_tab = "add"
                st.rerun()

            st.markdown("---")

            # === TAB 1: DANH SÁCH NGƯỜI DÙNG ===
            if st.session_state.active_tab == "list":
                st.subheader("📋 Danh sách người dùng")
                try:
                    users = user_controller.get_all_users()
                except Exception as e:
                    st.error(f"❌ Lỗi khi lấy danh sách người dùng: {e}")
                    users = []

                if not users:
                    st.info("Chưa có người dùng nào.")
                    return

                for user in users:
                    username = user.get("username", "username")
                    email = user.get("email", "(Không có email)")
                    role = user.get("role", "user")
                    user_id = user.get("id", "")

                    with st.expander(f"{email} ({role})"):
                        st.write(f"**Username:** {username}")
                        st.write(f"**Role hiện tại:** {role}")

                        # --- Cập nhật vai trò ---
                        new_role = st.selectbox(
                            f"Vai trò mới cho {email}",
                            ["user", "admin"],
                            index=0 if role == "user" else 1,
                            key=f"role_{user_id}"
                        )
                        if st.button(f"💾 Cập nhật vai trò {email}", key=f"update_{user_id}"):
                            try:
                                user_controller.update_user(user_id, {"role": new_role})
                                st.success("✅ Cập nhật thành công!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Lỗi khi cập nhật vai trò: {e}")

                        # --- Reset mật khẩu ---
                        if st.button(f"🔑 Reset mật khẩu cho {email}", key=f"reset_{user_id}"):
                            try:
                                new_pass = "123456"
                                user_controller.update_user(user_id, {"password": hash_password(new_pass)})
                                st.info(f"🔄 Mật khẩu mới cho **{email}** là: `{new_pass}`")
                            except Exception as e:
                                st.error(f"❌ Lỗi khi reset mật khẩu: {e}")

                        # --- Xóa user ---
                        if email == "admin@coin.com":
                            st.info("⚠️ Không thể xóa tài khoản admin gốc.")
                        else:
                            if st.button(f"🗑️ Xóa người dùng {email}", key=f"delete_{user_id}"):
                                try:
                                    user_controller.delete_user(user_id)
                                    st.warning(f"❌ Đã xóa người dùng {email}!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Lỗi khi xóa người dùng: {e}")

            # === TAB 2: THÊM NGƯỜI DÙNG MỚI ===
            elif st.session_state.active_tab == "add":
                st.subheader("➕ Thêm người dùng mới")

                username = st.text_input("Username", key="new_username")
                email = st.text_input("Email", key="new_email")
                password = st.text_input("Mật khẩu", type="password", key="new_password")
                role = st.selectbox("Vai trò", ["user", "admin"], key="new_role")

                if st.button("Thêm người dùng", key="btn_add_user"):
                    if not username or not email or not password:
                        st.error("⚠️ Vui lòng nhập đầy đủ thông tin!")
                    else:
                        try:
                            result = user_controller.add_user(username, email, hash_password(password), role)
                            if result is False:
                                st.error("❌ Email đã tồn tại hoặc không thể thêm người dùng!")
                            else:
                                st.success(f"✅ Đã thêm người dùng mới: {email}")
                                st.balloons()

                                # Reset form
                                for key in ["new_username", "new_email", "new_password", "new_role"]:
                                    if key in st.session_state:
                                        del st.session_state[key]

                                # 🔁 Chuyển về tab Danh sách
                                st.session_state.active_tab = "list"
                                st.rerun()

                        except Exception as e:
                            st.error(f"❌ Lỗi khi thêm người dùng: {e}")

        except Exception as e:
            st.error(f"❌ Lỗi không xác định trong AdminView: {e}")


if __name__ == "__main__":
    AdminView.show_user_admin(None)
