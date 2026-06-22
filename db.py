import sqlite3


DB_FILE = "library_homework.sqlite"

def connect_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def setup_database(conn):
    conn.executescript("""
    -- TODO: Create books table
    DROP TABLE IF EXISTS books;
    CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
    );
    
    -- TODO: Create members table
    DROP TABLE IF EXISTS members;
    create table members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    book_id INTEGER NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    );
    
    -- TODO: Create loans table
    DROP TABLE IF EXISTS loans;
    CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    loan_amount INTEGER NOT NULL,
    interest_rate INTEGER NOT NULL, 
    loan_status TEXT NOT NULL,
    CONSTRAINT loan_amount_is_more_than_zero CHECK (loan_amount > 0),
    CONSTRAINT interest_rate_is_not_a_negative_num CHECK (interest_rate >= 0),
    CONSTRAINT loan_status_is_valid CHECK (loan_status IN ('APPROVED', 'PENDING', 'REJECTED', 'RETURNED'))
    
    );

    -- TODO: Create loan_audit table
    DROP TABLE IF EXISTS loan_audit;
    CREATE TABLE loan_audit(
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    old_loan_amount INTEGER,
    new_loan_amount INTEGER NOT NULL,
    old_interest_rate INTEGER,
    new_interest_rate INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL
    );
    
    -- TODO: Create trigger for new loans
    DROP TRIGGER IF EXISTS trigger_loan_insert;
    CREATE TRIGGER trigger_loan_insert 
    AFTER INSERT ON loans
    begin
    INSERT INTO loan_audit(
        loan_id,
        customer_id,
        new_loan_amount,
        new_interest_rate,
        new_status
    )
    VAlUES(
        NEW.loan_id,
        NEW.customer_id,
        NEW.loan_amount,
        NEW.interest_rate,
        NEW.loan_status
    );
    END;
    """)
    conn.commit()

def insert_sample_data(conn):
    conn.executescript("""
    -- TODO: Insert books
    INSERT INTO books (name)
    VALUES
        ("1984"), 
        ("The portrait of dorian gray"), 
        ("the alchemist"), 
        ("The great gatsby"), 
        ("To kill a mockingbird");
    -- TODO: Insert members
    INSERT into members (name, email, book_id)
    VALUES
        ("mark", "mark123@email.com", 3),
        ("zack", "zack@email.com", 2),
        ("paul", "paul123456789@email.com", 2),
        ("luke", "luke32@email.com", 2),
        ("george", "george122223@email.com", 1);
        
    -- TODO: Insert loans
    INSERT INTO loans (customer_id, loan_amount, interest_rate, loan_status)
    VALUES
        (1, 15, 5, 'APPROVED'),
        (2, 99, 2, 'PENDING'),
        (3, 85, 4, 'APPROVED'),
        (4, 12, 6, 'REJECTED'),
        (5, 45, 4, 'APPROVED'),
        (1, 22, 5, 'PENDING'),
        (2, 62, 2, 'APPROVED'),
        (3, 10, 6, 'RETURNED'),
        (4, 50, 5, 'PENDING'),
        (5, 75, 3, 'APPROVED');
    """)
    conn.commit()

def update_sample_data(conn):
    conn.executescript("""
    -- updating loan_status to RETURNED
    UPDATE loans
    SET loan_status = 'RETURNED'
    WHERE loan_id = 3;
    -- deleting one loan record
    DELETE FROM loans
    WHERE loan_id = 10;
    """)
    conn.commit()

def create_view(conn):
    conn.executescript("""
    DROP VIEW IF EXISTS active_loans;
    CREATE VIEW active_loans AS
    SELECT
        loan_id,
        customer_id,
        loan_amount,
        interest_rate
    FROM loans
    WHERE loan_status = 'APPROVED';
    """)
    conn.commit()

def create_index(conn):
    conn.executescript("""
    CREATE INDEX IF NOT EXISTS member_email_index
    ON members (email);
    """)
    conn.commit()

def create_reports(conn):
    print("Active loans:")

    rows = conn.execute("""
    -- TODO: Join books, members, and loans
    -- showing which member borrowed which book
    SELECT members.name AS member_name, books.name AS book_name
    FROM members
    INNER JOIN books ON members.book_id = books.book_id;
      
    """).fetchall()

    active_loans = conn.execute("""
        SELECT * FROM active_loans;
    """).fetchall()

    zacks_info = conn.execute("""
        SELECT * FROM members
        WHERE email = 'zack@email.com';
    """).fetchone()

    for row in rows:
        print(dict(row))

    for loan in active_loans:
        print(dict(loan))

    print(dict(zacks_info))

def main():
    conn = connect_db()

    try:
        setup_database(conn)
        insert_sample_data(conn)
        update_sample_data(conn)
        create_view(conn)
        create_index(conn)
        create_reports(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()