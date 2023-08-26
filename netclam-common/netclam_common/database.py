"""Module providing database functionality used by NetClam OSS."""

import os
from time import sleep
from uuid import uuid4
from mysql.connector import errorcode
from netclam_common import query
from netclam_common.exception import MySQLConnectionException, FileNotFoundException, \
    RequestNotFoundException, ResultNotFoundException
from netclam_common.models.file import file
from netclam_common.models.request import request, PENDING
from netclam_common.models.result import result
import mysql.connector

MAX_FETCH_RETRIES = 3
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_ENDPOINT = os.environ.get("MYSQL_ENDPOINT")

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
            raise MySQLConnectionException(
                "MySQL Error: Invalid username/password or permissions."
            ) from err
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise MySQLConnectionException(
                "MySQL Error: Invalid database."
            ) from err
        else:
            raise MySQLConnectionException(
                "MySQL Error: Unknown error occurred."
            ) from err
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
    conn, cursor = get_mysql_conn(MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_ENDPOINT)
    attempt = 0
    data = None
    while data is None and attempt < MAX_FETCH_RETRIES:
        if attempt > 0:
            sleep(0.10)
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
    conn, cursor = get_mysql_conn(MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_ENDPOINT)
    cursor.execute(statement)
    conn.commit()
    dispose_mysql(conn, cursor)

def get_file(id: str) -> file:
    """Gets result object from MySQL

    :param id: Request ID
    :type id: str
    :raises ResultNotFoundException: Result not found
    :return: Result object
    :rtype: result
    """
    data = fetch_one_mysql(query.MYSQL_FILE_QUERY.format(id))
    if data is None:
        raise FileNotFoundException(f"Unable to find file for request with id: {id}")
    return file(*data)

def get_request(id: str) -> request:
    """Gets request object from MySQL

    :param id: Request ID
    :type id: str
    :raises RequestNotFoundException: Request not found
    :return: Request object
    :rtype: request
    """
    data = fetch_one_mysql(query.MYSQL_REQUEST_QUERY.format(id))
    if data is None:
        raise RequestNotFoundException(f"Unable to find request with id: {id}")
    return request(*data)

def get_result(id: str) -> result:
    """Gets result object from MySQL

    :param id: Request ID
    :type id: str
    :raises ResultNotFoundException: Result not found
    :return: Result object
    :rtype: result
    """
    data = fetch_one_mysql(query.MYSQL_RESULT_QUERY.format(id))
    if data is None:
        raise ResultNotFoundException(f"Unable to find result for request with id: {id}")
    return result(*data)

def create_new_request_id() -> str:
    """Returns a unique request ID

    :return: Unique Request ID
    :rtype: str
    """
    request_id = uuid4()
    while fetch_one_mysql(query.MYSQL_REQUEST_QUERY.format(request_id)) is not None:
        request_id = uuid4()
    return request_id

def create_request(file_name: str) -> request:
    """Creates a new request

    :param file_name: Name of file to be scanned
    :type file_name: str
    """
    request_id = create_new_request_id()
    insert_mysql(query.MYSQL_INSERT_REQUEST.format(request_id, PENDING))
    insert_mysql(query.MYSQL_INSERT_FILE.format(request_id, file_name))
    return request(*fetch_one_mysql(query.MYSQL_REQUEST_QUERY.format(request_id)))
