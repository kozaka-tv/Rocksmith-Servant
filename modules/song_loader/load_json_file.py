import json
import os
import sqlite3
from datetime import datetime

JSON_FILE = 'SongsMasterGrid.json'
# JSON_FILE = 'SongsMasterGrid_BIG.json'

db = sqlite3.connect('servant.db')


def file_datetime(filename):
    file_time = os.path.getmtime(filename)
    formatted_time = datetime.fromtimestamp(file_time)
    print("File datetime: {0}".format(formatted_time))
    return formatted_time


file_datetime(JSON_FILE)

with open(JSON_FILE, encoding='utf-8-sig') as json_file:
    # TODO extract to a method the load of the file
    json_file_data = json.loads(json_file.read())
    songs = dict(json_file_data)
    json_data = songs['dgvSongsMaster']

    # Aim of this block is to get the list of the columns in the JSON file.
    columns = []
    column = []
    for data in json_data:
        column = list(data.keys())
        for col in column:
            if col not in columns:
                columns.append(col)

    # Here we get values of the columns in the JSON file in the right order.
    value = []
    values = []
    for data in json_data:
        for i in columns:
            value.append(str(dict(data).get(i)).strip())
        values.append(list(value))
        value.clear()

    # Time to generate the create and insert queries and apply it to the sqlite3 database
    drop_query = "drop table if exists songs"
    create_query = "create table if not exists songs ({0})".format(" text,".join(columns))
    insert_query = "insert into songs ({0}) values (?{1})".format(",".join(columns), ",?" * (len(columns) - 1))
    print("insert has started at " + str(datetime.now()))
    c = db.cursor()
    c.execute(drop_query)
    db.commit()
    c.execute(create_query)
    c.executemany(insert_query, values)
    values.clear()
    db.commit()
    c.close()
    print("insert has completed at " + str(datetime.now()))
