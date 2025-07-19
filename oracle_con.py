import cx_Oracle
import oracledb
import os
import logging
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
import getpass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OracleConnection:
    """Oracle Database connection manager with multiple authentication methods"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect_basic(self, username: str, password: str, dsn: str) -> bool:
        """
        Basic Oracle connection with username/password
        DSN format: host:port/service_name or TNS name
        """
        try:
            self.connection = cx_Oracle.connect(
                user=username,
                password=password,
                dsn=dsn
            )
            self.cursor = self.connection.cursor()
            logger.info(f"Successfully connected to Oracle database: {dsn}")
            return True
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Oracle connection failed: {str(e)}")
            return False
    
    def connect_with_connection_string(self, connection_string: str) -> bool:
        """
        Connect using full connection string
        Format: username/password@host:port/service_name
        """
        try:
            self.connection = cx_Oracle.connect(connection_string)
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected using connection string")
            return True
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
    
    def connect_with_wallet(self, username: str, password: str, dsn: str, 
                           wallet_location: str, wallet_password: str = None) -> bool:
        """
        Connect using Oracle Wallet for secure authentication
        """
        try:
            # Configure wallet
            cx_Oracle.init_oracle_client(config_dir=wallet_location)
            
            if wallet_password:
                self.connection = cx_Oracle.connect(
                    user=username,
                    password=password,
                    dsn=dsn,
                    wallet_password=wallet_password
                )
            else:
                self.connection = cx_Oracle.connect(
                    user=username,
                    password=password,
                    dsn=dsn
                )
            
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected using Oracle Wallet")
            return True
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Wallet connection failed: {str(e)}")
            return False
    
    def connect_with_tns(self, username: str, password: str, tns_name: str, 
                        tns_admin_path: str = None) -> bool:
        """
        Connect using TNS names with optional TNS_ADMIN path
        """
        try:
            if tns_admin_path:
                os.environ['TNS_ADMIN'] = tns_admin_path
            
            self.connection = cx_Oracle.connect(
                user=username,
                password=password,
                dsn=tns_name
            )
            self.cursor = self.connection.cursor()
            logger.info(f"Successfully connected using TNS: {tns_name}")
            return True
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"TNS connection failed: {str(e)}")
            return False
    
    def connect_sysdba(self, username: str, password: str, dsn: str) -> bool:
        """
        Connect as SYSDBA (requires appropriate privileges)
        """
        try:
            self.connection = cx_Oracle.connect(
                user=username,
                password=password,
                dsn=dsn,
                mode=cx_Oracle.SYSDBA
            )
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected as SYSDBA")
            return True
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"SYSDBA connection failed: {str(e)}")
            return False

class OracleDatabaseOperations:
    """Oracle database operations wrapper"""
    
    def __init__(self, oracle_conn: OracleConnection):
        self.oracle_conn = oracle_conn
        self.connection = oracle_conn.connection
        self.cursor = oracle_conn.cursor
    
    def execute_query(self, query: str, params: tuple = None) -> List[Tuple]:
        """Execute SELECT query and return results"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            logger.info(f"Query executed successfully, returned {len(results)} rows")
            return results
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Query execution failed: {str(e)}")
            return []
    
    def execute_insert(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Insert data into specified table"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join([f':{key}' for key in data.keys()])
            
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            self.cursor.execute(query, data)
            self.connection.commit()
            
            logger.info(f"Successfully inserted data into {table_name}")
            return True
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Insert failed: {str(e)}")
            self.connection.rollback()
            return False
    
    def execute_bulk_insert(self, table_name: str, columns: List[str], 
                           data_list: List[List[Any]]) -> bool:
        """Execute bulk insert for better performance"""
        try:
            placeholders = ', '.join([f':{i+1}' for i in range(len(columns))])
            columns_str = ', '.join(columns)
            
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            self.cursor.executemany(query, data_list)
            self.connection.commit()
            
            logger.info(f"Successfully bulk inserted {len(data_list)} rows into {table_name}")
            return True
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Bulk insert failed: {str(e)}")
            self.connection.rollback()
            return False
    
    def execute_update(self, table_name: str, set_data: Dict[str, Any], 
                      where_clause: str, where_params: Dict[str, Any] = None) -> int:
        """Execute UPDATE statement"""
        try:
            set_clause = ', '.join([f"{key} = :{key}" for key in set_data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            
            # Combine parameters
            params = set_data.copy()
            if where_params:
                params.update(where_params)
            
            self.cursor.execute(query, params)
            rows_updated = self.cursor.rowcount
            self.connection.commit()
            
            logger.info(f"Successfully updated {rows_updated} rows in {table_name}")
            return rows_updated
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Update failed: {str(e)}")
            self.connection.rollback()
            return 0
    
    def execute_delete(self, table_name: str, where_clause: str, 
                      where_params: Dict[str, Any] = None) -> int:
        """Execute DELETE statement"""
        try:
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            
            if where_params:
                self.cursor.execute(query, where_params)
            else:
                self.cursor.execute(query)
            
            rows_deleted = self.cursor.rowcount
            self.connection.commit()
            
            logger.info(f"Successfully deleted {rows_deleted} rows from {table_name}")
            return rows_deleted
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Delete failed: {str(e)}")
            self.connection.rollback()
            return 0
    
    def call_stored_procedure(self, proc_name: str, params: List[Any]) -> Any:
        """Call Oracle stored procedure"""
        try:
            result = self.cursor.callproc(proc_name, params)
            self.connection.commit()
            
            logger.info(f"Successfully called procedure: {proc_name}")
            return result
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Procedure call failed: {str(e)}")
            return None
    
    def get_table_info(self, table_name: str) -> List[Tuple]:
        """Get table column information"""
        query = """
        SELECT column_name, data_type, nullable, data_length, data_precision, data_scale
        FROM user_tab_columns 
        WHERE table_name = UPPER(:table_name)
        ORDER BY column_id
        """
        return self.execute_query(query, (table_name,))

@contextmanager
def oracle_connection_context(connection_func, *args, **kwargs):
    """Context manager for Oracle connections"""
    oracle_conn = OracleConnection()
    try:
        if connection_func(oracle_conn, *args, **kwargs):
            yield OracleDatabaseOperations(oracle_conn)
        else:
            yield None
    finally:
        if oracle_conn.connection:
            oracle_conn.connection.close()
            logger.info("Oracle connection closed")

# Example usage functions
def example_basic_connection():
    """Example: Basic Oracle connection"""
    
    # Connection parameters
    username = "your_username"
    password = "your_password"  # Or use getpass.getpass("Password: ")
    dsn = "localhost:1521/XE"  # host:port/service_name
    
    oracle_conn = OracleConnection()
    
    if oracle_conn.connect_basic(username, password, dsn):
        db_ops = OracleDatabaseOperations(oracle_conn)
        
        # Example operations
        # 1. Simple query
        results = db_ops.execute_query("SELECT SYSDATE FROM DUAL")
        print(f"Current date: {results[0][0] if results else 'N/A'}")
        
        # 2. Insert data
        sample_data = {
            'id': 1,
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'created_date': 'SYSDATE'
        }
        db_ops.execute_insert('users', sample_data)
        
        # 3. Query data
        user_results = db_ops.execute_query(
            "SELECT * FROM users WHERE id = :id", 
            (1,)
        )
        print(f"User data: {user_results}")
        
        # Close connection
        oracle_conn.connection.close()

def example_tns_connection():
    """Example: TNS-based connection"""
    
    username = "your_username"
    password = getpass.getpass("Password: ")
    tns_name = "ORCL"  # TNS alias name
    tns_admin = "/path/to/tns/admin"  # Optional TNS_ADMIN path
    
    with oracle_connection_context(
        OracleConnection.connect_with_tns, 
        username, password, tns_name, tns_admin
    ) as db_ops:
        
        if db_ops:
            # Get database version
            version_result = db_ops.execute_query(
                "SELECT banner FROM v$version WHERE banner LIKE 'Oracle%'"
            )
            if version_result:
                print(f"Oracle Version: {version_result[0][0]}")
            
            # Get table information
            table_info = db_ops.get_table_info('EMPLOYEES')
            for column in table_info:
                print(f"Column: {column[0]}, Type: {column[1]}, Nullable: {column[2]}")

def example_bulk_operations():
    """Example: Bulk database operations"""
    
    connection_params = {
        'username': 'your_username',
        'password': 'your_password',
        'dsn': 'localhost:1521/XE'
    }
    
    with oracle_connection_context(
        OracleConnection.connect_basic, 
        **connection_params
    ) as db_ops:
        
        if db_ops:
            # Bulk insert example
            columns = ['id', 'name', 'department', 'salary']
            bulk_data = [
                [1, 'Alice Johnson', 'IT', 75000],
                [2, 'Bob Smith', 'HR', 65000],
                [3, 'Carol Davis', 'Finance', 70000],
                [4, 'David Wilson', 'IT', 80000]
            ]
            
            success = db_ops.execute_bulk_insert('employees', columns, bulk_data)
            if success:
                print("Bulk insert completed successfully")
            
            # Update example
            updated_rows = db_ops.execute_update(
                'employees',
                {'salary': 82000},
                'name = :name',
                {'name': 'David Wilson'}
            )
            print(f"Updated {updated_rows} employee records")
            
            # Query with results
            high_salary_employees = db_ops.execute_query(
                "SELECT name, department, salary FROM employees WHERE salary > :min_salary",
                {'min_salary': 70000}
            )
            
            print("High salary employees:")
            for emp in high_salary_employees:
                print(f"  {emp[0]} - {emp[1]} - ${emp[2]}")

def main():
    """Main function demonstrating Oracle connections"""
    
    print("Oracle Database Connection Examples")
    print("=" * 40)
    
    # Choose connection method
    connection_method = input("""
    Choose connection method:
    1. Basic connection (username/password/dsn)
    2. TNS connection
    3. Connection string
    4. Bulk operations example
    
    Enter choice (1-4): """)
    
    try:
        if connection_method == '1':
            example_basic_connection()
        elif connection_method == '2':
            example_tns_connection()
        elif connection_method == '3':
            # Connection string example
            conn_string = input("Enter connection string (user/pass@host:port/service): ")
            oracle_conn = OracleConnection()
            if oracle_conn.connect_with_connection_string(conn_string):
                print("Connection successful!")
                oracle_conn.connection.close()
        elif connection_method == '4':
            example_bulk_operations()
        else:
            print("Invalid choice")
            
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")

if __name__ == "__main__":
    main()
