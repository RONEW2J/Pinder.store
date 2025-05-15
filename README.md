# 🔥 TinderCloneProject – Full-Stack Django REST API Application

**TinderCloneProject** is a fully functional clone of the popular Tinder app, built as a final team project. It features a modern tech stack, RESTful APIs, background jobs, and a production-ready deployment on cloud infrastructure. This project demonstrates our team’s ability to design, develop, test, document, and deploy a scalable web application.

---

## 📱 About the Project

This Tinder clone replicates essential dating features:
- User registration, login, and profile management
- Swipe right/left interactions
- Real-time matching system
- Private chat between matched users
- Media uploads and profile photos

---

## ✅ Features

- **30+ Django REST API Endpoints**
- **Unit tests** for every endpoint and HTTP method
- **Swagger UI** for API documentation using `drf-yasg`
- **Silk** for performance profiling
- **Throttling** for both anonymous and authenticated users
- **Polished, responsive frontend UI**
- **Dockerized environment** using `docker-compose`
- **Deployed on GCP/AWS/PSCloud VM**
- **TLS certificate and custom domain support**

---

## 🧱 Tech Stack

### Backend
- Python 3.11+
- Django 5.x
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- MinIO / AWS S3 (for media)
- drf-yasg (Swagger UI)
- django-silk (profiling)

### Frontend
- HTML / CSS / JavaScript (Responsive UI)

### DevOps / Deployment
- Docker & Docker Compose
- nginx (static files & reverse proxy)
- GitHub Actions (CI/CD)
- GCP / AWS / PSCloud
- Let’s Encrypt TLS
- UFW Firewall Configuration

---

## 🐳 Local Development (Docker)

To build and run everything locally:

``
  docker-compose up --build
``

## 🧪 Testing
All endpoints and methods are covered with unit tests:

``
 python manage.py test
``

## 📚 API Documentation
Swagger UI is available at:

``
  http://localhost:8000/swagger/
``

## 🌐 Live Deployment

### The app is deployed on a production virtual machine.

 * 🔗 Production URL: https://yourdomain.com (replace with actual domain)

 * ✅ TLS/HTTPS: Enabled via Let’s Encrypt

 * 🔐 Firewall: Only web ports are exposed (80/443)

## 👨‍💻 Contributors

| Name                   | Role                         | GitHub                         |
|------------------------|------------------------------|--------------------------------|
| **Said Darkhanuly**    | Backend / FrontEnd Developer | [@sdrk47](https://github.com/sdrk47) |
| **Ikhtiyor Ibragimov** | Backend Developer / DevOps   | [@RONEW2J](https://github.com/RONEW2J) |
| **Kamron Yunussaliev**| FrontEnd Developer         | [@Kamron](https://github.com/kama683) |

## 📄 License

This project is licensed under the MIT License.

