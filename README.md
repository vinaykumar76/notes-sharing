# Peer-to-Peer Notes Sharing System

A complete full-stack web application designed for students to share, discover, and download academic notes.

## Features
* **User Authentication**: Secure registration, login, and session management using Werkzeug password hashing.
* **Student Dashboard**: Personalized view of uploaded notes and recent downloads.
* **Notes Management**: Upload PDF, DOC, DOCX, PPT, and PPTX files.
* **Browse & Search**: Filter notes by branch, semester, or search by keywords.
* **Secure Downloads**: Track the number of times a note has been downloaded.
* **Modern UI**: A responsive, dark-themed, glassmorphism UI built with custom CSS.

## Project Structure
```
notes-sharing-system/
├── app.py                 # Core Flask application
├── requirements.txt       # Python dependencies
├── schema.sql             # MySQL schema and sample data
├── static/
│   ├── css/
│   │   └── style.css      # Custom stylesheet
│   ├── js/
│   │   └── main.js        # UI interactivity script
│   └── uploads/           # Directory where notes are saved
└── templates/
    ├── base.html          # Main layout
    ├── index.html         # Landing page
    ├── register.html      # User registration form
    ├── login.html         # User login form
    ├── dashboard.html     # User dashboard
    ├── upload.html        # File upload form
    ├── browse.html        # Browse and search notes
    └── profile.html       # User profile and stats
```

## Setup Instructions

### 1. Prerequisites
You will need to have installed on your local machine:
* Python 3.8 or higher
* MySQL Server

### 2. Database Setup
1. Open your MySQL client (e.g., MySQL Workbench, phpMyAdmin, or terminal).
2. Create a new database named `p2p_notes` (or just run the schema file directly, as it includes the `CREATE DATABASE` statement).
3. Import the `schema.sql` file to create the necessary tables (`users`, `notes`, `downloads`) and insert sample data.
   * Command line: `mysql -u root -p < schema.sql`

### 3. Application Setup
1. Open a terminal and navigate to the project directory:
   ```bash
   cd notes-sharing-system
   ```
2. (Optional but recommended) Create and activate a Virtual Environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Database Connection**: Open `app.py` and locate the `get_db_connection()` function. Ensure the `user` and `password` match your local MySQL credentials. Find the secret key `app.secret_key` and ensure it's set to something secure if deploying.

### 4. Running Locally
Simply run the Flask application:
```bash
python app.py
```
The server will start on `http://127.0.0.1:5000/`. You can navigate to this URL in your web browser.

### Sample Test Data
If you loaded the sample data from `schema.sql`, you can test with:
* Email: `alice@college.edu`
* Password: `password123`
*(Note: Be sure to follow the DB setup correctly so these sample users exist)*

## Deployment Suggestions
For a complete college project submission, you might want to consider deploying it online:
1. **Platform**: Render, Heroku, or PythonAnywhere are great free/cheap options for Flask apps.
2. **Database**: Use a managed MySQL database provided by PlanetScale, Aiven, or AWS RDS.
3. **Storage**: Currently, files are stored locally in the `static/uploads/` directory. For a real production application, you should move this to a cloud storage provider like AWS S3 or Cloudinary.
4. **Configuration**: Use environment variables (`os.environ.get()`) to manage database credentials and secret keys rather than hardcoding them in `app.py`.
