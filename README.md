# Python License Server

A simple **FastAPI-based license key validation server** you can deploy on Render.

## 🚀 Features
- Admin login page
- Generate & revoke license keys
- Validate keys via API
- Secure with environment variables

## 🔧 Deployment (Render)
1. Push this repo to GitHub.
2. Go to [Render](https://render.com) → New → Web Service.
3. Connect your repo.
4. Set build & start commands:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render:
   - `SECRET_KEY` = your secret string
   - `ADMIN_PASSWORD` = your admin password

Your server will be live at `https://your-app.onrender.com/`
