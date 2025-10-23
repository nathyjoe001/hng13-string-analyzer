# 🧠 String Analyzer API — HNGi13 Stage 1 Backend Task

A RESTful API that analyzes strings and stores their computed properties.  
Built with **Django REST Framework** and hosted on **Railway**.

---

## 🚀 Live API Base URL

👉 **https://string-analyzer-production.up.railway.app/**

---

## 🧰 Tech Stack

- **Python 3.12**
- **Django 5**
- **Django REST Framework (DRF)**
- **drf-yasg** – Swagger/OpenAPI documentation
- **django-cors-headers**
- **gunicorn + whitenoise** – for production
- **Railway PostgreSQL** – for database
- **dotenv** – for environment variable management

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/hng13-string-analyzer.git
cd hng13-string-analyzer
2️⃣ Create Virtual Environment & Install Dependencies
bash
Copy code
python -m venv venv
venv\Scripts\activate       # On Windows
# source venv/bin/activate  # On macOS/Linux

pip install -r requirements.txt

3️⃣ Run Migrations and Start Server
bash
Copy code
python manage.py migrate
python manage.py runserver
The app should now be running on
👉 http://127.0.0.1:8000/

🧮 API Endpoints
1. Analyze String
POST /strings

Request:

json
Copy code
{
  "value": "string to analyze"
}
Response:

json
Copy code
{
  "id": "sha256_hash_value",
  "value": "string to analyze",
  "properties": {
    "length": 16,
    "is_palindrome": false,
    "unique_characters": 12,
    "word_count": 3,
    "sha256_hash": "abc123...",
    "character_frequency_map": {
      "s": 2,
      "t": 3
    }
  },
  "created_at": "2025-08-27T10:00:00Z"
}
2. Get Specific String
GET /strings/{string_value}

Response:

json
Copy code
{
  "id": "sha256_hash_value",
  "value": "requested string",
  "properties": { ... },
  "created_at": "2025-08-27T10:00:00Z"
}
3. Get All Strings with Filters
GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a

Response:

json
Copy code
{
  "data": [ ... ],
  "count": 15,
  "filters_applied": {
    "is_palindrome": true,
    "min_length": 5,
    "max_length": 20,
    "word_count": 2,
    "contains_character": "a"
  }
}
4. Natural Language Filter
GET /strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings

Response:

json
Copy code
{
  "data": [ ... ],
  "count": 3,
  "interpreted_query": {
    "original": "all single word palindromic strings",
    "parsed_filters": {
      "word_count": 1,
      "is_palindrome": true
    }
  }
}
5. Delete a String
DELETE /strings/{string_value}

Response:
204 No Content

🧪 Testing Locally
You can test endpoints using:

Postman

cURL

or directly through the Swagger Docs at
👉 http://127.0.0.1:8000/swagger/
or
👉 https://string-analyzer-production.up.railway.app/swagger/

🧩 Environment Variables
Variable	Description
SECRET_KEY	Django secret key
DEBUG	Set to False in production
ALLOWED_HOSTS	Allowed hostnames
DB_NAME	Database name
DB_USER	Database user
DB_PASSWORD	Database password
DB_HOST	Database host
DB_PORT	Database port

📦 Dependencies
Run:

bash
Copy code
pip freeze > requirements.txt
Ensure the following are included:

php
Copy code
Django
djangorestframework
drf-yasg
django-cors-headers
gunicorn
whitenoise
psycopg2-binary
python-dotenv

👤 Author
Name: Joseph Akpan
Email: akpannath@yahoo.com
Stack: Python (Django)
HNGi13 Username: JosephA

