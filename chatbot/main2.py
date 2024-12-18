import os
import sys
import mysql.connector
from dotenv import load_dotenv
import google.generativeai as genai
from prettytable import PrettyTable
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Load environment variables
load_dotenv()
KEY = os.getenv('key')
genai.configure(api_key=KEY)

def Generate_Content(prompt):
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])

    response = chat.send_message(prompt)
    gemini_response = response.text
    return gemini_response

def execute_query(query):
    # Define your connection parameters
    server = 'localhost'
    username = 'root'
    password = 'root'
    
    # Establish a connection
    try:
        connection = mysql.connector.connect(
            host=server,
            user=username,
            password=password,
            database="avijit"
        )
    except Exception as e:
        return f"Error connecting to database: {e}"

    cur = connection.cursor()
    try:
        cur.execute(query)
        results = cur.fetchall()
        column_names = [description[0] for description in cur.description]

        # Create a PrettyTable object
        table = PrettyTable()
        table.field_names = column_names

        # Add rows to the table
        for row in results:
            table.add_row(row)

        return (table)
    except Exception as e:
        return f"Error executing query: {e}"
    finally:
        cur.close()
        connection.close()

def on_submit():
    question = question_entry.get()
    if question.lower() == "no":
        root.quit()
        return

    prompt = f"""
    You are an SQL query generator. Based on the provided database schema, generate an accurate SQL query to answer the following question: "{question}". Ensure that the SQL query is correctly formatted and can be executed without errors.

**Table Name**: demo

**Table Schema**:
- id INT PRIMARY KEY AUTO_INCREMENT
- name VARCHAR(100) NOT NULL
- ph VARCHAR(15)
- area VARCHAR(100)
- age INT
- gender VARCHAR(10)

**Instructions**:
1. The query should select the appropriate columns based on the question.
2. If the question involves filtering, include a WHERE clause with the necessary conditions.
3. If the question requires aggregation (e.g., COUNT, AVG), include the appropriate SQL functions.
4. Ensure that the SQL syntax is correct and follows best practices.
5. Do not include any additional text or explanations; only provide the SQL query.
   
    """

    response = Generate_Content(prompt)
    query = response.replace("sql", "").replace("```", "").strip()

    # Execute the query and get the result
    result = execute_query(query)

    # Display the result in the text area
    result_text.delete(1.0, tk.END)  # Clear previous text
    result_text.insert(tk.END, result)  # Insert new result

# Create the main window
root = tk.Tk()
root.title("SQL Query Generator")

# Create and place the question label and entry
question_label = tk.Label(root, text="Enter your question:")
question_label.pack(pady=10)

question_entry = tk.Entry(root, width=50)
question_entry.pack(pady=5)

# Create and place the submit button
submit_button = tk.Button(root, text="Submit", command=on_submit)
submit_button.pack(pady=10)

# Create and place the result text area
result_text = scrolledtext.ScrolledText(root, width=80, height=20)
result_text.pack(pady=10)

# Start the GUI event loop
root.mainloop()