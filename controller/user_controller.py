from model.user_model import UserModel
from config.security import hash_password
class UserController:
    def login(self, email, password):
        user = UserModel.get_user_by_username_or_email(email)
        if user and user["password"] == hash_password(password):
            return user
        return None

    def get_user_by_email(self, email):
        return UserModel.get_user_by_email(email)

    def add_user(self, username, email, password, role="user"):
        return UserModel.add_user(username, email, password, role)

    def get_all_users(self):
        return UserModel.get_all_users()

    def delete_user(self, user_id):
        return UserModel.delete_user(user_id)

    def update_user(self, user_id, data):
        return UserModel.update_user(user_id, data)
