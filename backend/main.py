from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
import shutil
from datetime import datetime

app = FastAPI(title="NaviHab Deploy API")

sites_db = {}
connections_db = {}

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/agent-manifest")
def agent_manifest():
    return {"version": "1.0.0", "name": "navihab-deploy-skill"}

@app.post("/api/v1/agent-connections")
def create_connection():
    code = str(uuid.uuid4())[:8]
    connections_db[code] = {"status": "pending", "token": None}
    connect_url = f"http://localhost:8080/?code={code}"
    return {
        "code": code,
        "connect_url": connect_url,
        "poll_url": f"/api/v1/agent-connections/{code}"
    }

@app.get("/api/v1/agent-connections/{code}")
def check_connection(code: str):
    conn = connections_db.get(code)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return conn

@app.post("/api/v1/agent-connections/{code}/approve")
def approve_connection(code: str):
    conn = connections_db.get(code)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    token = str(uuid.uuid4())
    conn["status"] = "approved"
    conn["token"] = token
    return {"status": "approved", "token": token}

@app.post("/api/v1/sites")
async def deploy_site(
    name: str = Form(...),
    files: list[UploadFile] = File(...)
):
    site_id = f"site-{uuid.uuid4().hex[:8]}"
    site_dir = f"./sites/{site_id}"
    os.makedirs(site_dir, exist_ok=True)
    
    for file in files:
        file_path = os.path.join(site_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    sites_db[site_id] = {
        "id": site_id,
        "name": name,
        "status": "active",
        "url": f"https://{site_id}.navihab.local",
        "created_at": datetime.now().isoformat()
    }
    return sites_db[site_id]

@app.get("/api/v1/sites")
def list_sites():
    return list(sites_db.values())

@app.get("/api/v1/sites/{site_id}")
def get_site(site_id: str):
    if site_id not in sites_db:
        raise HTTPException(status_code=404, detail="Site not found")
    return sites_db[site_id]

@app.delete("/api/v1/sites/{site_id}")
def delete_site(site_id: str):
    if site_id not in sites_db:
        raise HTTPException(status_code=404, detail="Site not found")
    site_dir = f"./sites/{site_id}"
    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)
    del sites_db[site_id]
    return {"status": "deleted"}

os.makedirs("./sites", exist_ok=True)
app.mount("/sites", StaticFiles(directory="sites"), name="sites")
