from dotenv import load_dotenv
import os
load_dotenv()  # Loads the .env file in the current directory
import sys
# Access the environment variables
KEY = os.getenv('key')


import google.generativeai as genai
genai.configure(api_key=KEY)

def Generate_Content(prompt):
   model = genai.GenerativeModel('gemini-pro')
   chat = model.start_chat(history=[])

   response = chat.send_message(prompt)
   gemini_response = response.text
   return gemini_response


def main():
    question= input("question:\n")
    if question in ["NO","no"]:
        sys.exit()
        
    else:
        pass
#     prompt = f"""
#     Generate an SQL query to answer the following question {question} about the provided database schema.format the sql query in such manner i can directly put in sql query 
#     and it will give me result with out error:
#     table name: demo

#     table schema:
#     id INT PRIMARY KEY AUTO_INCREMENT,
#         name VARCHAR(100) NOT NULL,
#         ph VARCHAR(15),
#         area VARCHAR(100),
#         age INT ,
#         gender VARCHAR(10)
# """
    prompt=f"""
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
    print(response)
    query=response.replace("sql","")
    query=query.replace("```","")



    import mysql.connector
    from prettytable import PrettyTable

    # Define your connection parameters
    server = 'localhost'
    username ='root'
    password ='root'

    # Establish a connection
    try:
        connection = mysql.connector.connect(
                host=server,
                user=username,
                password=password,
                database="avijit")
    
    except Exception as e:
        print(f"Error: {e}")
    cur=connection.cursor()

    try:
        cur.execute(query)
        results=cur.fetchall()


        column_names = [description[0] for description in cur.description]

    # Create a PrettyTable object
        table = PrettyTable()

    # Add column names to the table
        table.field_names = column_names

    # Add rows to the table
        
        for row in results:
            table.add_row(row)

    # Print the table
        print("The output is :\n")
        print(table)
    except Exception as e:
        print(f"{e}")


if __name__=="__main__":
    while True:
        main()



# query="""
# INSERT INTO demo (id, name, ph, area, age, gender) VALUES
# (1, 'John Doe', '123-456-7890', 'New York', 25, 'Male'),
# (2, 'Jane Smith', '234-567-8901', 'Los Angeles', 30, 'Female'),
# (3, 'Michael Johnson', '345-678-9012', 'Chicago', 22, 'Male'),
# (4, 'Emily Davis', '456-789-0123', 'Houston', 28, 'Female'),
# (5, 'James Brown', '567-890-1234', 'Phoenix', 35, 'Male'),
# (6, 'Patricia Wilson', '678-901-2345', 'Philadelphia', 40, 'Female'),
# (7, 'Robert Miller', '789-012-3456', 'San Antonio', 29, 'Male'),
# (8, 'Linda Taylor', '890-123-4567', 'San Diego', 31, 'Female'),
# (9, 'William Anderson', '901-234-5678', 'Dallas', 27, 'Male'),
# (10, 'Elizabeth Thomas', '012-345-6789', 'San Jose', 33, 'Female'),
# (11, 'David Jackson', '123-456-7891', 'Austin', 24, 'Male'),
# (12, 'Susan White', '234-567-8902', 'Jacksonville', 36, 'Female'),
# (13, 'Joseph Harris', '345-678-9013', 'San Francisco', 38, 'Male'),
# (14, 'Jessica Martin', '456-789-0124', 'Columbus', 26, 'Female'),
# (15, 'Charles Thompson', '567-890-1235', 'Fort Worth', 32, 'Male'),
# (16, 'Sarah Garcia', '678-901-2346', 'Indianapolis', 29, 'Female'),
# (17, 'Thomas Martinez', '789-012-3457', 'Charlotte', 34, 'Male'),
# (18, 'Rebecca Robinson', '890-123-4568', 'Seattle', 27, 'Female'),
# (19, 'Daniel Clark', '901-234-5679', 'Denver', 30, 'Male'),
# (20, 'Laura Rodriguez', '012-345-6780', 'Washington', 28, 'Female'),
# (21, 'Matthew Lewis', '123-456-7892', 'Boston', 31, 'Male'),
# (22, 'Angela Lee', '234-567-8903', 'El Paso', 25, 'Female'),
# (23, 'Joshua Walker', '345-678-9014', 'Nashville', 29, 'Male'),
# (24, 'Kimberly Hall', '456-789-0125', 'Detroit', 33, 'Female'),
# (25, 'Andrew Allen', '567-890-1236', 'Memphis', 36, 'Male'),
# (26, 'Michelle Young', '678-901-2347', 'Baltimore', 22, 'Female'),
# (27, 'Christopher Hernandez', '789-012-3458', 'Milwaukee', 38, 'Male'),
# (28, 'Jessica King', '890-123-4569', 'Albuquerque', 27, 'Female'),
# (29, 'Kevin Wright', '901-234-5670', 'Tucson', 30, 'Male'),
# (30, 'Stephanie Scott', '012-345-6781', 'Fresno', 34, 'Female'),
# (31, 'Jason Green', '123-456-7893', 'Sacramento', 29, 'Male'),
# (32, 'Laura Adams', '234-567-8904', 'Kansas City', 31, 'Female'),
# (33, 'Eric Nelson', '345-678-9015', 'Long Beach', 25, 'Male'),
# (34, 'Rebecca Carter', '456-789-0126', 'Virginia Beach', 36, 'Female'),
# (35, 'Justin Mitchell', '567-890-1237', 'Atlanta', 28, 'Male'),
# (36, 'Kimberly Perez', '678-901-2348', 'Omaha', 33, 'Female'),
# (37, 'Charles Roberts', '789-012-3459', 'Raleigh', 29, 'Male'),
# (38, 'Patricia Turner', '890-123-4570', 'Miami', 30, ' Female'),
# (39, 'Matthew Phillips', '901-234-5671', 'Cleveland', 34, 'Male'),
# (40, 'Angela Campbell', '012-345-6782', 'Tulsa', 27, 'Female'),
# (41, 'Joshua Parker', '123-456-7894', 'Oakland', 31, 'Male'),
# (42, 'Kimberly Evans', '234-567-8905', 'Minneapolis', 25, 'Female'),
# (43, 'David Edwards', '345-678-9016', 'Wichita', 29, 'Male'),
# (44, 'Sarah Collins', '456-789-0127', 'New Orleans', 36, 'Female'),
# (45, 'Daniel Stewart', '567-890-1238', 'Arlington', 28, 'Male'),
# (46, 'Laura Sanchez', '678-901-2349', 'Bakersfield', 33, 'Female'),
# (47, 'Matthew Morris', '789-012-3460', 'Tampa', 30, 'Male'),
# (48, 'Rebecca Rogers', '890-123-4571', 'Honolulu', 34, 'Female'),
# (49, 'James Reed', '901-234-5672', 'Anaheim', 27, 'Male'),
# (50, 'Jessica Cook', '012-345-6783', 'Santa Ana', 31, 'Female'),
# (51, 'Charles Morgan', '123-456-7895', 'Corpus Christi', 25, 'Male'),
# (52, 'Angela Bell', '234-567-8906', 'Riverside', 29, 'Female'),
# (53, 'Joshua Murphy', '345-678-9017', 'St. Louis', 36, 'Male'),
# (54, 'Kimberly Rivera', '456-789-0128', 'Pittsburgh', 28, 'Female'),
# (55, 'David Cooper', '567-890-1239', 'Cincinnati', 33, 'Male'),
# (56, 'Sarah Richardson', '678-901-2350', 'Anchorage', 30, 'Female'),
# (57, 'Matthew Cox', '789-012-3461', 'Stockton', 34, 'Male'),
# (58, 'Laura Howard', '890-123-4572', 'Toledo', 27, 'Female'),
# (59, 'Daniel Ward', '901-234-5673', 'Greensboro', 31, 'Male'),
# (60, 'Rebecca Torres', '012-345-6784', 'Newark', 25, 'Female'),
# (61, 'Charles Peterson', '123-456-7896', 'Chula Vista', 29, 'Male'),
# (62, 'Angela Gray', '234-567-8907', 'Baton Rouge', 36, 'Female'),
# (63, 'Joshua Ramirez', '345-678-9018', 'Irvine', 28, 'Male'),
# (64, 'Kimberly James', '456-789-0129', 'Durham', 33, 'Female'),
# (65, 'David Watson', '567-890-1240', 'Chandler', 30, 'Male'),
# (66, 'Sarah Brooks', '678-901-2351', 'Madison', 34, 'Female'),
# (67, 'Matthew Kelly', '789-012-3462', 'Laredo', 27, 'Male'),
# (68, 'Laura Sanders', '890-123-4573', 'Scottsdale', 31, 'Female'),
# (69, 'Daniel Price', '901-234-5674', 'Birmingham', 25, 'Male'),
# (70, 'Rebecca Bennett', '012-345-6785', 'Boise', 29, 'Female'),
# (71, 'Charles Wood', '123-456-7897', 'Richmond', 36, 'Male'),
# (72, 'Angela Barnes', '234-567-8908', 'Spokane', 28, 'Female'),
# (73, 'Joshua Ross', '345-678-9019', 'Des Moines', 33, 'Male'),
# (74, 'Kimberly Henderson', '456-789-0130', 'Modesto', 30, 'Female'),
# (75, 'David Coleman', '567-890-1241', 'Fremont', 34, 'Male'),
# (76, 'Sarah Jenkins', '678-901-2352', 'Oxnard', 27, 'Female'),
# (77, 'Matthew Perry', '789-012-3463', 'Fontana', 31, 'Male');

# """
# cur.execute(query)
# cur.execute("commit;")
# print("done")
