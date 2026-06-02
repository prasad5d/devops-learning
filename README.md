# DevOps Learning App — Intern Guide

A hands-on Task Manager app built to teach core DevOps concepts from scratch.
Each folder and file in this project demonstrates a real DevOps practice.

---

## What You Will Learn

| Topic | Where it is in this project |
|---|---|
| Version Control (Git) | `.gitignore`, branching workflow below |
| Containerization | `Dockerfile` |
| Multi-service orchestration | `docker-compose.yml` |
| Reverse Proxy | `nginx/nginx.conf` |
| Environment Config | `.env.example` |
| CI/CD Pipeline | `.github/workflows/ci-cd.yml` |
| Automated Testing | `app/tests/test_app.py` |
| Health Checks | `/health` endpoint + Dockerfile HEALTHCHECK |
| Production vs Dev environments | `docker-compose.prod.yml` |

---

## Prerequisites

### On Windows
- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.12+](https://www.python.org/downloads/)
- [VS Code](https://code.visualstudio.com/)

### On Ubuntu 22.04 (recommended for learning — Docker runs natively)

```bash
# 1. Update packages
sudo apt update && sudo apt upgrade -y

# 2. Install Git and Python
sudo apt install -y git python3 python3-pip make curl

# 3. Install Docker Engine (NOT Docker Desktop)
sudo apt install -y ca-certificates gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 4. Run Docker without sudo (log out and back in after this)
sudo usermod -aG docker $USER
newgrp docker

# 5. Verify everything is installed
docker --version          # Docker version 24+
docker compose version    # Docker Compose version v2+
git --version
python3 --version
make --version
```

> **Note:** On Ubuntu use `python3` and `pip3` instead of `python` and `pip`.
> Update the Makefile `test` target if needed: replace `pip` with `pip3`.

---

## Quick Start (5 minutes)

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd devops-learning-app

# 2. Build and start everything
docker compose up -d

# 3. Open the app
# Browser → http://localhost        (via Nginx reverse proxy)
# Browser → http://localhost:5000   (direct Flask access, dev only)

# 4. Watch live logs
docker compose logs -f

# 5. Stop everything
docker compose down
```

---

## Project Structure

```
devops-learning-app/
│
├── app/                        # Python Flask application
│   ├── app.py                  # Main app — routes and logic
│   ├── requirements.txt        # Python dependencies
│   ├── templates/
│   │   └── index.html          # Frontend UI
│   └── tests/
│       └── test_app.py         # Automated unit tests
│
├── nginx/
│   └── nginx.conf              # Reverse proxy configuration
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions CI/CD pipeline
│
├── Dockerfile                  # How to build the container image
├── docker-compose.yml          # Dev environment (all services together)
├── docker-compose.prod.yml     # Production overrides
├── .env.example                # Template for environment variables
├── .gitignore                  # Files git should never track
└── Makefile                    # Shortcut commands
```

---

## Hands-On Exercises

Work through these in order. Each one builds on the previous.

---

### Module 1 — Git Basics

**Goal:** Understand version control before touching any DevOps tooling.

```bash
# Initialize git tracking
git init
git add .
git commit -m "initial commit: add task manager app"

# Create a feature branch (never work directly on main!)
git checkout -b feature/add-priority-field

# After making changes:
git add app/app.py
git commit -m "feat: add priority field to tasks"

# Merge back to main
git checkout main
git merge feature/add-priority-field
```

**Challenge:** Add a `priority` field (low/medium/high) to tasks. Follow the branch workflow above.

---

### Module 2 — Docker

**Goal:** Understand how to package an app into a container.

```bash
# Build the image manually (docker compose does this automatically)
docker build -t devops-task-app:v1 .

# Run the container manually (without compose)
docker run -d -p 5000:5000 --name my-app devops-task-app:v1

# See running containers
docker ps

# See logs from a container
docker logs my-app

# Stop and remove
docker stop my-app
docker rm my-app
```

**Things to explore in `Dockerfile`:**
- What is a multi-stage build and why does it keep images smaller?
- Why do we create a non-root user (`appuser`)?
- What does `HEALTHCHECK` do?

**Challenge:** Change the `WORKDIR` in the Dockerfile and rebuild. Does the app still work? Why?

---

### Module 3 — Docker Compose

**Goal:** Understand how multiple services work together.

```bash
# Start all services
docker compose up -d

# See all running containers
docker compose ps

# See logs from a specific service
docker compose logs app
docker compose logs nginx

# Restart only one service
docker compose restart app

# Scale up (run 2 instances of the app)
docker compose up -d --scale app=2
```

**Things to explore in `docker-compose.yml`:**
- What is a `network` and why do `app` and `nginx` share one?
- What is a `volume` and what happens to data if you remove it?
- What does `depends_on: condition: service_healthy` mean?

**Challenge:** Add a `redis` service to `docker-compose.yml` using `image: redis:alpine`. Connect it to the same network.

---

### Module 4 — Environment Variables

**Goal:** Never hardcode secrets or config — use environment variables.

```bash
# Copy the example file and edit it
cp .env.example .env

# Run with custom environment
docker compose --env-file .env up -d
```

**Why this matters:**
- Same Docker image runs in dev, staging, and production — only the `.env` changes
- Secrets (passwords, API keys) stay out of git

**Things to observe:**
- The app shows `environment` and `version` in the UI header — these come from env vars
- Hit `http://localhost:5000/health` — it returns the environment name

**Challenge:** Add a new env variable `APP_TITLE` and display it in the page `<title>` tag.

---

### Module 5 — Reverse Proxy (Nginx)

**Goal:** Understand why apps in production never expose themselves directly.

```
Browser → port 80 → Nginx → port 5000 → Flask app
```

**Open `nginx/nginx.conf` and find:**
- The `upstream` block — this points Nginx to our Flask service
- `proxy_set_header X-Real-IP` — this passes the client's real IP to Flask
- Security headers like `X-Frame-Options`

**Challenge:** Add a `/status` location block in nginx.conf that returns a simple 200 response directly from Nginx (without hitting Flask). Hint: use `return 200 "nginx is up\n";`

---

### Module 6 — Health Checks

**Goal:** Understand how systems know a service is alive and ready.

```bash
# Check the health endpoint
curl http://localhost:5000/health

# See Docker's health check status
docker inspect taskapp | grep -A 10 '"Health"'

# Watch health checks in real time
docker events --filter type=container
```

**What a health check is used for:**
- Load balancers route traffic only to healthy instances
- Kubernetes restarts pods that fail health checks
- `docker-compose.yml` uses it with `depends_on: condition: service_healthy`

**Challenge:** Make the `/health` endpoint also return the number of tasks stored. This is called adding a **readiness check**.

---

### Module 7 — CI/CD Pipeline

**Goal:** Understand how code goes from developer laptop to production automatically.

**Open `.github/workflows/ci-cd.yml` and read through it.**

The pipeline has 3 jobs that run in sequence:

```
Push to GitHub
     │
     ▼
 [test]  ← runs pytest
     │ (only if tests pass)
     ▼
 [build] ← builds Docker image, smoke tests it
     │ (only on push to main)
     ▼
 [deploy] ← ships to production
```

**To activate this:**
1. Create a free account on [GitHub](https://github.com)
2. Create a new repository
3. Push this code: `git remote add origin <url> && git push -u origin main`
4. Go to the "Actions" tab — watch the pipeline run!

**Challenge:** Add a 4th job called `notify` that runs after `deploy` and prints "Deployment successful! Version: $VERSION". Make it only run if deploy succeeds.

---

### Module 8 — Automated Tests

**Goal:** Understand why tests are the safety net of CI/CD.

```bash
# Run tests locally
cd app
pip install pytest flask
pytest tests/ -v

# What each test does:
# test_health_check       → verifies /health returns 200
# test_get_tasks_empty    → verifies fresh state has no tasks
# test_create_task        → verifies POST /api/tasks works
# test_create_task_missing_title → verifies validation rejects bad input
# test_update_task        → verifies PUT /api/tasks/:id works
# test_delete_task        → verifies DELETE cleans up
```

**Challenge:** Write a new test `test_cannot_delete_nonexistent_task` that sends `DELETE /api/tasks/999` and asserts the response is 404.

---

### Module 9 — Production vs Development

**Goal:** Understand why you need separate configs for different environments.

| Setting | Development | Production |
|---|---|---|
| Direct port exposure | Yes (port 5000) | No (nginx only) |
| Debug mode | On | Off |
| WSGI server | Flask dev server | Gunicorn |
| Logging | Verbose | Structured |

```bash
# Start in production mode
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Notice: port 5000 is no longer accessible directly!
curl http://localhost:5000    # fails
curl http://localhost         # works (via nginx)
```

---

## Common Commands Reference

```bash
# Docker
docker ps                          # list running containers
docker images                      # list local images
docker logs <container>            # view logs
docker exec -it <container> sh     # shell into container
docker stats                       # live CPU/memory usage

# Docker Compose
docker compose up -d               # start in background
docker compose down                # stop and remove containers
docker compose down -v             # also remove volumes (deletes data!)
docker compose build --no-cache    # force rebuild

# Git
git status                         # see what changed
git log --oneline                  # compact history
git diff                           # see exact changes
git stash                          # temporarily save changes
```

---

## What's Next?

After completing all modules, explore these real-world topics:

1. **Kubernetes** — orchestrate containers at scale (`kubectl`, `minikube` locally)
2. **Terraform** — provision cloud infrastructure as code
3. **Prometheus + Grafana** — metrics and dashboards
4. **Secrets Management** — HashiCorp Vault, AWS Secrets Manager
5. **Cloud providers** — deploy this app to AWS ECS, GCP Cloud Run, or Azure

---

## Getting Help

- Stuck on Docker? → [docs.docker.com](https://docs.docker.com)
- Git confused? → [learngitbranching.js.org](https://learngitbranching.js.org) (interactive)
- GitHub Actions syntax? → [docs.github.com/actions](https://docs.github.com/actions)
- Nginx config? → [nginx.org/en/docs](https://nginx.org/en/docs)
Pipeline Test Mon Jun  1 05:55:50 UTC 2026
# trigger
