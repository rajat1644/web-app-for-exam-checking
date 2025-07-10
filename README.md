\# Django Task Annotation App

![status](https://img.shields.io/badge/status-in--progress-yellow)


A Django-based web application for assigning tasks involving image annotation. Users can draw, label, or tag images using a canvas interface. Admins can review submitted work and approve or reject based on quality.



---



\## 🚀 Features



\- User authentication (login/register/logout)

\- Admin dashboard for task creation and review

\- Task assignment to users

\- Interactive image annotation with:

&nbsp; - Drawing tools

&nbsp; - Rectangle/text

&nbsp; - Number tagging

\- Submission tracking and history

\- Score calculation and auto-approval

\- Image and annotation integrity checks

\- "Go back and edit" for rejected/pending tasks



---



\## 🛠️ Tech Stack



\- \*\*Backend:\*\* Django, PostgreSQL

\- \*\*Frontend:\*\* HTML, Bootstrap, JavaScript

\- \*\*Canvas Tools:\*\* Fabric.js

\- \*\*Image Parsing:\*\* Python

---



\## 📦 Setup Instructions



\### 🔧 Requirements



\- Python 3.10+

\- pip

\- virtualenv (recommended)



\### 🖥️ Local Setup



```bash

\# Clone the repository

git clone https://github.com/yourusername/task-annotation-app.git

cd task-annotation-app



\# Create and activate virtual environment

python -m venv penv

penv\\Scripts\\activate  # For Windows



\# Install dependencies

pip install -r requirements.txt



\# Run migrations

python manage.py makemigrations

python manage.py migrate



\# Create superuser (admin login)

python manage.py createsuperuser



\# Start server

python manage.py runserver





\##🙋 Author

Rajatbir Singh Walia



GitHub: RAJATBIR SINGH WALIA

