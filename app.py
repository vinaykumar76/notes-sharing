import os
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pymysql

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here_for_development'

# --- Configuration ---
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Database Connection Utility ---
def get_db_connection():
    # Update with your MySQL credentials
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='admin123', # Add your root password if any
        database='p2p_notes',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                g.user = cursor.fetchone()
        except Exception as e:
            print(f"Error loading user: {e}")
            g.user = None
        finally:
            conn.close()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

# --- Authentication Routes ---

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        branch = request.form['branch']
        year = request.form['year']

        error = None
        if not name or not email or not password:
            error = 'Name, email, and password are required.'
        
        if error is None:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
                    if cursor.fetchone() is not None:
                        error = f"Email {email} is already registered."
                    else:
                        cursor.execute(
                            'INSERT INTO users (name, email, password_hash, branch, year) VALUES (%s, %s, %s, %s, %s)',
                            (name, email, generate_password_hash(password), branch, year)
                        )
                        conn.commit()
                        flash('Registration successful! Please log in.', 'success')
                        return redirect(url_for('login'))
            except Exception as e:
                error = f"Database error: {e}"
            finally:
                conn.close()
        
        if error:
            flash(error, 'danger')

    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        error = None
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                user = cursor.fetchone()

                if user is None:
                    error = 'Incorrect email.'
                elif not check_password_hash(user['password_hash'], password):
                    error = 'Incorrect password.'

                if error is None:
                    session.clear()
                    session['user_id'] = user['id']
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('dashboard'))
        except Exception as e:
            error = f"Database error: {e}"
        finally:
            conn.close()

        if error:
            flash(error, 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# --- Application Routes ---

@app.route('/dashboard')
def dashboard():
    if g.user is None:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # My Uploads
            cursor.execute('SELECT * FROM notes WHERE user_id = %s ORDER BY upload_date DESC', (g.user['id'],))
            my_uploads = cursor.fetchall()
            
            # My Downloads (Using the downloads junction table)
            cursor.execute('''
                SELECT n.*, d.download_date 
                FROM notes n
                JOIN downloads d ON n.id = d.note_id
                WHERE d.user_id = %s
                ORDER BY d.download_date DESC
            ''', (g.user['id'],))
            my_downloads = cursor.fetchall()
            
    except Exception as e:
        flash(f"Error loading dashboard: {e}", 'danger')
        my_uploads = []
        my_downloads = []
    finally:
        conn.close()

    return render_template('dashboard.html', uploads=my_uploads, downloads=my_downloads)

@app.route('/upload', methods=('GET', 'POST'))
def upload():
    if g.user is None:
        flash('Please log in to upload notes.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        description = request.form.get('description', '')
        branch = request.form['branch']
        semester = request.form['semester']
        
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create a unique filename to avoid overwriting
            import time
            unique_filename = f"{int(time.time())}_{filename}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Calculate file hash
            file_content = file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            # Reset file pointer for saving
            file.seek(0)
            
            # Save to db
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    # Check for duplicates
                    cursor.execute('SELECT id FROM notes WHERE file_hash = %s', (file_hash,))
                    if cursor.fetchone():
                        flash('This exact file has already been uploaded by someone else!', 'danger')
                        return redirect(request.url)

                    cursor.execute('''
                        INSERT INTO notes (user_id, title, subject, description, branch, semester, file_name, file_path, file_hash)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (g.user['id'], title, subject, description, branch, semester, unique_filename, f'static/uploads/{unique_filename}', file_hash))
                    conn.commit()
                flash('Note uploaded successfully!', 'success')
                
                # Now save the file since DB insert succeeded
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)

                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'An error occurred: {e}', 'danger')
            finally:
                conn.close()
        else:
            flash('Allowed file types are pdf, doc, docx, ppt, pptx', 'danger')

    return render_template('upload.html')

@app.route('/browse')
def browse():
    search_query = request.args.get('q', '')
    branch_filter = request.args.get('branch', '')
    semester_filter = request.args.get('semester', '')
    
    query = '''
        SELECT n.*, u.name as uploader_name
        FROM notes n
        JOIN users u ON n.user_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if search_query:
        query += ' AND (n.title LIKE %s OR n.subject LIKE %s OR n.description LIKE %s)'
        like_search = f'%{search_query}%'
        params.extend([like_search, like_search, like_search])
        
    if branch_filter:
        query += ' AND n.branch = %s'
        params.append(branch_filter)
        
    if semester_filter:
        query += ' AND n.semester = %s'
        params.append(semester_filter)
        
    query += ' ORDER BY n.upload_date DESC'
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            notes = cursor.fetchall()
            
            # Get distinct branches for filter dropdown
            cursor.execute('SELECT DISTINCT branch FROM notes WHERE branch IS NOT NULL AND branch != ""')
            branches = [row['branch'] for row in cursor.fetchall()]
            
    except Exception as e:
        flash(f"Error loading notes: {e}", 'danger')
        notes = []
        branches = []
    finally:
        conn.close()

    return render_template('browse.html', notes=notes, branches=branches)

@app.route('/download/<int:note_id>')
def download(note_id):
    if g.user is None:
        flash('Please log in to download notes.', 'warning')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get note info
            cursor.execute('SELECT * FROM notes WHERE id = %s', (note_id,))
            note = cursor.fetchone()
            
            if note is None:
                flash('Note not found.', 'danger')
                return redirect(url_for('browse'))
                
            # Update download count
            cursor.execute('UPDATE notes SET download_count = download_count + 1 WHERE id = %s', (note_id,))
            
            # Record in downloads table
            cursor.execute('INSERT INTO downloads (note_id, user_id) VALUES (%s, %s)', (note_id, g.user['id']))
            conn.commit()
            
            # Send file
            file_path = note['file_path']
            # We assume file_path is something like static/uploads/filename.ext
            # Extract just the filename to send from the uploads directory
            safe_filename = note['file_name']
            
            return send_file(
                os.path.join(app.root_path, file_path),
                as_attachment=True,
                download_name=note['title'] + os.path.splitext(safe_filename)[1]
            )
            
    except Exception as e:
        flash(f"Error downloading file: {e}", 'danger')
        return redirect(url_for('browse'))
    finally:
        conn.close()

@app.route('/note/<int:note_id>', methods=['GET', 'POST'])
def note_details(note_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # If posting a review
            if request.method == 'POST':
                if g.user is None:
                    flash('Please log in to submit a review.', 'warning')
                    return redirect(url_for('login'))
                
                rating = request.form.get('rating')
                review_text = request.form.get('review_text', '')
                
                if rating and rating.isdigit() and 1 <= int(rating) <= 5:
                    # Check if user already reviewed
                    cursor.execute('SELECT id FROM reviews WHERE note_id = %s AND user_id = %s', (note_id, g.user['id']))
                    if cursor.fetchone():
                        flash('You have already reviewed this note.', 'warning')
                    else:
                        cursor.execute(
                            'INSERT INTO reviews (note_id, user_id, rating, review_text) VALUES (%s, %s, %s, %s)',
                            (note_id, g.user['id'], int(rating), review_text)
                        )
                        conn.commit()
                        flash('Review submitted successfully!', 'success')
                else:
                    flash('Invalid rating selected.', 'danger')
                
                return redirect(url_for('note_details', note_id=note_id))

            # Fetch note details with uploader name
            cursor.execute('''
                SELECT n.*, u.name as uploader_name 
                FROM notes n 
                JOIN users u ON n.user_id = u.id 
                WHERE n.id = %s
            ''', (note_id,))
            note = cursor.fetchone()
            
            if note is None:
                flash('Note not found.', 'danger')
                return redirect(url_for('browse'))
                
            # Fetch reviews
            cursor.execute('''
                SELECT r.*, u.name as reviewer_name 
                FROM reviews r 
                JOIN users u ON r.user_id = u.id 
                WHERE r.note_id = %s 
                ORDER BY r.created_at DESC
            ''', (note_id,))
            reviews = cursor.fetchall()
            
            # Calculate average rating
            avg_rating = 0
            if reviews:
                avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
                
    except Exception as e:
        flash(f"Error loading note: {e}", 'danger')
        return redirect(url_for('browse'))
    finally:
        conn.close()

    return render_template('note_details.html', note=note, reviews=reviews, avg_rating=round(avg_rating, 1))

@app.route('/profile')
def profile():
    if g.user is None:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT count(*) as upload_count FROM notes WHERE user_id = %s', (g.user['id'],))
            upload_stats = cursor.fetchone()
            
            cursor.execute('SELECT count(*) as download_count FROM downloads WHERE user_id = %s', (g.user['id'],))
            download_stats = cursor.fetchone()
            
            stats = {
                'uploads': upload_stats['upload_count'],
                'downloads': download_stats['download_count']
            }
    except Exception as e:
        stats = {'uploads': 0, 'downloads': 0}
    finally:
        conn.close()
        
    return render_template('profile.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
