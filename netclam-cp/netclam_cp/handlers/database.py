import mysql.connector
from mysql.connector import errorcode
from models.result import result
from models.request import request
from uuid import uuid4
from models import request_status
import os
from time import sleep

mysql_database = os.environ.get("MYSQL_DATABASE")
mysql_user = os.environ.get("MYSQL_USER")
mysql_password = os.environ.get("MYSQL_PASSWORD")
mysql_endpoint = os.environ.get("MYSQL_ENDPOINT")
mysql_file_query = "SELECT name FROM files WHERE request_id='{0}'"
mysql_request_query = "SELECT id, status, created_time, updated_time FROM requests WHERE id='{0}'"
mysql_request_status_query = "SELECT status FROM requests WHERE id='{0}'"
mysql_result_query = "SELECT decision, decision_time FROM results WHERE request_id='{0}'"
mysql_insert_file = "INSERT INTO files (request_id, name) VALUES ('{0}', '{1}')"
mysql_insert_request = "INSERT INTO requests (id, status, created_time, updated_time) VALUES ('{0}', '{1}', NOW(), NOW())"
max_fetch_retries = 3

def get_mysql_conn(username: str, password: str, database: str, hostname: str = "localhost") -> tuple:
    """_summary_

    :param username: MySQL Username
    :type username: str
    :param password: MySQL Password
    :type password: str
    :param database: MySQL Database
    :type database: str
    :param hostname: MySQL Server Hostname, defaults to "localhost"
    :type hostname: str, optional
    :raises Exception: Invalid username/password
    :raises Exception: Invalid database
    :raises Exception: Unknown error
    :return: MySQL Connection, MySQL Cursor
    :rtype: tuple
    """
    try:
        conn = mysql.connector.connect(
            host = hostname,
            user = username,
            password = password,
            database = database
        )
        cursor = conn.cursor()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise Exception("MySQL Error: Invalid username/password or permissions.") from err
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise Exception("MySQL Error: Invalid database.") from err
        else:
            raise Exception("MySQL Error: Unknown error occurred.") from err
    return conn, cursor

def dispose_mysql(conn, cursor):
    """Cleanly disposes of mysql cursor and connection

    :param conn: MySQL connection being disposed
    :type conn: connection.MySQLConnection
    :param cursor: MySQL cursor being disposed
    :type cursor: cursor.MySQLCursor
    """
    cursor.close()
    conn.close()

def fetch_one_mysql(query: str):
    """Fetches the first row of data returned by a MySQL query

    :param query: MySQL query to be executed
    :type query: str
    :return: First row from query result set
    :rtype: tuple
    """
    conn, cursor = get_mysql_conn(mysql_user, mysql_password, mysql_database, mysql_endpoint)
    attempt = 0
    data = None
    while data == None and attempt < max_fetch_retries:
        if attempt > 0:
            sleep(0.05)
        cursor.execute(query)
        data = cursor.fetchone()
        attempt += 1
    dispose_mysql(conn, cursor)
    return data

def insert_mysql(statement: str):
    """Inserts a row of data using a MySQL statement

    :param statement: MySQL statement to be executed
    :type statement: str
    """
    conn, cursor = get_mysql_conn(mysql_user, mysql_password, mysql_database, mysql_endpoint)
    cursor.execute(statement)
    conn.commit()
    dispose_mysql(conn, cursor)

def get_request_status(request_id: str) -> str:
    """Returns the status of a request

    :param request_id: Request ID in uuid4 format
    :type request_id: str
    :raises Exception: Request not found
    :return: Request status
    :rtype: str
    """
    data = fetch_one_mysql(mysql_request_status_query.format(request_id))
    if data == None:
        raise Exception("Request not found.")
    status = data[0]
    return status

def get_result(request_id: str) -> result:
    """Returns a result of a scan

    :param request_id: Request ID in uuid4 format
    :type request_id: str
    :raises Exception: Request not found
    :return: Result
    :rtype: result
    """
    data = list(fetch_one_mysql(mysql_result_query.format(request_id)))
    if data == None:
        raise Exception("Result not found.")
    data.insert(0, request_id)
    return result(*data)

def create_new_request_id() -> str:
    """Returns a unique request ID

    :return: Unique Request ID
    :rtype: str
    """
    request_id = uuid4()
    while fetch_one_mysql(mysql_request_query.format(request_id)) != None:
        request_id = uuid4()
    return request_id

def create_request(file_name: str):
    """Creates a new request

    :param file_name: Name of file to be scanned
    :type file_name: str
    """
    request_id = create_new_request_id()
    insert_mysql(mysql_insert_request.format(request_id, request_status.PENDING))
    insert_mysql(mysql_insert_file.format(request_id, file_name))
    return request(*fetch_one_mysql(mysql_request_query.format(request_id)))