from config.firebase_config import db
import hashlib

def hash_password(password: str) -> str:
    """Hàm mã hoá mật khẩu (SHA256)."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user():
    users_ref = db.collection("users")
    admin_doc = users_ref.document("admin").get()
    if admin_doc.exists:
        print("⚠️ Admin đã tồn tại, bỏ qua.")
        return

    admin_data = {
        "username": "admin",
        "password": hash_password("admin123"),  # 🔑 mật khẩu ban đầu
        "role": "admin",
        "email": "admin@coin.com",
        "created_at": firestore.SERVER_TIMESTAMP,
    }
    users_ref.document("admin").set(admin_data)
    print("✅ Đã tạo tài khoản admin thành công!")

if __name__ == "__main__":
    create_admin_user()
