#!/bin/sh
# FAILED: sh create_show_sqlite3_db.sh /home/schakrab02/drsa/ai-gcp-5d/stockanalyst_session.db
# cd /home/schakrab02/drsa/ai-gcp-5d;  sh create_show_sqlite3_db.sh stockanalyst_session.db

if [ $# -le 0 ]; then
    echo "$0:\n  Usage: $0 <Sqlite3 Database file name from working directory>"
    echo "  Example: cd /home/schakrab02/drsa/ai-gcp-5d/aiagent-st-fsi;  sh create_show_sqlite3_db.sh stockanalyst_session.db"
    exit 1
fi
echo "DB Name: $1"
export SQLITE3_DB_NAME="${1}"

python -c "
import os
import sys
import sqlite3
from google.adk.sessions import DatabaseSessionService

DB_NAME=f'{os.environ.get(\"SQLITE3_DB_NAME\", \"INVALID DB NAME\")}'
db_url=f'sqlite:///{DB_NAME}'

print(f'DB NAME: {DB_NAME}   DB URL: {db_url}')

def check_data_in_db(db_name: str):
    print(f'Showing data from Sqlite3 Database: {db_name}')
    with sqlite3.connect(db_name) as connection:
        cursor = connection.cursor()
        result = cursor.execute('select app_name, session_id, author, content from events')
        print([_[0] for _ in result.description])
        for each in result.fetchall():
            print(each)

session_service_db = None
try:
    session_service_db = DatabaseSessionService(db_url=db_url)
except Exception as ex:
    print(f'Error creating Database: {ex}')

if session_service_db is not None:
    print(f'Database created as {db_url}')
#    check_data_in_db(db_url)
    check_data_in_db(DB_NAME)




"
