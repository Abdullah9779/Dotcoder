from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from dotcoder_agent import DotCoderAgent
from dotcoder.chat_enhancer import ChatEnhancer
from dotcoder.dotcoder_auth import DotCoderAuth
from datetime import timedelta
from datetime import datetime
import os
import base64
import time
import requests

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=30)

chat_enhancer = ChatEnhancer()
auth = DotCoderAuth()

# **************** Functions ***************

def get_valid_token():
    id_token = session.get('idToken', None)
    refresh_token = session.get('refresh_token', None)
    if id_token and refresh_token:
        is_valid = auth.account_info(id_token)
        if is_valid is not None:
            return id_token
        else:
            refresh_user = auth.refresh_token(refresh_token)
            if refresh_user is not None:
                session.permanent = True
                session['idToken'] = refresh_user["idToken"]
                session["refresh_token"] = refresh_user["refreshToken"]
                time.sleep(2)
                return refresh_user["idToken"]
            else:
                return None
    else:
        return None
    
def verify_recaptcha(response_token):
    secret_key = os.getenv("Google_reCAPTCHA")
    payload = {
        'secret': secret_key,
        'response': response_token
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    result = r.json()
    return result.get('success', False)


    
@app.template_filter('time_ago')
def time_ago(time_string):
    """
    Returns how much time has passed since the given ISO 8601 time string.
    """
    given_time = datetime.fromisoformat(time_string)
    now = datetime.now()
    time_diff = now - given_time

    days = time_diff.days
    seconds = time_diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if days > 0:
        return f"{days} day(s) ago"
    elif hours > 0:
        return f"{hours} hour(s) ago"
    elif minutes > 0:
        return f"{minutes} minute(s) ago"
    else:
        return "Just now"
    
# **************** Privacy Policy -- Terms & Conditions ***************

@app.route('/privacy-policy')
def privacy_policy():
    return render_template("privacy_policy.html")

@app.route('/terms-conditions')
def terms_conditions():
    return render_template("terms_conditions.html")
    
# **************** Project Gallery End point ***************

@app.route("/live-projects")
def all_project_projects():
    token = get_valid_token()
    if token is None:
        return redirect(url_for("sign_in"))
    
    live_projects_data = auth.get_all_live_projects_data(token)

    return render_template('all_live_projects.html', live_projects_data=live_projects_data)


# **************** Page Not Found End point ***************

@app.errorhandler(404)
def page_not_found(e):
    return render_template('page_not_found.html'), 404


# **************** Chat Page end point ***************

@app.route('/chat')
def chat():
    token = get_valid_token()
    if token is None:
        return redirect(url_for("sign_in"))
    
    return render_template('chat_page.html') 

# **************** Dashboard Langing page ***************

@app.route("/landing")
def landing_page():
    token = get_valid_token()
    if token is not None:
        return redirect(url_for("dashboard"))
    
    return render_template("langing_page.html")

@app.route('/')
def home():
    token = get_valid_token()
    if token is None:
        return redirect(url_for("landing_page"))
    return redirect(url_for("dashboard"))

@app.route('/dashboard')
def dashboard():
    id_token = get_valid_token()
    if id_token is None:
        return redirect(url_for("sign_in"))
    
    user_data = auth.get_user_by_id_token(id_token, get_live_projects_data=True)

    return render_template('dashboard.html', user_data=user_data)

# **************** visit Live project End Point ***************

@app.route('/live/<path:url_path>')
def view_live_project(url_path):
    if url_path:
        file_path = f"static/live_projects/{url_path}.html"
        
        if os.path.exists(file_path):
            directory = os.path.join(app.root_path, 'static', 'live_projects')
            filename = f"{url_path}.html"
            return send_from_directory(directory, filename)
        else:
            return jsonify({"message": f"No project found on this address {url_path}"}), 404
        

# **************** Download Project End point ***************

@app.route("/api/download-project", methods=["POST"])
def download_project():
    token = get_valid_token()
    if token is None:
        return redirect(url_for("sign_in"))
    
    data = request.get_json()

    project_url = data.get("project_url")
    username = data.get("username")
    
    if username is None or project_url is None:
        return {"error": "Invalid Data"}, 400

    filename = f"{project_url}.html"
    directory = os.path.join(app.root_path, "static", "live_projects", username)

    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}, 404

    return send_from_directory(directory=directory, path=filename, as_attachment=True)



# **************** Delete Project End point ***************

@app.route('/api/deleate-project', methods=["POST"])
def delete_project():
    token = get_valid_token()
    if token is None:
        return redirect(url_for("sign_in"))
    
    data = request.get_json()
    project_url = data.get("project_url")

    if project_url is None:
        return jsonify({"message": "Invalid Data"})

    is_deleted = auth.remove_project(token, project_url)
    if is_deleted:
        return jsonify({"message": f'Project "{project_url}" is deleted successfully!'})
    else:
        return jsonify({"message": f'project "{project_url}" is not deleted!'})


# **************** Make the project live end point ***************

@app.route('/api/make-project-live', methods=['POST'])
def make_project_live():
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
    
    id_token = get_valid_token()
    if id_token is None:
        return redirect(url_for("sign_in"))
    
    data = request.get_json()
    project_url = data.get("project_url")
    code = data.get("code")
    description = data.get("description")

    if project_url is None or code is None:
        return jsonify({'message': 'Invalid input data'}), 400
    
    user_data = auth.get_user_by_id_token(id_token, get_live_projects_data=True)

    if user_data is None:
        return jsonify({"message": "Data is not found!"})
    
    if project_url in user_data.get("live_projects_data", {}):
        return jsonify({"message": f'Project with name "{project_url}" is already exist.'})

    else:
        is_created = auth.add_live_project(
            id_token=id_token,
            local_id=user_data.get("local_id_data", {}).get("local_id"),
            project_url=project_url,
            username=user_data.get("local_id_data", {}).get("username"),
            code=code,
            description=description
        )

        if is_created:
            return jsonify({"message": "Project live"})
        else:
            return jsonify({"message": "Project is not live"})

# **************** Account Info Endpoint ***************

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
    
    id_token = get_valid_token()
    if id_token is None:
        return redirect(url_for("sign_in"))

    data = request.get_json()
    avatar = data.get('avatar')

    if avatar:
        try:
            image_data = base64.b64decode(avatar.split(',')[1])
        except Exception as e:
            return jsonify({'error': 'Invalid avatar data'}), 400

    user_info = auth.update_profile(id_token, data.get('full_name'), image_data if avatar else None)

    if user_info:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Failed to retrieve user information'}), 500


# **************** Reset Password Endpoint ***************

@app.route('/reset-password')
def reset_password():
    if get_valid_token() is not None:
        return redirect(url_for("dashboard"))
    return render_template('reset_password_page.html')

@app.route('/api/reset-password', methods=['POST'])
def reset_password_api():
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
    
    data = request.get_json()

    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    is_send = auth.reset_password(email)

    if is_send:
        if "error" in is_send:
            return jsonify({'message': is_send['error']}), 400
        else:
            return jsonify({'message': True}), 200
    else:
        return jsonify({'message': 'Failed to send password reset email'}), 500


# **************** verify email endpoint ***************

@app.route('/verify-email')
def verify_email():
    if get_valid_token() is not None:
        return redirect(url_for("dashboard"))
    return render_template('verify_email_page.html')


@app.route('/get-verify-email-link')
def get_verify_email_link_page():
    if get_valid_token() is not None:
        return redirect(url_for("dashboard"))
    return render_template('get_verify_email_link.html')


@app.route('/api/get-verify-email-link', methods=['POST'])
def get_verify_email_link():
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
    
    data = request.get_json()

    email = data.get('email')
    password = data.get("password")

    if not email and not password:
        return jsonify({'error': 'Email is required'}), 400
    
    is_send = auth.verify_email(email, password)

    if is_send:
        if "error" in is_send:
            return jsonify({'message': is_send['error']}), 400
        else:
            return jsonify({'message': True}), 200
    else:
        return jsonify({'message': 'Invalid email not sent verification link.'}), 500


# **************** Sign Up Endpoint ***************

@app.route('/sign-up')
def sign_up():
    if get_valid_token() is not None:
        return redirect(url_for("dashboard"))
    return render_template('sign_up_page.html')

@app.route('/api/sign-up', methods=['POST'])
def sign_up_api():
    if request.method != 'POST':
        return jsonify({'message': 'Method not allowed'}), 405
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 400
    
    recaptcha_response = data.get('g-recaptcha-response')
    if not recaptcha_response or not verify_recaptcha(recaptcha_response):
        return jsonify({'message': 'reCAPTCHA verification failed. Please try again.'}), 400
    is_user_exists = auth.username_exists(data.get('username'))
    if is_user_exists:
        return jsonify({'message': 'Username already exists.'}), 400
    user = auth.sign_up(
        name=data.get('name'),
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password')
    )
    if isinstance(user, dict) and 'error' in user:
        return jsonify({'message': user['error']}), 400
    else:
        return jsonify({'message': True}), 201

# **************** Sign out Endpoint ***************

@app.route('/sign-out')
def sign_out():
    session.clear()
    return redirect(url_for("landing_page"))
    
# **************** Sign In Endpoint ***************

@app.route('/sign-in')
def sign_in():
    if get_valid_token() is not None:
        return redirect(url_for("dashboard"))
    return render_template('sign_in_page.html')

@app.route('/api/sign-in', methods=['POST'])
def sign_in_api():
    if request.method != 'POST':
        return jsonify({'message': 'Method not allowed'}), 405
    data = request.get_json()   
    if not data:
        return jsonify({'message': 'Invalid input'}), 400
    
    recaptcha_response = data.get('g-recaptcha-response')
    if not recaptcha_response or not verify_recaptcha(recaptcha_response):
        return jsonify({'message': 'reCAPTCHA verification failed. Please try again.'}), 400
    remember = data.get('remember_me', True) 
    user = auth.sign_in(
        email=data.get('email'),
        password=data.get('password')
    )
    if user:
        if isinstance(user, dict) and 'error' in user:
            return jsonify({'message': user['error']}), 400
        else:
            session.permanent = True
            session['idToken'] = user["idToken"]
            session["refresh_token"] = user["refreshToken"]
            return jsonify({'message': True}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 400

# **************** AI Response End Endpoint ***************

@app.route('/api/chat-data', methods=['POST'])
def get_data():
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
    
    token = get_valid_token()
    if token is None:
        return jsonify({'error': 'You are not authentic user. Try again'}), 500

    query = request.form.get('query')
    messages = request.form.getlist('messages')
    file = request.form.get('file')

    if not query or not messages:
        return jsonify({'error': 'Query and messages are required'}), 400

    ai_response = DotCoderAgent(query, messages)["output"]

    if ai_response is None:
        return jsonify({'error': 'Failed to get response from AI'}), 500
    return jsonify({'response': ai_response})


# **************** Chat Enhancer Endpoint ***************

@app.route('/api/enhance-prompt', methods=['POST'])
def enhance_prompt():
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
    
    token = get_valid_token()
    if token is None:
        return redirect(url_for("sign_in"))

    data = request.get_json()

    prompt = data.get('prompt') if isinstance(data, dict) else None
    conversation = data.get('conversation') if isinstance(data, dict) else []

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    if not isinstance(conversation, list):
        conversation = []

    enhanced_prompt = chat_enhancer.enhance_prompt(prompt, conversation)
    if enhanced_prompt:
        return jsonify({'enhanced_prompt': enhanced_prompt})
    else:
        return jsonify({'enhanced_prompt': ""})
    


# PWA manifest and service worker routes
@app.route('/sw.js')
def service_worker():
    return app.send_static_file('sw.js')

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')


if __name__ == '__main__':
    app.run(debug=True)

