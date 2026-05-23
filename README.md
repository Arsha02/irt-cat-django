# IRT-CAT Django

An adaptive quiz engine built on **Item Response Theory (IRT)**, the same psychometric model used in standardized tests, implemented as a Django REST API.

## Overview

This project is a **Computerized Adaptive Test (CAT)** engine built with Django REST Framework. Instead of giving everyone the same questions, it adapts in real-time after each answer, re-estimates the user's ability level (θ) and picks the next question that gives the most information about them.

Unlike traditional fixed-form tests, this approach requires only **10 questions** to produce an accurate ability estimate, because every question is chosen to be maximally informative for that specific user at that moment. The underlying IRT model is the same framework used in large-scale standardized assessments to measure latent traits like knowledge and aptitude.

Session state is managed server-side (responses, current question, theta, count, done flag), and the test ends after 10 questions, returning a final ability score (θ).

## Project Structure

```
irt/
├── cat/                        # Core CAT app
│   ├── engine.py               # IRT logic: estimate_theta(), next_item(), se()
│   ├── models.py               # Item model (item_id, a, b, c, correct_option)
│   ├── serializers.py          # ItemSerializer
│   ├── views.py                # test_api and reset_test endpoints
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── irt/                        # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── question_bank_100.json      # 100 items with IRT parameters (a, b, c)
├── import_questions.py         # Script to load item bank into DB
├── db.sqlite3
└── manage.py
```

## How the Engine Works (`engine.py`)

This is the core of the project. It implements the **3-Parameter Logistic (3PL) IRT model** entirely with NumPy.

### 1. Item Characteristic Curve
The probability of a correct response given ability θ:
```
P(θ) = c + (1 - c) / (1 + exp(-a * (θ - b)))
```
- `a` — discrimination (how well the item separates ability levels)
- `b` — difficulty (θ value where P ≈ 0.5)
- `c` — guessing (lower asymptote / chance probability)

### 2. Ability Estimation — `estimate_theta()`
Uses **Maximum Likelihood Estimation (MLE)** over a grid of 100 θ values from -3 to +3. For each candidate θ, it computes the log-likelihood of all responses so far with a `−0.5θ²` penalty to prevent ability estimates from diverging to extremes early in the test. The θ with the highest score is returned as the ability estimate.

### 3. Item Selection — `next_item()`
Selects the unanswered item with the **maximum Fisher information** at the current θ. Fisher information measures how precisely an item can estimate ability — higher information means the item is optimally targeted at the test-taker's level.

### 4. Standard Error — `se()`
Computes the standard error of the θ estimate as `1 / √(total_information)`.
## Setup

```bash
git clone https://github.com/Arsha02/irt-cat-django.git
cd irt-cat-django
pip install django djangorestframework numpy
python manage.py migrate
python manage.py shell < import_questions.py   # loads 100-item question bank
python manage.py runserver
```

## API

### `GET /api/test/`
Start the test or retrieve the current question.

**Response:**
```json
{
  "status": "ongoing",
  "progress": 1,
  "question": { "item_id": "42", "question": "...", "options": {...} }
}
```

### `POST /api/test/`
Submit an answer to the current question.

**Request body:**
```json
{ "q_id": "42", "ans": "B" }
```

**In-progress response:**
```json
{
  "status": "ongoing",
  "progress": 2,
  "question": { "item_id": "17", ... }
}
```

**Completed response** (after 10 answers):
```json
{
  "status": "completed",
  "final_score": 1.23,
  "total_items": 10
}
```

### `POST /api/reset/`
Clears the session and restarts the test.

```json
{ "status": "reset" }
```

## Testing with Postman

### 1. Start the Test
- Method: `GET`
- URL: `http://127.0.0.1:8000/api/test/`

### 2. Submit an Answer
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/test/`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{ "q_id": "42", "ans": "B" }
```

Repeat this step for each question. Progress increments with each correct submission until `total_items` reaches 10.

### 3. Reset the Test
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/reset/`

> **Note:** Postman persists session cookies automatically. Make sure **"Automatically follow redirects"** and **cookie handling** are enabled in Postman settings to maintain the session across requests.

## Stack
- Django + Django REST Framework
- NumPy
- SQLite

## Author
**Arsha02** — [github.com/Arsha02](https://github.com/Arsha02)
