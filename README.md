# 📊 Vendor Qualification System 🔍
A lightweight semantic search engine for ranking software vendors based on user-specified capabilities. Built with FastAPI and SBERT.
---

## 🚀 Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/your-username/vendor-qualification-system.git
```
```
cd vendor-qualification-system
```
### 2. Set up the virtual environment
```bash
python -m venv venv
```
Mac
```
source venv/bin/activate
```
Windows
```
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the API
```bash
uvicorn app.main:app --reload
```

### 5. Test the endpoint
Curl
```bash
curl -X POST http://localhost:8000/vendor_qualification \
-H "Content-Type: application/json" \
-d '{
  "software_category": "CRM Software",
  "capabilities": ["workflow capability", "access management"]
}'
```
Or Postman
- Method: ```POST```
- URL: ```http://127.0.0.1:8000/vendor_qualification```
- Headers:

| Key    | Value |
| -------- | ------- |
| Content-Type  | application/json    |

- Click the Body tab, select raw, and set the format to ```JSON```.
```
{
  "software_category": "CRM Software",
  "capabilities": ["workflow capability", "access management"]
}
```

Or Open Swagger UI at (in your browser):
```
http://127.0.0.1:8000/docs
```
