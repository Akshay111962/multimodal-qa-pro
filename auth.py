import sqlite3
import bcrypt

def init_db():
    """Initializes the SQLite database and creates the users table if it doesn't exist."""
    conn = sqlite3.connect("users.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()

# Initialize the database when the module is imported
init_db()

def register_user(name: str, email: str, password: str) -> dict:
    """
    Registers a new user after validation.
    
    Requirements:
    - Validates email format (basic check for @ and .)
    - Validates password is at least 8 characters
    - Checks if email already exists, returns {"success": False, "message": "Email already registered"}
    - Hashes password with bcrypt and stores it
    - Returns success dict or failure dict with clear error message
    """
    try:
        # Validate inputs
        if not name or not name.strip():
            return {"success": False, "message": "Name cannot be empty"}
        if "@" not in email or "." not in email:
            return {"success": False, "message": "Invalid email format"}
        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters"}

        conn = sqlite3.connect("users.db")
        try:
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {"success": False, "message": "Email already registered"}
            
            # Hash the password
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt)
            password_hash = hashed_pw.decode("utf-8")
            
            # Insert the new user
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            conn.commit()
        finally:
            conn.close()
            
        return {"success": True, "message": "Account created successfully"}
    except Exception as e:
        return {"success": False, "message": f"Registration failed: {str(e)}"}

def login_user(email: str, password: str) -> dict:
    """
    Authenticates a user with email and password.
    
    Requirements:
    - Looks up the user by email
    - Verifies the password against the stored bcrypt hash
    - Returns user details on success
    - Returns {"success": False, "message": "Invalid email or password"} on failure
    """
    try:
        conn = sqlite3.connect("users.db")
        row = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name, email, password_hash FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
        finally:
            conn.close()
            
        if not row:
            return {"success": False, "message": "Invalid email or password"}
            
        db_name, db_email, db_password_hash = row
        
        # Verify the password hash
        if bcrypt.checkpw(password.encode("utf-8"), db_password_hash.encode("utf-8")):
            return {
                "success": True,
                "message": "Login successful",
                "name": db_name,
                "email": db_email
            }
        else:
            return {"success": False, "message": "Invalid email or password"}
            
    except Exception as e:
        return {"success": False, "message": f"Login failed: {str(e)}"}

if __name__ == "__main__":
    import os
    
    print("--- Resetting test database ---")
    if os.path.exists("users.db"):
        try:
            os.remove("users.db")
            print("Removed existing users.db")
        except Exception as e:
            print(f"Could not remove users.db: {e}")
            
    init_db()
    
    test_name = "Alice Hackathon"
    test_email = "alice@example.com"
    test_password = "securepassword123"
    
    # 1. Register a test user
    print("\n--- Test 1: Registering new user ---")
    res1 = register_user(test_name, test_email, test_password)
    print("Result:", res1)
    
    # 2. Try registering the same email again (should fail with "already registered")
    print("\n--- Test 2: Registering duplicate email ---")
    res2 = register_user("Bob Hackathon", test_email, "anotherpassword")
    print("Result:", res2)
    
    # 3. Log in with correct credentials (should succeed)
    print("\n--- Test 3: Logging in with correct credentials ---")
    res3 = login_user(test_email, test_password)
    print("Result:", res3)
    
    # 4. Log in with wrong password (should fail with "Invalid email or password")
    print("\n--- Test 4: Logging in with wrong password ---")
    res4 = login_user(test_email, "wrongpassword")
    print("Result:", res4)
    
    # Extra check: Login with non-existent email
    print("\n--- Test 5: Logging in with non-existent email ---")
    res5 = login_user("nonexistent@example.com", "anypassword")
    print("Result:", res5)
    
    # Extra check: Register with invalid email
    print("\n--- Test 6: Registering with invalid email ---")
    res6 = register_user("Bad Email", "bademail.com", "password123")
    print("Result:", res6)
    
    # Extra check: Register with short password
    print("\n--- Test 7: Registering with short password ---")
    res7 = register_user("Short Pass", "short@example.com", "short")
    print("Result:", res7)
