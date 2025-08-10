<p align="center">
  <img src="https://dotcoder.site/static/icons/dotcoder-logo.png" alt="DotCoder Logo" width="150"/>
</p>

<h1 align="center">DotCoder</h1>
<p align="center"><em>Prompt. Code. Done.</em></p>

---

## 🚀 Overview
**DotCoder** is an **AI-powered coding tool** that lets you create **websites, games, and more** using **HTML, CSS, Tailwind CSS, JavaScript, and React** - all with a **live preview**.

You can **edit your code by writing natural language prompts**, instantly generating or modifying code with AI assistance.

DotCoder also allows you to **collaborate in real time** and **publish your work** for other users around the world to view, interact with, and build upon.
 

Whether you're a beginner or an advanced developer, DotCoder is here to make your coding journey smoother.  

🌐 **Website:** [https://dotcoder.site](https://dotcoder.site)  

---

## ✨ Features

- 🖋 **Clean Editor UI** – Syntax highlighting for better readability.  
- ⚡ **Instant Execution** – Write and run your code in seconds.  

- 🔗 **Sharable Snippets** – Share your code via unique links.  
- 📱 **Responsive Design** – Works on desktops, tablets, and smartphones.  
- 🎨 **Dark & Light Modes** – Code your way, day or night.  

---

## 🤖 AI Features & Tools

- 🔍 **Search Google** – Find relevant information, documentation, and resources directly from the platform.  
- 📂 **Search GitHub Repositories** – Discover and fetch open-source code with direct repository links.  
- 📄 **Get Content / Code for Public Host Files** – Retrieve and integrate publicly available code or content into your projects instantly.  

---
## 🛠 Technologies Used

- **Frontend:** HTML, CSS, Tailwind CSS, JavaScript  
- **Backend:** Python ( Flask )
- **AI:** Google Gemini-based models for code generation and natural language processing 
- **AI Framework:** LangChain for advanced prompt chaining and AI workflow management
- **Database:** Firebase Realtime Database (with secure rules)
- **Authentication:** Firebase Authentication

---

## 📷 DotCoder Screenshots  

<p>
  <a href="https://dotcoder.site/static/pictures/dotcoder-pic-1.png" target="_blank" rel="noopener noreferrer">
    <img src="https://dotcoder.site/static/pictures/dotcoder-pic-1.png" alt="DotCoder Image 1" width="400" style="margin-right:10px;" />
  </a>
  <a href="https://dotcoder.site/static/pictures/dotcoder-pic-3.png" target="_blank" rel="noopener noreferrer">
    <img src="https://dotcoder.site/static/pictures/dotcoder-pic-3.png" alt="DotCoder Image 3" width="400" style="margin-right:10px;" />
  </a>
  <a href="https://dotcoder.site/static/pictures/dotcoder-pic-2.png" target="_blank" rel="noopener noreferrer">
    <img src="https://dotcoder.site/static/pictures/dotcoder-pic-2.png" alt="DotCoder Image 2" width="400" style="margin-right:10px;" />
  </a>
  <a href="https://dotcoder.site/static/pictures/dotcoder-pic-4.png" target="_blank" rel="noopener noreferrer">
    <img src="https://dotcoder.site/static/pictures/dotcoder-pic-4.png" alt="DotCoder Image 4" width="400" />
  </a>
</p>


---

# 🎬  DotCoder Demo Video

<video width="600" controls>
  <source src="https://dotcoder.site/static/videos/dotcoder-demo-video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

**Video link:** [DotCoder Demo Video](https://dotcoder.site) 

---

## 🛠 Installation (Local Development)

```bash
# Clone the repository
git clone https://github.com/Abdullah9779/dotcoder.git
cd dotcoder

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```
---

# 📜 DotCoder Firebase Realtime Database Rules

```json
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "auth != null && auth.uid === $uid",
        ".write": "auth != null && auth.uid === $uid"
      }
    },
    "usernames": {
      "$username": {
        ".read": true,
        ".write": "auth != null && newData.child('local_id').val() === auth.uid"
      }
    },
    "live_projects": {
      "$uid": {
        ".read": "auth != null && auth.uid === $uid",
        ".write": "auth != null && auth.uid === $uid"
      }
    },
    "all_user_projects": {
      ".read": "auth != null",
      "$projectKey": {
        ".write": "auth != null"
      }
    }
  }
}
```
## ⚙️ Configuration Files

### `config.json`

This file contains the Firebase configuration for your DotCoder client-side application. It includes your app's API keys and identifiers needed to initialize Firebase services like Authentication, Firestore, or Storage.

Example structure:

```json
{
  "apiKey": "YOUR_API_KEY_HERE",
  "authDomain": "your-app.firebaseapp.com",
  "projectId": "your-app",
  "storageBucket": "your-app.appspot.com",
  "messagingSenderId": "YOUR_SENDER_ID",
  "appId": "YOUR_APP_ID"
}
```

### `dotcoder-dev-sdk.json`

This file contains the Firebase Admin SDK service account credentials. It is used on your backend server to securely authenticate and interact with Firebase services with full administrative privileges (e.g., managing users, accessing Firestore securely).

> **Warning:** This file holds sensitive private keys. Never expose it publicly or commit it to public repositories.



Example structure:

```json
{
  "type": "service_account",
  "project_id": "dotcoder-demo",
  "private_key_id": "abcdef1234567890abcdef1234567890abcdef12",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEv...YourPrivateKeyHere...IDAQAB\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-demo@dotcoder-demo.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-demo%40dotcoder-demo.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

```
---

**LICENSE:** [Apache License 2.0](https://github.com/Abdullah9779/Dotcoder/blob/main/LICENSE)
