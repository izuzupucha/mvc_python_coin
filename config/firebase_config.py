import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
# tải file service account
#cred = credentials.Certificate("scalp-trade-5m-firebase.json")
# khởi tạo firebase app
#firebase_admin.initialize_app(cred)
# Kết nối đến firebase
#db = firestore.client()
#lấy thông tin firebase từ secrect của treamlit
if not firebase_admin._apps:
    firebase_creds = json.loads(st.secrets["firebase"]["service_account"])
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred)
db = firestore.client()