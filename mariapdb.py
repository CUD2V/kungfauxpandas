


import mysql.connector as mariadb

class pseudocursor(mysql.connector.cursor))
    # Overload all methods which return data
:

def main():
    mariadb_connection = mariadb.connect(user='python_user', password='some_pass', database='employees')
    cursor = mariadb_connection.cursor()
