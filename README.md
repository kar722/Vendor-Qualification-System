# 📊 Vendor Qualification System 🔍
A lightweight semantic search engine for evaluating and ranking software vendors based on how well they match a user’s specified capabilities. Built with FastAPI and SBERT.
---

## Project Approach

### 1. Data Processing
- The system processes a CSV file containing a single software category: `"CRM Software"`.
- Necessary fields are extracted: `product_name`, `main_category`, `Features`, `rating`, and `reviews_count`.
- The `Features` column, stored as a nested list of dictionaries, is parsed using `ast.literal_eval` to extract feature `name` values into a clean string (`parsed_features`) for semantic matching.

---

### 2. Similarity Scoring & Matching

#### **TF-IDF (initial baseline)**
- Initial implementation utilized TF-IDF with cosine similarity via `sklearn`.
- While functional, the approach failed to capture semantically similar phrases (e.g., `"workflow automation"` ≠ `"process management"`).
- Score distribution remained narrow, with top matches often being shallow.

#### **SBERT (final solution)**
- Implementation switched to `sentence-transformers` (`all-MiniLM-L6-v2`) for semantic embeddings.
- Results showed better score distribution and improved accuracy.
- An exact match boost (+0.05) was added for capabilities matching feature names exactly — resolving borderline cases and ensuring optimal performance for literal queries.

#### Thresholding
- Threshold testing ranged from 0.6 to 0.3.
- Final SBERT similarity threshold of 0.30 was selected to accommodate useful but semantically looser matches while filtering noise.

---

### 3. Ranking System

The ranking system combines multiple trust and relevance metrics:

- `similarity_score` (semantic feature match)
- `rating` (normalized to 0–1)
- `review_count` (log-transformed and scaled)

Initial testing used a 50/30/20 split, followed by optimization via grid search. The final weights were determined as:
```
final_score = 0.4 * similarity_score + 0.2 * normalized_rating + 0.4 * log_normalized_reviews
```

This configuration provides optimal separation between strong and weak vendors, particularly when similarity scores are tightly clustered.

---

### 4. FastAPI Endpoint

The system implements a `/vendor_qualification` endpoint using FastAPI. Example request format:

```json
{
  "software_category": "CRM Software",
  "capabilities": ["workflow capability", "access management"]
}
```

Response includes:
- Top 10 vendors
- similarity_score, rating, reviews_count, final_score
- exact_match flag for transparency

The API handles:
- Invalid categories (with suggested valid options)
- No relevant vendors (filtered by score)
- JSON serialization of ranking output

---

## Challenges Encountered
- TF-IDF limitations: Underperformance on short feature names and synonym-heavy capabilities.
- Parsing Features column: Required robust handling of nested data and malformed values.
- FastAPI debugging: A 404 error was initially masked as a 500 due to generic Exception handling overriding FastAPI's HTTPException. Resolution involved allowing HTTPException to propagate naturally.

## Possible Future Improvements
- Integration of OpenAI Embeddings as a multilingual, cloud-scale alternative
- Implementation of SBERT vector caching for improved production response times
- Addition of fuzzy matching or autocomplete for user-entered capabilities
- Development of a frontend interface for the API

## 🚀 How to Run

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
