import mysql.connector
con = mysql.connector.connect(
    user='root',
    host='127.0.0.1',
    database='first',
    passwd='Sony@123'
)
# print(con)
cur = con.cursor()
cur.execute("CREATE TABLE customers (name VARCHAR(255),id int);")
con.commit()