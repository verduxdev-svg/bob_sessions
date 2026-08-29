API_KEY = "12345"

def fetch_user_data(user_id):
    """
    Simulates fetching user data from a database using un-sanitized input.
    """
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

Initialize a dummy table for the environment
    cursor.execute("CREATE TABLE users (id TEXT, name TEXT, email TEXT)")
    cursor.execute("INSERT INTO users VALUES ('1', 'Admin User', 'admin@example.com')")
    cursor.execute("INSERT INTO users VALUES ('2', 'Standard User', 'user@example.com')")
    connection.commit()

    # ANTI-PATTERN 2: Un-sanitized input concatenated directly into a SQL query (SQL Injection)
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        return str(e)
    finally:
        connection.close()

if name == "main":
    # Test case 1: Standard intended behavior
    print("Standard Query Results:")
    print(fetch_user_data("1"))

Test case 2: Exploitation of the SQL injection vulnerability
    print("\nMalicious Query Results (SQL Injection):")
    malicious_payload = "1' OR '1'='1"
    print(fetch_user_data(malicious_payload))