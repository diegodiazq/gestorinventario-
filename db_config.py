import pyodbc

def get_connection():
    # Autenticación Windows y servidor proporcionado por el usuario
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-E26QEMQ\\SQLEXPRESS;"
        "DATABASE=Gestor_inventario;"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)
