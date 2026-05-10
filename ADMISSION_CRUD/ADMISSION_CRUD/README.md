# Docker Project — Complete Flow
### Student Admission CRUD | Starting Se Ending Tak

---

## Project Tech Stack

| Layer | Original (EASY_CRUD) | New (ADMISSION_CRUD) |
|-------|----------------------|----------------------|
| Frontend | React + Vite + Apache | HTML + Vanilla JS + Nginx |
| Backend | Java Spring Boot | Python Flask |
| Database | MariaDB | MariaDB (Docker Hub) |

---

## Step-by-Step Flow — Commands with Explanation

---

### Step 1 — Docker Network Banaya

Sabse pehle ek custom network create kiya taaki teeno containers (DB, backend, frontend) ek doosre se naam se baat kar sake. Bina network ke containers isolated rehte hain.

```bash
docker network create my_network
```

> **Note:** `my_network` naam ka bridge network ban gaya. Ab is network pe run hone wale containers ek doosre ko naam se dhundh sakte hain — jaise backend `mariadb_count` naam se DB ko dhundhta hai.

---

### Step 2 — MariaDB Container Run Kiya

Database pehle start karna zaruri tha kyunki backend usse connect karta hai. Environment variables se root password, database naam, aur user set kiya. Volume se data permanently save hoga.

```bash
docker run -d -p 3306:3306 \
  --name mariadb_count \
  --network my_network \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=student_db \
  -e MYSQL_USER=admin \
  -e MYSQL_PASSWORD=admin \
  -v db_data:/var/lib/mysql \
  mariadb:latest
```

> **Note:** `-v db_data:/var/lib/mysql` se data EC2 pe permanently save hoga. Container delete ho jaye tab bhi data safe rahega.

---

### Step 3 — Backend Image Build Kiya

`backend/` folder mein jaake Dockerfile se image build ki. Is process mein Python 3.12, Flask, SQLAlchemy, aur PyMySQL install hote hain.

```bash
cd /Admission_CRUD/ADMISSION_CRUD/ADMISSION_CRUD/backend

docker build -t backend .
```

> **Note:** `-t backend` matlab image ka naam `backend` rakho. `.` matlab current folder ka Dockerfile use karo.

---

### Step 4 — Backend Container Run Kiya

> ⚠️ **Error jo pehli baar aaya (DATABASE_URL missing tha):**
> ```
> Access denied for user 'root'@'172.18.0.3' (using password: NO)
> ```
> **Karan:** `-e DATABASE_URL` bhool gaya tha. Flask ko database ka password pata hi nahi tha.

**Fix — DATABASE_URL ke saath sahi command:**

```bash
docker run -d -p 5000:5000 \
  --name backend_count \
  --network my_network \
  -e DATABASE_URL="mysql+pymysql://root:root@mariadb_count:3306/student_db" \
  backend:latest
```

> **Note:** `DATABASE_URL` mein `mariadb_count` container ka naam hai — IP nahi. Same network mein hone se Flask usse naam se dhundh leta hai. `using password: NO` matlab Flask ko password mila hi nahi tha.

---

### Step 5 — Frontend Image Build Kiya

`frontend/` folder mein Nginx ka Dockerfile tha. `index.html` aur `nginx.conf` copy hokar Nginx image bani.

```bash
cd ../frontend

docker build -t frontend .
```

> **Note:** Nginx lightweight web server hai — React jaisa build step nahi chahiye, seedha HTML serve karta hai.

---

### Step 6 — nginx.conf Mein Typo Fix Kiya

> ⚠️ **Error jo aaya:**
> ```
> nginx: [emerg] invalid URL prefix in /etc/nginx/conf.d/default.conf:10
> ```
> **Karan:** `nginx.conf` mein `http:/` tha — ek slash missing tha.

**Fix — vim se sahi kiya:**

```bash
vim nginx.conf
```

```nginx
# Galat tha (ek slash missing):
proxy_pass http:/44.202.92.250:5000/api/;

# Sahi kiya — container naam use karo (IP se better):
proxy_pass http://backend_count:5000/api/;
```

> **Note:** IP use karne ke bajaay container naam use karna better hai kyunki EC2 IP change hoti rehti hai, lekin container naam same rehta hai.

---

### Step 7 — Port 80 Already In Use — Apache Band Kiya

> ⚠️ **Error jo aaya:**
> ```
> failed to bind host port 0.0.0.0:80/tcp: address already in use
> ```
> **Karan:** EC2 pe Apache2 pehle se chal raha tha aur port 80 use kar raha tha.

**Fix:**

```bash
# Apache band karo
sudo systemctl stop apache2

# Phir frontend run karo
docker run -d -p 80:80 \
  --name frontend_count \
  --network my_network \
  frontend:latest
```

> **Note:** EC2 pe by default Apache2 installed hota hai jo port 80 use karta hai. Docker ko wahi port chahiye tha isliye pehle Apache band karna pada.

---

### Step 8 — index.html Mein API URL Fix Kiya

> ⚠️ **Problem:** Website khul rahi thi lekin form submit karne par `Backend not reachable` aa raha tha.  
> **Karan:** `index.html` mein `localhost` likha tha — browser ke liye localhost matlab user ka apna PC, EC2 nahi!

**Fix — vim se sahi kiya:**

```bash
vim index.html
```

```javascript
// Galat tha (browser ke liye localhost = apna PC):
const API_BASE = 'http://localhost:5000/api';

// Sahi kiya — EC2 ka Public IP:
const API_BASE = 'http://44.202.92.250:5000/api';
```

> **Note:** AWS Security Group mein port `5000` bhi open karna pada taaki browser bahar se backend reach kar sake.  
> EC2 → Security Groups → Inbound Rules → Add Rule → Port 5000 → Save

---

### Step 9 — Image Rebuild Karke Final Run

`nginx.conf` aur `index.html` fix karne ke baad image dobara build ki aur naya container run kiya:

```bash
# Image rebuild karo
docker build -t frontend:latest .

# Purana container hatao
docker rm -f frontend_count

# Naya container run karo
docker run -d -p 80:80 \
  --name frontend_count \
  --network my_network \
  frontend:latest

# Check karo sab running hai
docker ps
```

---

## Final Result — Teeno Containers Running!

```bash
docker ps

# Output:
CONTAINER ID   IMAGE             STATUS   PORTS
frontend_count  frontend:latest   Up       0.0.0.0:80->80/tcp
backend_count   backend:latest    Up       0.0.0.0:5000->5000/tcp
mariadb_count   mariadb:latest    Up       0.0.0.0:3306->3306/tcp
```

---

## Request Ka Safar (Browser Se Database Tak)

```
User (Browser)
      |
      | port 80
      ▼
frontend_count (Nginx)
      |
      | port 5000  (/api/ calls forward karta hai)
      ▼
backend_count (Flask)
      |
      | port 3306
      ▼
mariadb_count (MariaDB)
```

| Order | Container | Port | Kaam |
|-------|-----------|------|------|
| 1 | Browser (User) | — | Form fill karta hai, HTTP request bhejta hai |
| 2 | frontend_count | 80 | Nginx HTML serve karta hai, `/api/` calls backend ko forward karta hai |
| 3 | backend_count | 5000 | Flask API request receive karta hai, DB se data fetch/save karta hai |
| 4 | mariadb_count | 3306 | MariaDB data store/retrieve karta hai |

---

## Errors Summary — Jo Aaye Aur Fix Kiya

| Error | Karan | Fix |
|-------|-------|-----|
| `network my_network not found` | Container banaya lekin network pehle nahi banaya tha | `docker network create my_network` → container rm → fresh run |
| `Access denied (using password: NO)` | Backend run karte waqt `-e DATABASE_URL` nahi diya | `docker run` mein `DATABASE_URL` environment variable add kiya |
| `invalid URL prefix in nginx.conf:10` | `nginx.conf` mein `http:/` tha — ek slash missing | `http://backend_count:5000/api/` kiya — double slash |
| `port 80 already in use` | EC2 pe Apache2 already port 80 use kar raha tha | `sudo systemctl stop apache2` |
| `Backend not reachable` (form submit pe) | `index.html` mein `localhost` tha — browser ke liye wrong | EC2 Public IP diya: `http://44.202.92.250:5000/api` |

---

## Useful Commands — Quick Reference

### Container Management

```bash
docker ps               # Running containers dekho
docker ps -a            # Saare containers (stopped bhi)
docker logs <name>      # Container ke logs dekho
docker inspect <name>   # Full details dekho
docker rm <name>        # Container delete karo
docker rm -f <name>     # Force delete (running ho tab bhi)
docker start <name>     # Band container start karo
docker stop <name>      # Container band karo
```

### Database Access

```bash
# MariaDB mein login karo
docker exec -it mariadb_count mysql -u root -proot

# Andar jaake ye commands chalaao:
SHOW DATABASES;
USE student_db;
SHOW TABLES;
SELECT * FROM students;
```

### Network Commands

```bash
docker network ls                     # Saare networks dekho
docker network inspect my_network     # Network ki details
docker network create my_network      # Naya network banao
```

### Image Commands

```bash
docker images                         # Saari images dekho
docker build -t <naam> .              # Image build karo
docker rmi <naam>                     # Image delete karo
```

---

> 💡 **Sabse Bada Lesson:**  
> Containers chalaane ka **order matter karta hai!**  
> **Pehle** Network → **Phir** Database → **Phir** Backend → **Aakhir mein** Frontend  
> Aur har container ko proper **environment variables** dena zaruri hai — bina `DATABASE_URL` ke backend DB se connect nahi ho sakta.






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
