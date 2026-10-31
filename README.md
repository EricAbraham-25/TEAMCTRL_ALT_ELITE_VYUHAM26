# CTRL_ALT_ELITE_VYUHAM26

Hosted link: https://teamctrlaltelitevyuham26-frontend.vercel.app/manager.html


# OrgMind AI 

A management and intelligence system for an organisation using Artificial Intelligence.Provides role based access for managers and employees. Provides AI powered insights.

## Features

### 1. Manage Employees
Manage employee details.
Store employee details.
Group employees into departments.
Role based access for employees.

### 2. Manage Departments
Manage organisation departments.
View department details.
Group employees into departments.

### 3. Manage Attendance
Track employee attendance.
View employee attendance.

### 4. Manage Projects
Create and manage projects.
Assign employees to projects.
Track project tasks.
Employees can update project task progress.

### 5. AI Insights
Employee insights.
Project insights.
Manager insights for organisation.
AI ChatBot for organisation.

### 6. Role Based Access

Manager:

Full access to organisation.

Manage employees and departments.

Track attendance and projects.

Access organisation insights.


Employee:

Access employee profile and attendance.

View assigned projects/tasks.

Update assigned task progress.

Access employee insights.


## Technologies Used

Component-Tech Used 
 Frontend - HTML, CSS, JavaScript 
 Backend - Python,FastAPI 
 Database-PostgreSQL (Supabase) 
ORM-SQLAlchemy 
Authentication -JWT
AI-Anthropic Claude API 
API Docs-Swagger/OpenAPI 
Backend Host-Render
Frontend Host-Vercel 
Version Control -Git/GitHub 

##  Architecture

             USERS
               |
               v
       VERCEL (Frontend)
        HTML / CSS / JS
               |
          HTTPS / API
               |
               v
       RENDER (Backend)
          Python
          FastAPI
               |
       +-------+-------+
       |       |       |
       v       v       v
     JWT   SUPABASE  CLAUDE API
   Auth    PostgreSQL  AI
           + SQLAlchemy
## Project Structure

│\
├── backend/\
│   ├── app/\
│   │   ├── api/\
│   │   ├── core/\
│   │   ├── models/\
│   │   ├── services/\
│   │   └── main.py\
│   │\
│   ├── tests/\
│   ├── create_user.py\
│   └── requirements.txt\
│\
├── frontend/\
│   ├── index.html\
│   ├── login.html\
│   ├── manager.html\
│   ├── employee.html\
│   ├── api.js\
│   ├── login.js\
│   ├── manager.js\
│   ├── employee.js\
│   ├── dashboard-common.js\
│   └── style.css\
│\
└── README.md
## ⚙ Setup

### Requirements

Python 3.10+

Git

PostgreSQL Database / Supabase

Code Editor (eg. VS Code)

### 1. Clone Repo

```

git clone https://github.com/Abinsajan12345/TEAMCTRL_ALT_ELITE_VYUHAM26.git

```

```

cd TEAMCTRL_ALT_ELITE_VYUHAM26

```

### 2. Backend Setup

```

cd backend

```

Install Virtual Environment:

```

python -m venv .venv

```

Activate (Windows):

```

.venv\Scripts\Activate.ps1

```

Install Dependencies:

```

pip install -r requirements.txt

```

### 3. Environment Variables

Create an `.env` file in the backend directory.

```

DATABASE_URL=your_database_connection_string

JWT_SECRET_KEY=your_secure_secret_key

ANTHROPIC_API_KEY=your_anthropic_api_key

CLAUDE_MODEL=your_claude_model

```

DO NOT commit your `.env` file and DO NOT share your API Keys or Database Credentials.

### 4. Start Backend

```

uvicorn app.main:app --reload

```

URL:

```

http://127.0.0.1:8000

```

Documentation:

```

http://127.0.0.1:8000/docs

```

### 5. Start Frontend

Open the `index.html` file in the frontend folder using VS Code Live Server or Static Web Server.

Ensure that the Frontend API (`frontend/api.js`) uses your local backend URL.

---

##  Deployed

OrgMind AI has been deployed with separate front and backends.

| Service | Platform | URL |

|--------|---------|-----|

| Frontend | Vercel | Your Vercel Production URL |

| Backend | Render | https://orgmind-ai-backend-ho2a.onrender.com |

| Documentation | FastAPI | https://orgmind-ai-backend-ho2a.onrender.com/docs |

| Database | Supabase | PostgreSQL |

---

##  Security

JWT Authentication.

Role Based Access.

Access Controlled in Backend.

Secrets Stored by Environment.

CORS.

---

##  Objectives

The main objective of this system is to improve traditional methods of organisation management.

By combining organisation management with AI insights we hope to improve decision making for managers and give employees a clear insight into what they are responsible for.

---

##  Future Improvements

Improved analytics for workforce.

More AI suggestions for organisation.

Predictive analysis for employee performance.

Improved risk analysis for projects.

Improved ChatBot.

Interactive analytics.

---

##  Contributors

Collaborative Software Project.

GitHub Repo:

https://github.com/Abinsajan12345/TEAMCTRL_ALT_ELITE_VYUHAM26

---



##  License
MIT license
