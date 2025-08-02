import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import pyodbc
import oracledb  # Modern Oracle driver (replaces cx_Oracle)
# Alternative imports for SQLAlchemy approach
from sqlalchemy import create_engine, text
import csv
from datetime import datetime
import threading
import os

class DatabaseComparisonTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Comparison Tool - SQL Server & Oracle")
        self.root.geometry("1200x800")
        
        # Database connections
        self.sql_server_conn = None
        self.oracle_conn = None
        self.sql_server_engine = None  # SQLAlchemy engine
        self.oracle_engine = None      # SQLAlchemy engine
        
        # Connection method selector
        self.connection_method = tk.StringVar(value="native")  # "native" or "sqlalchemy"
        
        # Data storage
        self.sql_server_data = None
        self.oracle_data = None
        self.discrepancies = []
        self.differing_rows_sql = pd.DataFrame()
        self.differing_rows_oracle = pd.DataFrame()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Connection Tab
        self.connection_frame = ttk.Frame(notebook)
        notebook.add(self.connection_frame, text="Database Connections")
        self.setup_connection_tab()
        
        # Query Tab
        self.query_frame = ttk.Frame(notebook)
        notebook.add(self.query_frame, text="Query & Compare")
        self.setup_query_tab()
        
        # Results Tab
        self.results_frame = ttk.Frame(notebook)
        notebook.add(self.results_frame, text="Results & Export")
        self.setup_results_tab()
        
    def setup_connection_tab(self):
        # Connection method selection
        method_frame = ttk.LabelFrame(self.connection_frame, text="Connection Method", padding=10)
        method_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Radiobutton(method_frame, text="Native Drivers (pyodbc + oracledb)", 
                       variable=self.connection_method, value="native").pack(side='left', padx=5)
        ttk.Radiobutton(method_frame, text="SQLAlchemy (Universal)", 
                       variable=self.connection_method, value="sqlalchemy").pack(side='left', padx=5)
        
        # SQL Server Connection Frame
        sql_frame = ttk.LabelFrame(self.connection_frame, text="SQL Server Connection", padding=10)
        sql_frame.pack(fill='x', padx=10, pady=5)
        
        # SQL Server fields
        ttk.Label(sql_frame, text="Server:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.sql_server_entry = ttk.Entry(sql_frame, width=30)
        self.sql_server_entry.grid(row=0, column=1, padx=5, pady=2)
        self.sql_server_entry.insert(0, "localhost")
        
        ttk.Label(sql_frame, text="Database:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.sql_database_entry = ttk.Entry(sql_frame, width=30)
        self.sql_database_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(sql_frame, text="Username:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.sql_username_entry = ttk.Entry(sql_frame, width=30)
        self.sql_username_entry.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(sql_frame, text="Password:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.sql_password_entry = ttk.Entry(sql_frame, show="*", width=30)
        self.sql_password_entry.grid(row=3, column=1, padx=5, pady=2)
        
        self.sql_connect_btn = ttk.Button(sql_frame, text="Connect to SQL Server", 
                                         command=self.connect_sql_server)
        self.sql_connect_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.sql_status_label = ttk.Label(sql_frame, text="Not Connected", foreground="red")
        self.sql_status_label.grid(row=5, column=0, columnspan=2)
        
        # Oracle Connection Frame
        oracle_frame = ttk.LabelFrame(self.connection_frame, text="Oracle Connection", padding=10)
        oracle_frame.pack(fill='x', padx=10, pady=5)
        
        # Oracle fields
        ttk.Label(oracle_frame, text="Host:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.oracle_host_entry = ttk.Entry(oracle_frame, width=30)
        self.oracle_host_entry.grid(row=0, column=1, padx=5, pady=2)
        self.oracle_host_entry.insert(0, "localhost")
        
        ttk.Label(oracle_frame, text="Port:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.oracle_port_entry = ttk.Entry(oracle_frame, width=30)
        self.oracle_port_entry.grid(row=1, column=1, padx=5, pady=2)
        self.oracle_port_entry.insert(0, "1521")
        
        ttk.Label(oracle_frame, text="Service Name:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.oracle_service_entry = ttk.Entry(oracle_frame, width=30)
        self.oracle_service_entry.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(oracle_frame, text="Username:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.oracle_username_entry = ttk.Entry(oracle_frame, width=30)
        self.oracle_username_entry.grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(oracle_frame, text="Password:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.oracle_password_entry = ttk.Entry(oracle_frame, show="*", width=30)
        self.oracle_password_entry.grid(row=4, column=1, padx=5, pady=2)
        
        self.oracle_connect_btn = ttk.Button(oracle_frame, text="Connect to Oracle", 
                                           command=self.connect_oracle)
        self.oracle_connect_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.oracle_status_label = ttk.Label(oracle_frame, text="Not Connected", foreground="red")
        self.oracle_status_label.grid(row=6, column=0, columnspan=2)
        
    def setup_query_tab(self):
        # Query frames
        query_frame = ttk.Frame(self.query_frame)
        query_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # SQL Server Query
        sql_query_frame = ttk.LabelFrame(query_frame, text="SQL Server Query", padding=5)
        sql_query_frame.pack(fill='both', expand=True, pady=5)
        
        self.sql_query_text = scrolledtext.ScrolledText(sql_query_frame, height=8, width=80)
        self.sql_query_text.pack(fill='both', expand=True)
        self.sql_query_text.insert('1.0', "SELECT * FROM your_table ORDER BY id")
        
        # Oracle Query
        oracle_query_frame = ttk.LabelFrame(query_frame, text="Oracle Query", padding=5)
        oracle_query_frame.pack(fill='both', expand=True, pady=5)
        
        self.oracle_query_text = scrolledtext.ScrolledText(oracle_query_frame, height=8, width=80)
        self.oracle_query_text.pack(fill='both', expand=True)
        self.oracle_query_text.insert('1.0', "SELECT * FROM your_table ORDER BY id")
        
        # Control buttons
        button_frame = ttk.Frame(self.query_frame)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.execute_btn = ttk.Button(button_frame, text="Execute Queries & Compare", 
                                     command=self.execute_and_compare)
        self.execute_btn.pack(side='left', padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Results", 
                                   command=self.clear_results)
        self.clear_btn.pack(side='left', padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side='right', padx=5)
        
    def setup_results_tab(self):
        # Results display
        results_notebook = ttk.Notebook(self.results_frame)
        results_notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Summary tab
        summary_frame = ttk.Frame(results_notebook)
        results_notebook.add(summary_frame, text="Summary")
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=15, width=80)
        self.summary_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Discrepancies tab
        discrepancies_frame = ttk.Frame(results_notebook)
        results_notebook.add(discrepancies_frame, text="Discrepancies")
        
        # Treeview for discrepancies
        tree_frame = ttk.Frame(discrepancies_frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.discrepancy_tree = ttk.Treeview(tree_frame)
        self.discrepancy_tree.pack(side='left', fill='both', expand=True)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.discrepancy_tree.yview)
        tree_scrollbar.pack(side='right', fill='y')
        self.discrepancy_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Export frame
        export_frame = ttk.Frame(self.results_frame)
        export_frame.pack(fill='x', padx=10, pady=5)
        
        self.export_btn = ttk.Button(export_frame, text="Export Discrepancies to CSV", 
                                    command=self.export_to_csv)
        self.export_btn.pack(side='left', padx=5)
        
        self.export_sql_rows_btn = ttk.Button(export_frame, text="Export SQL Server Differing Rows", 
                                             command=self.export_sql_differing_rows)
        self.export_sql_rows_btn.pack(side='left', padx=5)
        
        self.export_oracle_rows_btn = ttk.Button(export_frame, text="Export Oracle Differing Rows", 
                                                command=self.export_oracle_differing_rows)
        self.export_oracle_rows_btn.pack(side='left', padx=5)
        
        self.save_summary_btn = ttk.Button(export_frame, text="Save Summary Report", 
                                          command=self.save_summary)
        self.save_summary_btn.pack(side='left', padx=5)
        
    def connect_sql_server(self):
        try:
            server = self.sql_server_entry.get()
            database = self.sql_database_entry.get()
            username = self.sql_username_entry.get()
            password = self.sql_password_entry.get()
            
            if self.connection_method.get() == "native":
                # Native pyodbc connection
                if username and password:
                    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
                else:
                    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
                
                self.sql_server_conn = pyodbc.connect(conn_str)
                
            else:
                # SQLAlchemy connection
                if username and password:
                    conn_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
                else:
                    conn_str = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
                
                self.sql_server_engine = create_engine(conn_str)
                # Test connection
                with self.sql_server_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            
            self.sql_status_label.config(text="Connected", foreground="green")
            messagebox.showinfo("Success", "Connected to SQL Server successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to SQL Server: {str(e)}")
            self.sql_status_label.config(text="Connection Failed", foreground="red")
    
    def connect_oracle(self):
        try:
            host = self.oracle_host_entry.get()
            port = self.oracle_port_entry.get()
            service = self.oracle_service_entry.get()
            username = self.oracle_username_entry.get()
            password = self.oracle_password_entry.get()
            
            if self.connection_method.get() == "native":
                # Modern oracledb connection (thick mode not required for basic operations)
                dsn = f"{host}:{port}/{service}"
                self.oracle_conn = oracledb.connect(user=username, password=password, dsn=dsn)
                
            else:
                # SQLAlchemy connection
                conn_str = f"oracle+oracledb://{username}:{password}@{host}:{port}/?service_name={service}"
                self.oracle_engine = create_engine(conn_str)
                # Test connection
                with self.oracle_engine.connect() as conn:
                    conn.execute(text("SELECT 1 FROM DUAL"))
            
            self.oracle_status_label.config(text="Connected", foreground="green")
            messagebox.showinfo("Success", "Connected to Oracle successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Oracle: {str(e)}")
            self.oracle_status_label.config(text="Connection Failed", foreground="red")
    
    def execute_and_compare(self):
        # Check connections based on method
        if self.connection_method.get() == "native":
            if not self.sql_server_conn or not self.oracle_conn:
                messagebox.showerror("Error", "Please connect to both databases first!")
                return
        else:
            if not self.sql_server_engine or not self.oracle_engine:
                messagebox.showerror("Error", "Please connect to both databases first!")
                return
        
        # Start progress bar
        self.progress.start()
        self.execute_btn.config(state='disabled')
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._execute_and_compare_thread)
        thread.daemon = True
        thread.start()
    
    def _execute_and_compare_thread(self):
        try:
            # Get queries
            sql_query = self.sql_query_text.get('1.0', tk.END).strip()
            oracle_query = self.oracle_query_text.get('1.0', tk.END).strip()
            
            if self.connection_method.get() == "native":
                # Execute using native connections
                self.sql_server_data = pd.read_sql(sql_query, self.sql_server_conn)
                self.oracle_data = pd.read_sql(oracle_query, self.oracle_conn)
            else:
                # Execute using SQLAlchemy engines
                self.sql_server_data = pd.read_sql(text(sql_query), self.sql_server_engine)
                self.oracle_data = pd.read_sql(text(oracle_query), self.oracle_engine)
            
            # Compare data
            self._compare_data()
            
            # Update UI in main thread
            self.root.after(0, self._update_results_ui)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Execution failed: {str(e)}"))
        finally:
            self.root.after(0, self._finish_execution)
    
    def _compare_data(self):
        self.discrepancies = []
        self.differing_rows_sql = pd.DataFrame()
        self.differing_rows_oracle = pd.DataFrame()
        
        # Check if both datasets have the same shape
        if self.sql_server_data.shape != self.oracle_data.shape:
            self.discrepancies.append({
                'Type': 'Shape Mismatch',
                'Details': f"SQL Server: {self.sql_server_data.shape[0]} rows, {self.sql_server_data.shape[1]} columns | Oracle: {self.oracle_data.shape[0]} rows, {self.oracle_data.shape[1]} columns"
            })
        
        # Check column names
        sql_cols = set(self.sql_server_data.columns)
        oracle_cols = set(self.oracle_data.columns)
        
        if sql_cols != oracle_cols:
            missing_in_oracle = sql_cols - oracle_cols
            missing_in_sql = oracle_cols - sql_cols
            
            if missing_in_oracle:
                self.discrepancies.append({
                    'Type': 'Columns Missing in Oracle',
                    'Details': ', '.join(missing_in_oracle)
                })
            
            if missing_in_sql:
                self.discrepancies.append({
                    'Type': 'Columns Missing in SQL Server',
                    'Details': ', '.join(missing_in_sql)
                })
        
        # Get common columns for comparison
        common_cols = list(sql_cols.intersection(oracle_cols))
        
        if not common_cols:
            self.discrepancies.append({
                'Type': 'No Common Columns',
                'Details': 'Cannot compare data - no matching columns found'
            })
            return
        
        # Ensure both dataframes have the same number of rows for comparison
        min_rows = min(len(self.sql_server_data), len(self.oracle_data))
        
        if len(self.sql_server_data) != len(self.oracle_data):
            self.discrepancies.append({
                'Type': 'Row Count Mismatch',
                'Details': f"SQL Server: {len(self.sql_server_data)} rows | Oracle: {len(self.oracle_data)} rows"
            })
        
        # Prepare dataframes for comparison (same columns, same row count)
        sql_compare = self.sql_server_data[common_cols].head(min_rows).reset_index(drop=True)
        oracle_compare = self.oracle_data[common_cols].head(min_rows).reset_index(drop=True)
        
        # Direct dataframe comparison using pandas
        try:
            # Compare dataframes - this creates a boolean mask
            comparison_result = sql_compare.equals(oracle_compare)
            
            if comparison_result:
                self.discrepancies.append({
                    'Type': 'No Differences',
                    'Details': 'All data matches perfectly!'
                })
            else:
                # Find rows that are different
                # Use pandas compare method (available in pandas 1.1.0+)
                try:
                    # Method 1: Using pandas compare (modern approach)
                    diff_mask = ~(sql_compare == oracle_compare).all(axis=1)
                    differing_row_indices = diff_mask[diff_mask].index.tolist()
                    
                except:
                    # Method 2: Fallback for older pandas versions
                    differing_row_indices = []
                    for idx in range(len(sql_compare)):
                        if not sql_compare.iloc[idx].equals(oracle_compare.iloc[idx]):
                            differing_row_indices.append(idx)
                
                # Store differing rows
                if differing_row_indices:
                    self.differing_rows_sql = self.sql_server_data.iloc[differing_row_indices].copy()
                    self.differing_rows_oracle = self.oracle_data.iloc[differing_row_indices].copy()
                    
                    # Add row index for reference
                    self.differing_rows_sql.insert(0, 'Original_Row_Index', differing_row_indices)
                    self.differing_rows_oracle.insert(0, 'Original_Row_Index', differing_row_indices)
                    
                    self.discrepancies.append({
                        'Type': 'Data Differences Found',
                        'Details': f"Found {len(differing_row_indices)} differing rows out of {min_rows} compared rows"
                    })
                    
                    # Additional detailed analysis for summary
                    for idx in differing_row_indices[:10]:  # Show details for first 10 differences
                        sql_row = sql_compare.iloc[idx]
                        oracle_row = oracle_compare.iloc[idx]
                        
                        diff_cols = []
                        for col in common_cols:
                            if pd.isna(sql_row[col]) and pd.isna(oracle_row[col]):
                                continue
                            if sql_row[col] != oracle_row[col]:
                                diff_cols.append(col)
                        
                        if diff_cols:
                            self.discrepancies.append({
                                'Type': f'Row {idx} Differences',
                                'Details': f"Columns with differences: {', '.join(diff_cols)}"
                            })
                
        except Exception as e:
            self.discrepancies.append({
                'Type': 'Comparison Error',
                'Details': f"Error during comparison: {str(e)}"
            })
    
    def _update_results_ui(self):
        # Update summary
        summary = f"Comparison Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += "=" * 60 + "\n\n"
        summary += f"SQL Server Data: {self.sql_server_data.shape[0]} rows, {self.sql_server_data.shape[1]} columns\n"
        summary += f"Oracle Data: {self.oracle_data.shape[0]} rows, {self.oracle_data.shape[1]} columns\n"
        summary += f"Total Issues Found: {len(self.discrepancies)}\n"
        
        if not self.differing_rows_sql.empty:
            summary += f"Differing Rows: {len(self.differing_rows_sql)}\n"
        
        summary += "\n"
        
        if self.discrepancies:
            summary += "Issues Found:\n"
            for i, disc in enumerate(self.discrepancies, 1):
                summary += f"  {i}. {disc['Type']}: {disc['Details']}\n"
        else:
            summary += "No discrepancies found! Data matches perfectly.\n"
        
        if not self.differing_rows_sql.empty:
            summary += f"\nDiffering rows have been identified and can be exported separately.\n"
            summary += f"Use the export buttons to save SQL Server and Oracle differing rows to CSV files.\n"
        
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', summary)
        
        # Update discrepancy tree
        for item in self.discrepancy_tree.get_children():
            self.discrepancy_tree.delete(item)
        
        if self.discrepancies:
            columns = ['Type', 'Details']
            self.discrepancy_tree['columns'] = columns
            self.discrepancy_tree['show'] = 'headings'
            
            for col in columns:
                self.discrepancy_tree.heading(col, text=col)
                if col == 'Type':
                    self.discrepancy_tree.column(col, width=200)
                else:
                    self.discrepancy_tree.column(col, width=400)
            
            for i, disc in enumerate(self.discrepancies):
                values = [disc['Type'], disc['Details']]
                self.discrepancy_tree.insert('', 'end', values=values)
    
    def _finish_execution(self):
        self.progress.stop()
        self.execute_btn.config(state='normal')
    
    def clear_results(self):
        self.summary_text.delete('1.0', tk.END)
        for item in self.discrepancy_tree.get_children():
            self.discrepancy_tree.delete(item)
        self.discrepancies = []
        self.differing_rows_sql = pd.DataFrame()
        self.differing_rows_oracle = pd.DataFrame()
    
    def export_to_csv(self):
        if not self.discrepancies:
            messagebox.showwarning("Warning", "No discrepancies to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Discrepancies Summary"
        )
        
        if filename:
            try:
                # Create a simple discrepancies summary
                summary_data = []
                for disc in self.discrepancies:
                    summary_data.append({
                        'Issue_Type': disc['Type'],
                        'Details': disc['Details']
                    })
                
                df = pd.DataFrame(summary_data)
                df.to_csv(filename, index=False)
                
                messagebox.showinfo("Success", f"Discrepancies summary exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def export_sql_differing_rows(self):
        if self.differing_rows_sql.empty:
            messagebox.showwarning("Warning", "No differing SQL Server rows to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save SQL Server Differing Rows"
        )
        
        if filename:
            try:
                self.differing_rows_sql.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"SQL Server differing rows exported to {filename}\nTotal rows: {len(self.differing_rows_sql)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def export_oracle_differing_rows(self):
        if self.differing_rows_oracle.empty:
            messagebox.showwarning("Warning", "No differing Oracle rows to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Oracle Differing Rows"
        )
        
        if filename:
            try:
                self.differing_rows_oracle.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Oracle differing rows exported to {filename}\nTotal rows: {len(self.differing_rows_oracle)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def save_summary(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Summary Report"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.summary_text.get('1.0', tk.END))
                
                messagebox.showinfo("Success", f"Summary saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save summary: {str(e)}")
    
    def __del__(self):
        # Close database connections
        try:
            if self.sql_server_conn:
                self.sql_server_conn.close()
            if self.oracle_conn:
                self.oracle_conn.close()
            if self.sql_server_engine:
                self.sql_server_engine.dispose()
            if self.oracle_engine:
                self.oracle_engine.dispose()
        except:
            pass  # Ignore cleanup errors

def main():
    root = tk.Tk()
    app = DatabaseComparisonTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
