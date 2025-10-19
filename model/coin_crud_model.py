from config.firebase_config import db
from binance.client import Client
import os
import streamlit as st
class CRUDCoinModel:
    def __init__(self, collection_name="coin"):
            try:
                self.collection = db.collection(collection_name)
            except Exception as e:
                st.error(f"❌ Lỗi khi kết nối Firestore collection '{collection_name}': {e}")
                self.collection = None

    # ================= Firestore CRUD =================
    def add_coin(self, coin_data):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            doc_ref = self.collection.add(coin_data)
            st.success("✅ Thêm coin thành công.")
            return doc_ref
        except Exception as e:
            st.error(f"❌ Lỗi khi thêm coin: {e}")
            return None

    def get_coins(self):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            docs = self.collection.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            st.error(f"❌ Lỗi khi lấy danh sách coin: {e}")
            return []

    def get_coin_by_id(self, coin_id):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            doc = self.collection.document(coin_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            st.error(f"❌ Lỗi khi lấy coin theo ID: {e}")
            return None

    def update_coin(self, coin_id, data):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            self.collection.document(coin_id).update(data)
            st.success(f"✅ Cập nhật coin {coin_id} thành công.")
        except Exception as e:
            st.error(f"❌ Lỗi khi cập nhật coin {coin_id}: {e}")

    def delete_coin(self, coin_id):
        try:
            if self.collection is None:
                raise ValueError("Firestore collection chưa khởi tạo.")
            self.collection.document(coin_id).delete()
            st.warning(f"❌ Đã xóa coin {coin_id}.")
        except Exception as e:
            st.error(f"❌ Lỗi khi xóa coin {coin_id}: {e}")
