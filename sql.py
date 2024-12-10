import azure.functions as func
import logging
import json
import os
from dotenv import load_dotenv
import pymssql

load_dotenv()
server = os.getenv("sqlserver")
username = os.getenv("user")
password =os.getenv("password")

try:
        conn = pymssql.connect(server=server, user=username, password=password, database="ReckittSQLDB")
        print("Connection successful!")
except Exception as e:
        print(f"Error: {e}")
    

cursor = conn.cursor()

# Write a SQL query
cursor.execute("insert into emp_data1(emp_id, emp_fname, emp_lname)values(333, 'avijit', 'sam')")
cursor.execute("select * from emp_data1")
rows=cursor.fetchall()
for i in rows:
        print(i)


print("done")
conn.commit()

cursor.close()
conn.close()
