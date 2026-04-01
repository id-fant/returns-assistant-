# Returns Assistant API

A Django REST API that processes eCommerce return requests and uses Google Gemini to automatically classify them as **APPROVE**, **EXCHANGE**, or **ESCALATE**.

Built to demonstrate Django REST Framework + LLM integration.

---

## Tech Stack

- **Django 4.2** — web framework
- **Django REST Framework** — API layer
- **Google Gemini API** — AI decision engine
- **SQLite** — lightweight database (built into Python, no setup needed)
- **python-dotenv** — environment variable management

---

## Setup

### 1. Clone and create a virtual environment
```bash
git clone <your-repo-url>
cd returns_assistant
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API key
Edit the `.env` file:
```
GEMINI_API_KEY=your_actual_key_here
```
Get a free key at: https://aistudio.google.com/app/apikey

### 4. Run migrations and start the server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## API Endpoints

### `POST /api/returns/`
Submit a new return request. The AI automatically decides the outcome.

**Request body:**
```json
{
  "order_id": "ORD-1042",
  "product_name": "Running Shoes Size 10",
  "reason": "Received wrong size, ordered size 9"
}
```

**Response:**
```json
{
  "id": 1,
  "order_id": "ORD-1042",
  "product_name": "Running Shoes Size 10",
  "reason": "Received wrong size, ordered size 9",
  "ai_decision": "EXCHANGE",
  "ai_explanation": "Customer received incorrect size, a replacement with the correct size is appropriate.",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### `GET /api/returns/`
List all return requests.

### `GET /api/returns/<id>/`
Fetch a specific return request by ID.

---

## Testing with curl

```bash
# Damaged item — should APPROVE
curl -X POST http://localhost:8000/api/returns/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "ORD-001", "product_name": "Bluetooth Headphones", "reason": "Item arrived with cracked casing and does not power on"}'

# Wrong size — should EXCHANGE
curl -X POST http://localhost:8000/api/returns/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "ORD-002", "product_name": "Cotton T-Shirt", "reason": "Ordered medium but received large"}'

# Vague reason — should ESCALATE
curl -X POST http://localhost:8000/api/returns/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "ORD-003", "product_name": "Laptop Stand", "reason": "I just dont want it anymore"}'
```

---

## Django Admin Panel

Create a superuser to explore the admin UI:
```bash
python manage.py createsuperuser
```
Then visit: http://localhost:8000/admin/

---

## Project Structure

```
returns_assistant/
├── manage.py                     # Django CLI entry point
├── requirements.txt
├── .env                          # Your API keys (never commit this)
├── returns_assistant/            # Project config
│   ├── settings.py
│   └── urls.py
└── returns/                      # The app
    ├── models.py                 # Database schema
    ├── serializers.py            # JSON input/output shaping
    ├── views.py                  # Request handling logic
    ├── urls.py                   # URL routing
    ├── ai_engine.py              # Gemini integration + prompt
    └── admin.py                  # Admin panel config
```
