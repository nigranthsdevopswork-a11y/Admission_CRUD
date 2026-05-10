# Apne project folder mein copy karo
cp README.md /path/to/ADMISSION_CRUD/README.md

# Phir GitHub pe push karo
git add README.md
git commit -m "Add complete Docker flow README"
git push












--------------------------------------------------------------------------------------------------------------------------------------------


# Student Admission CRUD — Docker Practice Project

## Tech Stack (Original vs This Project)

| Layer    | Original (EASY_CRUD)       | This Project               |
|----------|----------------------------|----------------------------|
| Frontend | React + Vite + Apache      | **HTML + Vanilla JS + Nginx** |
| Backend  | Java Spring Boot           | **Python Flask**           |
| Database | MariaDB                    | **MySQL 8.0**              |

---

## Project Structure

```
ADMISSION_CRUD/
├── docker-compose.yml
├── init.sql
├── backend/
│   ├── Dockerfile
│   ├── app.py          ← Flask REST API
│   └── requirements.txt
└── frontend/
    ├── Dockerfile
    ├── nginx.conf      ← Nginx with API proxy
    └── index.html      ← Full frontend
```

---

## Docker Commands

### Build & Run (sab kuch ek saath)
```bash
docker-compose up --build
```

### Background mein run karo
```bash
docker-compose up --build -d
```

### Logs dekhna
```bash
docker-compose logs -f
docker-compose logs backend
```

### Stop karo
```bash
docker-compose down
```

### Database data bhi delete karo
```bash
docker-compose down -v
```

---

## Access

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost            |
| Backend  | http://localhost:5000/api/students |
| Database | localhost:3306 (root/redhat) |

---

## API Endpoints

| Method | Endpoint                  | Description           |
|--------|---------------------------|-----------------------|
| GET    | /api/students             | Get all students      |
| POST   | /api/register             | Register new student  |
| DELETE | /api/students/{id}        | Delete student by ID  |
| GET    | /health                   | Backend health check  |

---

## Individual Docker Commands (Practice)

### Sirf ek container build karo
```bash
docker build -t admission-backend ./backend
docker build -t admission-frontend ./frontend
```

### Manually run karo (without compose)
```bash
# Network banao
docker network create admission-net

# MySQL
docker run -d --name admission_db \
  --network admission-net \
  -e MYSQL_ROOT_PASSWORD=redhat \
  -e MYSQL_DATABASE=admission_db \
  mysql:8.0

# Backend
docker run -d --name admission_backend \
  --network admission-net \
  -e DATABASE_URL=mysql+pymysql://root:redhat@admission_db:3306/admission_db \
  -p 5000:5000 \
  admission-backend

# Frontend
docker run -d --name admission_frontend \
  --network admission-net \
  -p 80:80 \
  admission-frontend
```
