from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import pandas as pd

#sql libs
import os
from dotenv import load_dotenv
import pymssql

#ADLS CREDS
account_name = ''
account_key = ''
container_name = ''

#connect to adls specif file 
sas_i = generate_blob_sas(account_name = account_name,
                                container_name = container_name,
                                blob_name = 'sample_01.csv',
                                account_key=account_key,
                                permission=BlobSasPermissions(read=True),
                                expiry=datetime.utcnow() + timedelta(hours=1))
sas_url = 'https://' + account_name+'.blob.core.windows.net/' + container_name + '/' + "sample_01.csv" + '?' + sas_i
    
df = pd.read_csv(sas_url)
print(df)



#SQL


load_dotenv()
server = os.getenv("sqlserver")
username = os.getenv("user")
password =os.getenv("password")
try:
        conn = pymssql.connect(server=server, user=username, password=password, database="ReckittSQLDB")
        print("Connection successful!")
except Exception as e:
        print(f"Error: {e}")


csr=conn.cursor()
columns=','.join(df.columns)
placeholders=','.join(['%s'] * len(df.columns))
insert_stmt = f"INSERT INTO emp_data1 ({columns}) VALUES ({placeholders})"

for index,row in df.iterrows():
        csr.execute(insert_stmt,tuple(row))
conn.commit()
csr.close
print("successfully inserted")
