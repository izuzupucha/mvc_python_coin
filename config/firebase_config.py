import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# =======================
# Khởi tạo Firebase App
# =======================

def init_firebase():
    try:
        if not firebase_admin._apps:  # tránh khởi tạo lại nhiều lần
            # 1️⃣ Lấy secret từ Streamlit (local dev)
            if "firebase" in st.secrets:
                firebase_creds_json = st.secrets["firebase"]["service_account"]
                cred = credentials.Certificate(json.loads(firebase_creds_json))
                firebase_admin.initialize_app(cred)

            # 2️⃣ Lấy secret từ Environment Variable (deploy Cloud Run / Firebase)
            elif os.environ.get("FIREBASE_SERVICE_ACCOUNT"):
                firebase_creds_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
                cred = credentials.Certificate(json.loads(firebase_creds_json))
                firebase_admin.initialize_app(cred)

            else:
                st.error("❌ Không tìm thấy Firebase credentials!")
                return None

        return firestore.client()

    except json.JSONDecodeError:
        st.error("❌ Firebase credentials JSON không hợp lệ!")
        return None
    except ValueError as e:
        st.error(f"❌ Lỗi khi khởi tạo Firebase: {e}")
        return None
    except Exception as e:
        st.error(f"⚠️ Lỗi không xác định khi kết nối Firebase: {e}")
        return None
# =======================
# Tạo kết nối Firestore mặc định
# =======================
db = init_firebase()        