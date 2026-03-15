import pymysql

# Replace 'your_password_here' with the Root password you created during MySQL installation
MYSQL_ROOT_PASSWORD = 'admin123'

print("Attempting to connect to MySQL...")
try:
    # Connect to MySQL Server (Without selecting a database yet)
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password=MYSQL_ROOT_PASSWORD
    )
    cursor = connection.cursor()

    # Create the database
    print("Creating p2p_notes database if it doesn't exist...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS p2p_notes;")
    
    # Use the newly created database
    cursor.execute("USE p2p_notes;")

    print("Dropping existing tables to apply new schema...")
    cursor.execute("DROP TABLE IF EXISTS downloads;")
    cursor.execute("DROP TABLE IF EXISTS reviews;")
    cursor.execute("DROP TABLE IF EXISTS notes;")
    cursor.execute("DROP TABLE IF EXISTS users;")

    print("Creating tables...")
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        branch VARCHAR(50),
        year INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Notes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(200) NOT NULL,
        subject VARCHAR(100) NOT NULL,
        description TEXT,
        branch VARCHAR(50),
        semester VARCHAR(10),
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(255) NOT NULL,
        file_hash VARCHAR(64) NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        download_count INT DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')

    # Downloads table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS downloads (
        id INT AUTO_INCREMENT PRIMARY KEY,
        note_id INT NOT NULL,
        user_id INT NOT NULL,
        download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')

    # Reviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INT AUTO_INCREMENT PRIMARY KEY,
        note_id INT NOT NULL,
        user_id INT NOT NULL,
        rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
        review_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')

    print("Checking for sample data...")
    # checking if users table is empty
    cursor.execute("SELECT COUNT(*) FROM users;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Inserting sample users and notes...")
        cursor.execute('''
        INSERT INTO users (name, email, password_hash, branch, year) VALUES 
        ('Alice Smith', 'alice@college.edu', 'scrypt:32768:8:1$Cq7a8q9C$889e4c194689b093375815616dc31d77a28e83be602b9370007817e089d81d520379def286f9ee19f4a62e3d30b9101b05807afb248a3ed444d320475af317ca', 'Computer Science', 3),
        ('Bob Jones', 'bob@college.edu', 'scrypt:32768:8:1$Cq7a8q9C$889e4c194689b093375815616dc31d77a28e83be602b9370007817e089d81d520379def286f9ee19f4a62e3d30b9101b05807afb248a3ed444d320475af317ca', 'Information Technology', 2);
        ''')

        cursor.execute('''
        INSERT INTO notes (user_id, title, subject, description, branch, semester, file_name, file_path, file_hash) VALUES 
        (1, 'OS Chapter 1-3 Notes', 'Operating Systems', 'Detailed notes on processes and threads', 'Computer Science', '3-1', 'OS_Notes_Ch1_3.pdf', 'static/uploads/OS_Notes_Ch1_3.pdf', 'dummy_hash_1'),
        (2, 'DBMS ER Diagrams', 'Database Management', 'Examples of ER diagrams with solutions', 'Information Technology', '2-2', 'DBMS_ER.pdf', 'static/uploads/DBMS_ER.pdf', 'dummy_hash_2');
        ''')
    
    connection.commit()
    print("------------------------------------------")
    print("✅ SUCCESS! The database is fully set up!")
    print("------------------------------------------")

except pymysql.MySQLError as e:
    print("------------------------------------------")
    print("❌ ERROR: Could not connect to MySQL.")
    print("Message:", e)
    print("------------------------------------------")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
