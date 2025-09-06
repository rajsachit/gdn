import os
import hashlib
import base64
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

licenses = {}

def generate_license_key(email: str) -> str:
    raw = f"{email}:{SECRET_KEY}"
    hashed = hashlib.sha256(raw.encode()).digest()
    return base64.urlsafe_b64encode(hashed)[:20].decode()

def validate_license(email: str, key: str) -> bool:
    return licenses.get(email) == key

def is_logged_in(request: Request) -> bool:
    return request.session.get("logged_in", False)

def require_login(request: Request):
    if not is_logged_in(request):
        raise HTTPException(status_code=401, detail="Not authenticated")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["logged_in"] = True
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    require_login(request)
    return templates.TemplateResponse("dashboard.html", {"request": request, "licenses": licenses})

@app.post("/add_license")
async def add_license(request: Request, email: str = Form(...)):
    require_login(request)
    key = generate_license_key(email)
    licenses[email] = key
    return RedirectResponse("/dashboard", status_code=302)

@app.post("/revoke_license")
async def revoke_license(request: Request, email: str = Form(...)):
    require_login(request)
    licenses.pop(email, None)
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/validate")
async def validate(email: str, license_key: str, request: Request):
    client_ip = request.client.host
    if validate_license(email, license_key):
        return {"status": "valid", "email": email, "client_ip": client_ip}
    raise HTTPException(status_code=403, detail="Invalid or revoked license")
