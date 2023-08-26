"""Provides common MySQL queries used by NetClam OSS."""

MYSQL_FILE_QUERY = "SELECT name FROM files WHERE request_id='{0}'"
MYSQL_REQUEST_QUERY = "SELECT id, status, created_time, updated_time FROM requests WHERE id='{0}'"
MYSQL_RESULT_QUERY = "SELECT decision, decision_time FROM results WHERE request_id='{0}'"
MYSQL_INSERT_FILE = "INSERT INTO files (request_id, name) VALUES ('{0}', '{1}')"
MYSQL_INSERT_REQUEST = "INSERT INTO requests (id, status, created_time, updated_time) \
    VALUES ('{0}', '{1}', NOW(), NOW())"
