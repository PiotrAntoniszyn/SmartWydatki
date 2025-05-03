# SmartWydatki

[![CI Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()  
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

## Table of Contents

- [Project Description](#project-description)  
- [Tech Stack](#tech-stack)  
- [Getting Started Locally](#getting-started-locally)  
- [Available Scripts](#available-scripts)  
- [Project Scope](#project-scope)  
- [Project Status](#project-status)  
- [License](#license)  

---

## Project Description

**SmartWydatki** is a web application for recording and analyzing your everyday small expenses. Leveraging AI, the app automatically categorizes expenses and provides actionable financial advice, helping you gain control over your spending.  

**Key problems addressed:**
- Manual tracking of small, frequent expenses is time-consuming and error-prone.  
- Lack of simple automated categorization and personalized saving tips.  

---

## Tech Stack

- **Backend Framework:** Python, Flask (2.3.x)  
- **Templating:** Jinja2  
- **Forms & Validation:** Flask-WTF, email-validator  
- **Authentication & Session:** Flask-Login, Flask-Session  
- **Database & Auth:** Supabase (PostgreSQL, REST/GraphQL, RLS)  
- **AI Integration:** OpenRouter.ai Python client  
- **Retry & Timeouts:** tenacity  
- **HTTP Requests:** requests  
- **Environment Management:** python-dotenv  
- **Production WSGI Server:** Gunicorn  
- **Frontend UI:** Bootstrap (optionally Tailwind & vanilla JS)  
- **CI/CD & Hosting:** GitHub Actions, Docker, DigitalOcean (Kubernetes/Droplet)  

---

## Getting Started Locally

### Prerequisites

- Python 3.10+  
- Supabase account & project  
- OpenRouter.ai API key  
- Git  

### Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/PiotrAntoniszyn/smartwydatki.git
   cd smartwydatki
   ```

2. **Create and activate a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables**  
   - Copy `.env.example` to `.env`  
   - Set the following values in `.env`:  
     ```
     FLASK_APP=app.py
     FLASK_ENV=development
     SUPABASE_URL=your-supabase-url
     SUPABASE_KEY=your-supabase-key
     OPENROUTER_API_KEY=your-openrouter-key
     SESSION_TYPE=filesystem
     ```
   
5. **Supabase Setup**  
   - Create your database tables & RLS policies as per `db/migrations/`  
   - Ensure your Supabase project has Auth enabled

6. **Run the development server**  
   ```bash
   flask run
   ```
   The app will be available at `http://localhost:5000`.

---

## Available Scripts

From the project root, use the following commands:

| Command                         | Description                              |
|---------------------------------|------------------------------------------|
| `flask run`                     | Start Flask development server           |
| `gunicorn app:app`              | Run production WSGI server via Gunicorn  |
| `docker build -t smartwydatki .`| Build the Docker image                   |
| `docker run -p 5000:5000 smartwydatki` | Run the containerized app         |
| _[Add your test/lint commands here]_ | _e.g., `pytest`, `flake8`_         |

---

## Project Scope

This README covers the **MVP** scope as defined in the [Product Requirements Document (PRD)](./.ai/prd.md):

Included features:
- User authentication (email/password) with password change & account deletion  
- Onboarding with AI-generated category suggestions  
- Expense CRUD operations via modals (validation, loader, AI categorization)  
- Category management (unique names, inline validation)  
- Expense listing with pagination, sorting, search, and filters  
- AI-driven financial advice messages  
- Operation logging in database  

Out-of-scope for MVP:
- Data import/export  
- Charts and dashboards  
- Bank integrations  
- Push/email notifications  
- Mobile applications  
- Bulk edits & log archiving  

---

## Project Status

- **Development Stage:** MVP complete / **Active development**  
- **Upcoming:** tests, CI badge integration, end-to-end testing, UI polish

---

## License

Distributed under the **MIT License**. See [LICENSE](./LICENSE) for more information.  

---

*Built with ❤️ by the SmartWydatki team* 