# ReviewPilot
An event-driven AI code intelligence platform integrated with GitHub.


# 🚀 Local Development Setup

This project uses **FastAPI**, **Celery**, **Redis**, and **ngrok** for local development and async task processing.

Follow the steps below to get everything running locally.

---

## 📦 Prerequisites

Make sure you have installed:

* Python 3
* Docker
* pip / virtualenv

---

## ⚙️ 1. Start FastAPI Server

Run the FastAPI app locally:

```bash
fastapi dev main.py
```

Or if you're using uvicorn directly:

```bash
uvicorn main:app --reload
```

App will be available at:

```
http://127.0.0.1:8000
```

---

## 🌐 2. Expose Local Server using ngrok

Start ngrok to expose your FastAPI server:

```bash
ngrok http 8000
```

You’ll get a public URL like:

```
https://<random>.ngrok-free.app
```

Use this for webhooks or external integrations.

---

## 🐳 3. Run Redis using Docker

Start Redis container:

```bash
docker run -d -p 6379:6379 redis
```

This will run Redis locally on:

```
localhost:6379
```

---

## ⚡ 4. Start Celery Worker

Run Celery worker for background tasks:

```bash
celery -A app.core.celery_app worker --loglevel=info
```

## 🧠 Architecture Overview

* **FastAPI** → Handles API requests
* **Celery** → Processes async/background jobs
* **Redis** → Message broker + backend
* **ngrok** → Exposes local APIs to the internet

---

## 🧪 Common Issues

### Redis not starting?

Make sure Docker is running:

```bash
docker ps
```

---

### Celery not picking tasks?

* Verify Redis is running
* Check broker URL in `celery_app.py`

---

### ngrok URL not working?

* Ensure FastAPI server is running
* Confirm correct port (8000)

---

## 🏁 You're Good to Go!