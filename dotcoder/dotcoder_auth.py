import os
import json
import pyrebase
import firebase_admin
from firebase_admin import credentials
from datetime import datetime

class DotCoderAuth:
    def __init__(self):
        with open("config.json", "r") as f:
            config = json.load(f)
        cred = credentials.Certificate("dotcoder-dev-sdk.json")

        firebase_admin.initialize_app(cred)
        firebase = pyrebase.initialize_app(config)

        self.auth = firebase.auth()
        self.db = firebase.database()
    

    def _create_profile_picture(self, user_id: str, default_picture: bool = False, image: bytes = None):
        """Save a profile picture (default or custom image) for the user and return its URL."""
        import requests
        

        if user_id is None:
            return None

        save_path = f"static/profile/profile_image/{user_id}.png"
        os.makedirs("static/profile/profile_image", exist_ok=True)

        if default_picture:
            default_picture_url = "https://cdn.pixabay.com/photo/2023/02/18/11/00/icon-7797704_1280.png"
            with open(save_path, "wb") as f:
                f.write(requests.get(default_picture_url).content)

        if image is not None:
            with open(save_path, "wb") as f:
                f.write(image)

        if os.path.exists(save_path):
            return f"http://127.0.0.1:5000/static/profile/profile_image/{user_id}.png"
        else:
            return None
    

    def sign_up(self, name: str, username: str, email: str, password: str):
        """Sign up a new user with email and password, create a profile, and store user data in the database."""
        try:
            user = self.auth.create_user_with_email_and_password(
                email=email,
                password=password
            )

            self.auth.send_email_verification(user["idToken"])
            if not user:
                return {"error": "User creation failed"}

            profile_picture = self._create_profile_picture(user["localId"], default_picture=True)

            self.auth.update_profile(user["idToken"], display_name=name, photo_url=profile_picture)

            created_at = datetime.now().isoformat()

            self.db.child("users").child(user["localId"]).set({
                "local_id": user["localId"],
                "name": name,
                "username": username,
                "email": email,
                "profile_picture": profile_picture,
                "created_at": created_at,
            }, token=user["idToken"])

            self.db.child("usernames").child(username).set({
                "local_id": user["localId"],
                "name": name,
                "email": email,
                "profile_picture": profile_picture,
                "created_at": created_at,
            }, token=user["idToken"])

            return user

        except Exception as e:
            message = json.loads(e.args[1])["error"]["message"]
            if message == "EMAIL_EXISTS":
                return {"error": "Email already in use"}
            elif message == "INVALID_EMAIL":
                return {"error": "Invalid email"}
            elif "WEAK_PASSWORD" in message:
                return {"error": "Password should be at least 8 characters"}
            else:
                return {"error": message}

    def sign_in(self, email: str, password: str):
        """Log in a user with email and password."""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            user_info = self.auth.get_account_info(user["idToken"])
            if user_info["users"][0]["emailVerified"]:
                return user
            else:
                return {"error": "Email is not verified"}
        except Exception as e:
            message = json.loads(e.args[1])["error"]["message"]
            if message == "EMAIL_NOT_FOUND":
                return {"error": "Email not found"}
            elif message == "INVALID_PASSWORD":
                return {"error": "Invalid password"}
            elif message == "TOO_MANY_ATTEMPTS_TRY_LATER":
                return {"error": "Too many attempts, try later"}
            elif message == "INVALID_LOGIN_CREDENTIALS":
                return {"error": "Invalid login credentials"}
            elif message == "USER_DISABLED":
                return {"error": "User account is disabled"}
            else:
                return {"error": message}

    def username_exists(self, username: str):
        """Check if a username already exists."""
        if username:
            return self.db.child("usernames").child(username).get().val() is not None
        else:
            return None

    def verify_email(self, email: str, password: str):
        """Send a verification email to the user."""
        user = self.sign_in(email, password)
        if user:
            if isinstance(user, dict) and 'error' in user:
                return {'message': user['error']}
            else:
                id_token = user["idToken"]
                try:
                    user_info = self.auth.get_account_info(id_token)
                    if not user_info["users"][0]["emailVerified"]:
                        self.auth.send_email_verification(id_token)
                        return {"message": True}
                    else:
                        return {"error": "Email is already verified"}
                except Exception as e:
                    message = json.loads(e.args[1])["error"]["message"]
                    if message == "INVALID_EMAIL":
                        return {"error": "Invalid email."}
                    elif message == "INVALID_ID_TOKEN":
                        return {"error": "Invaild OR Wrong email."}
                    elif message == "TOO_MANY_ATTEMPTS_TRY_LATER":
                        return {"error": "Too many attempts, try later"}
                    elif message == "EMAIL_NOT_FOUND":
                        return {"error": "Email not found"}
                    elif message == "EMAIL_ALREADY_VERIFIED":
                        return {"error": "Email is already verified"}
                    else:
                        return {"error": message}
                    

    def refresh_token(self, refresh_token: str):
        """Refresh the user's authentication token."""
        try:
            user = self.auth.refresh(refresh_token)
            return user
        except Exception as e:
            return None

    def account_info(self, id_token):
        """Retrieve account information for a user."""
        try:
            account_info = self.auth.get_account_info(id_token)
            return account_info
        except Exception as e:
            return None

    def reset_password(self, email: str):
        """Send a password reset email to the user."""
        try:
            self.auth.send_password_reset_email(email)
            return {"message": True}
        except Exception as e:
            message = json.loads(e.args[1])["error"]["message"]
            if message == "EMAIL_NOT_FOUND":
                return {"error": "Email not found"}
            elif message == "INVALID_EMAIL":
                return {"error": "Invalid email"}
            else:
                return {"error": message}
        
    def delete_account(self, id_token: str):
        """Delete a user's account."""
        try:
            user_info = self.auth.get_account_info(id_token)
            user_id = user_info["users"][0]["localId"]
            self.db.child("users").child(user_id).remove(token=id_token)
            self.db.child("usernames").order_by_child("user_id").equal_to(user_id).get().each(lambda x: x.ref.remove(token=id_token))
            self.auth.delete_user(id_token)
            return True
        except Exception as e:
            return False

    def update_profile(self, id_token: str, name: str = None, profile_picture: str = None):
        """Update the user's profile information."""
        try:
            user_info = self.auth.get_account_info(id_token)
            user_id = user_info["users"][0]["localId"]

            user_data = self.db.child("users").child(user_id).get(token=id_token).val()

            updates = {}

            if name:
                updates["name"] = name

            if profile_picture is not None:
                image_path = self._create_profile_picture(user_id, image=profile_picture)
                updates["profile_picture"] = image_path

            self.db.child("users").child(user_id).update(updates, token=id_token)
            self.db.child("usernames").child(user_data["username"]).update(updates, token=id_token)

            self.auth.update_profile(id_token, display_name=updates.get("name"), photo_url=updates.get("profile_picture"))

            return True
        except Exception as e:
            return False

    def get_user_by_id_token(self, token: str = None, get_username_data: bool = False, get_live_projects_data: bool = False):
        """Retrieve user information by local ID."""
        try:
            get_local_id_data = True
            data = {}
            if get_local_id_data:
                try:
                    local_id = self.account_info(token)["users"][0]["localId"]
                    user_data = self.db.child("users").child(local_id).get(token=token).val()
                    data["local_id_data"] = user_data if user_data else {}
                except:
                    data["local_id_data"] = {}

            if get_username_data:
                try:
                    username_data = self.db.child("usernames").child(data.get("local_id_data", {}).get("username")).get(token=token).val()
                    data["username_data"] = username_data if username_data else {}
                except:
                    data["username_data"] = {}

            if get_live_projects_data:
                try:
                    live_projects = dict(self.db.child("live_projects").child(local_id).child("live_project").get(token=token).val())
                    data["live_projects_data"] = live_projects if live_projects else {}
                except:
                    data["live_projects_data"] = {}

            return data
        except Exception as e:
            return None

    def get_user_by_username(self, username: str, token: str = None):
        """Retrieve user information by username."""
        try:
            user_data = self.db.child("usernames").child(username).get(token=token).val()
            if user_data:
                user_info = self.db.child("users").child(user_data["user_id"]).get(token=token).val()
                return user_info
            else:
                return None
        except Exception as e:
            return None
    

    def add_live_project(self, id_token: str, local_id: str, project_url, username: str, code: str, description: str):
        """Add a live project for the user."""
        try:
            url = f"http://127.0.0.1:5000/live/{username}/{project_url}"
            created_at = datetime.now().isoformat()
            self.db.child("live_projects").child(local_id).child("live_project").child(project_url).set({
                "project_url": project_url,
                "url": url,
                "timestamp": created_at,
                "description": description
            }, token=id_token)

            profile_picture = f"http://127.0.0.1:5000/static/profile/profile_image/{local_id}.png"

            self.db.child("all_user_projects").child(f"{username}--__SEP__--{project_url}").set({
                "project_url": project_url,
                "url": url,
                "timestamp": created_at,
                "username": username,
                "profile_picture": profile_picture,
                "description": description
            }, token=id_token)

            if not os.path.exists("static/live_projects"):
                os.makedirs("static/live_projects", exist_ok=True)

            if not os.path.exists(f"static/live_projects/{username}"):
                os.makedirs(f"static/live_projects/{username}")

            with open(f"static/live_projects/{username}/{project_url}.html", "wb") as file:
                file.write(code.encode("utf-8"))

            return True
        except Exception as e:
            return False
        
    def remove_project(self, token: str, project_url: str):
        """Remove a live project for the user."""
        try:
            data = self.get_user_by_id_token(token)
            username = data.get("local_id_data", {}).get("username")
            local_id = data.get("local_id_data", {}).get("local_id")

            self.db.child("live_projects").child(local_id).child("live_project").child(project_url).remove(token=token)
            self.db.child("all_user_projects").child(f"{username}--__SEP__--{project_url}").remove(token=token)


            path = f"static/live_projects/{username}/{project_url}.html"
            if os.path.exists(path):
                os.remove(path)
                return True
            else:
                return True

        except Exception as e:
            return False
        
    def get_all_live_projects_data(self, token: str):
        try:
            projects_data = self.db.child("all_user_projects").get(token=token).val()
            return projects_data
        except Exception as e:
            return False

