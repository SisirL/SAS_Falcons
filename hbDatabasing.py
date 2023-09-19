import mysql.connector as connector


def init_db():
    global connection
    try:
        connection = connector.connect(host = "localhost", user = "root", password = "0409")
        print("Connected")
    except Exception as exp:
        print(repr(exp))
    if not connection.is_connected():
        print("Connection failed")
    return

#__main()__
init_db()