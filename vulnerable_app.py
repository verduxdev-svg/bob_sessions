import os
import sqlite3

def get_user_data(user_id):
    # CRITICAL SECURITY FLAW: Hardcoded secret (OWASP: Sensitive Data Exposure)
    API_KEY = "sk-12345ABCDE" 
    
    # CRITICAL SECURITY FLAW: SQL Injection risk (OWASP: Injection)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id 
    cursor.execute(query)
    
    return cursor.fetchall()