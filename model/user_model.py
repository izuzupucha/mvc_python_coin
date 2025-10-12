from config.firebase_config import db
from google.cloud import firestore
from config.security import hash_password

class UserModel:
    @staticmethod
    def get_user_by_username_or_email(value):
        try:
            users_ref = db.collection("users")
            # tìm theo username
            query = users_ref.where("username", "==", value).stream()
            for doc in query:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            # nếu không thấy username, thử tìm email
            query = users_ref.where("email", "==", value).stream()
            for doc in query:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None
        except Exception as e:
            print(f"❌ Lỗi khi get_user_by_username_or_email: {e}")
            return None

    @staticmethod
    def get_user_by_email(email):
        try:
            users_ref = db.collection("users")
            query = users_ref.where("email", "==", email).stream()
            for doc in query:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None
        except Exception as e:
            print(f"❌ Lỗi khi get_user_by_email: {e}")
            return None

    @staticmethod
    def add_user(username, email, password, role="user"):
        try:
            hashed_pw = hash_password(password)
            db.collection("users").add({
                "username": username,
                "email": email,
                "password": hashed_pw,
                "role": role,
                "created_at": firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            print(f"❌ Lỗi khi add_user: {e}")
            return False

    @staticmethod
    def update_user(user_id, data):
        try:
            db.collection("users").document(user_id).update(data)
            return True
        except Exception as e:
            print(f"❌ Lỗi khi update_user: {e}")
            return False

    @staticmethod
    def delete_user(user_id):
        try:
            db.collection("users").document(user_id).delete()
            return True
        except Exception as e:
            print(f"❌ Lỗi khi delete_user: {e}")
            return False

    @staticmethod
    def get_all_users():
        try:
            return [{**doc.to_dict(), "id": doc.id} for doc in db.collection("users").stream()]
        except Exception as e:
            print(f"❌ Lỗi khi get_all_users: {e}")
            return []
