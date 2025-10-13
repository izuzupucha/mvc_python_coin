import streamlit as st
from view.profile_view import ProfileView
from view.admin_view import AdminView
from view.rsi_view import RSIView
from view.ema_view import EMAView
from view.macd_view import MACDView
from view.ic_view import ICView
from view.psar_view import PSARView
from view.adx_view import ADXView
from view.bb_view import BBView
from view.obv_view import OBVView
from view.kdj_view import KDJView
from config import constants as cons

class MenuView:
    @staticmethod
    def show_main_menu(controller, user_controller, user):
        # Khởi tạo biến điều hướng
        if "page" not in st.session_state:
            st.session_state.page = "home"

        # === PAGE 1: TRANG CHỦ ===
        if st.session_state.page == "home":
            st.markdown(
                f"<p style='font-size:16px; font-weight:600; color:#333;'>💹 Chào mừng <span style='color:#0078ff'>{user.get('email')}</span>!</p>",
                unsafe_allow_html=True
            )
            # --- CSS Tùy chỉnh để căn nút và bố cục đẹp hơn ---
            # --- CSS để làm nút có kích thước đồng đều và bố cục đẹp ---
            st.markdown("""
                <style>
                    /* Toàn bộ nút có cùng kích thước */
                    .stButton > button {
                        width: 100% !important;
                        height: 18px !important;
                        background-color: #f8f9fa;
                        color: #333;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        font-weight: 600;
                        font-size: 14px;
                        transition: all 0.2s ease-in-out;
                    }

                    /* Hover đẹp */
                    .stButton > button:hover {
                        background-color: #0078ff !important;
                        color: white !important;
                        border-color: #0078ff;
                        transform: scale(1.03);
                    }

                    /* Các cột có khoảng cách đều */
                    div[data-testid="column"] {
                        padding-right: 8px !important;
                        padding-left: 8px !important;
                    }

                    /* Khoảng cách giữa các nhóm */
                    h3, .stSubheader {
                        margin-top: 25px !important;
                        margin-bottom: 12px !important;
                    }

                    /* Gạch phân cách */
                    hr {
                        margin-top: 30px !important;
                        margin-bottom: 30px !important;
                        border-color: #ccc !important;
                    }
                    div[data-testid="stMarkdownContainer"] h3 {
                        font-size: 14px !important;
                        font-weight: 600 !important;
                        color: #444 !important;
                        margin-top: 16px !important;
                        margin-bottom: 8px !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            # --- Nhóm chỉ báo xu hướng ---
            st.subheader("1. Nhóm chỉ báo xu hướng")
            cols = st.columns(5)
            buttons = {
                cons.EMA: cols[0].button("Chỉ báo EMA"),
                cons.MACD: cols[1].button("Chỉ báo MACD"),
                cons.IC: cols[2].button("Ichimoku"),
                cons.PSAR: cols[3].button("Parabolic SAR"),
                cons.ADX: cols[4].button("Chỉ báo ADX")
            }
            
            # --- Nhóm chỉ báo phụ trợ xác nhận xu hướng---
            st.subheader("2. Nhóm chỉ báo phụ trợ xác nhận xu hướng")
            cols = st.columns(4)
            buttons.update({
                cons.RSI: cols[0].button("Chỉ báo RSI"),
                cons.BB: cols[1].button("Bollinger Bands"),
                cons.OBV: cols[2].button("Volume + OBV"),
                cons.KDJ: cols[3].button("Chỉ báo KDJ"),
            })
            
            # --- Combo nhóm chỉ báo xác nhận xu hướng---
            st.subheader("3. Combo chỉ báo xác nhận xu hướng")
            cols = st.columns(2)
            buttons.update({
                cons.EMA_MACD_RSI: cols[0].button("Combo EMA - MACD - RSI"),
                cons.EMA_20_50_MACD: cols[1].button("Combo EMA 20/50 - MACD"),
            })
            # --- Combo nhóm chỉ báo phát hiện đảo chiều ---
            st.subheader("4. Combo nhóm chỉ báo phát hiện đảo chiều")
            cols = st.columns(2)
            buttons.update({
                cons.RSI_MACD: cols[0].button("Combo RSI - MACD"),
                cons.MACD_SAR_ADX: cols[1].button("Combo MACD - SAR - ADX"),
            })
            # --- Combo nhóm chỉ báo Scalping nhanh ---
            st.subheader("5. Combo nhóm chỉ báo Scalping nhanh")
            cols = st.columns(2)
            buttons.update({
                cons.EMA_SAR: cols[0].button("Combo EMA 9/21 - SAR"),
                cons.RSI_Stoch_VWAP: cols[1].button("Combo RSI - Stoch - VWAP"),
            })                             

            # Khi bấm chiến lược, chuyển trang
            for key, clicked in buttons.items():
                if clicked:
                    st.session_state.page = key
                    st.rerun()
            st.markdown("---")

            # --- Hàng nút chức năng cuối trang ---
            st.subheader("⚙️ Tùy chọn")
            cols3 = st.columns(3 if user.get("role") == "admin" else 2)

            if cols3[0].button("👤 Thông tin cá nhân"):
                st.session_state.page = "profile"
                st.rerun()

            if user.get("role") == "admin":
                if cols3[1].button("👑 Quản trị người dùng"):
                    st.session_state.page = "admin"
                    st.rerun()
                logout_col = cols3[2]
            else:
                logout_col = cols3[1]

            if logout_col.button("🚪 Đăng xuất"):
                st.session_state.pop("user", None)
                st.session_state.page = "home"
                st.success("Đã đăng xuất!")
                st.rerun()
        else:
            # === PAGE 2: RSI ===
            # Nút quay lại đầu trang
            if st.button("🔙 Quay lại Trang chủ", key = "top"):
                MenuView.go_home()
                
            elif st.session_state.page == cons.EMA:
                EMAView.show(controller)
                
            elif st.session_state.page == cons.MACD:
                MACDView.show(controller)
                
            elif st.session_state.page == cons.IC:
                ICView.show(controller)
                
            elif st.session_state.page == cons.PSAR:
                PSARView.show(controller)
                
            elif st.session_state.page == cons.ADX:
                ADXView.show(controller)
                
            elif st.session_state.page == cons.RSI:
                RSIView.show(controller)
                
            elif st.session_state.page == cons.BB:
                BBView.show(controller)
                
            elif st.session_state.page == cons.OBV:
                OBVView.show(controller)
                
            elif st.session_state.page == cons.KDJ:
                KDJView.show(controller)
                
            elif st.session_state.page == cons.EMA_MACD_RSI:
                st.header("📊 EMA_MACD_RSI Indicator")
                controller.handle_strategy(cons.EMA_MACD_RSI, None, None)
                
            elif st.session_state.page == cons.EMA_20_50_MACD:
                st.header("📊 EMA_20_50_MACD Indicator")
                controller.handle_strategy(cons.EMA_20_50_MACD, None, None)
                
            elif st.session_state.page == cons.RSI_MACD:
                st.header("📊 RSI_MACD Indicator")
                controller.handle_strategy(cons.RSI_MACD, None, None)
                
            elif st.session_state.page == cons.MACD_SAR_ADX:
                st.header("📊 MACD_SAR_ADX Indicator")
                controller.handle_strategy(cons.MACD_SAR_ADX, None, None)
                
            elif st.session_state.page == cons.EMA_SAR:
                st.header("📊 EMA_SAR Indicator")
                controller.handle_strategy(cons.EMA_SAR, None, None)
                
            elif st.session_state.page == cons.RSI_Stoch_VWAP: 
                st.header("📊 RSI_Stoch_VWAP Indicator")
                controller.handle_strategy(cons.RSI_Stoch_VWAP, None, None)
                
            
            elif st.session_state.page == "profile":
                ProfileView.show_profile(user_controller, user)

            # === PAGE 5: Quản trị người dùng ===
            elif st.session_state.page == "admin":
                AdminView.show_user_admin(user_controller)

            # === PAGE 6: Các chiến lược khác (trend, breakout, scalp, reversal) ===
            else:
                st.header(f"🔍 Đang chạy chiến lược: {st.session_state.page}")
                controller.handle_strategy(st.session_state.page, None, None)
            if st.button("🔙 Quay lại Trang chủ", key = "bottom"):
                    MenuView.go_home()
    @staticmethod
    def go_home():
        """Chuyển hướng về trang chủ"""
        st.session_state.page = "home"
        st.rerun()
