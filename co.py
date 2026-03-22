import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="yourdb"
)

cursor = db.cursor()
cursor.execute("SELECT * FROM your_table")

for row in cursor:
    print(row)