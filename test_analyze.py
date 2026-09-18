import requests
import io

base_url = "http://localhost:8080"

# Register
requests.post(f"{base_url}/register", json={"username": "test_crash", "password": "123"})

# Login
resp = requests.post(f"{base_url}/api/login", json={"username": "test_crash", "password": "123"})
token = resp.json().get("access_token")

if token:
    headers = {"Authorization": f"Bearer {token}"}
    files = {"resume": ("resume.txt", io.BytesIO(b"I am a software engineer."), "text/plain")}
    data = {"job_description": "We need a fast-paced developer."}
    
    res = requests.post(f"{base_url}/analyze", headers=headers, files=files, data=data)
    print("Status:", res.status_code)
    print("Response:", res.text)
else:
    print("Failed to login", resp.text)
