import mysql.connector as connector
"""
Exceptions:
Exception for database does not exist - 1049 (42000): Unknown database 'psdatabase'
Exception for table does not exist - 1146 (42S02): Table 'psdatabase.data' doesn't exist

Format for table:
Location|Latitude|Longitude|Type of source|Nearest Power Substation|Latitude of SS|Longituse of SS|If active plant exists|If yes power supply capacity else none

Create Table command:
create table data(
location varchar(80),
latitudeL double,
longitudeL double,
sourceType varchar(20),
nearestSubstation varchar(80),
latitudeSS double,
longitudeSS double,
plantOwner varchar(80),
plantCapacity double
);
"""
pwd = "0409"


def init_db():
    global connection
    dbError = None
    try:
        connection = connector.connect(host = "localhost", user = "root", password = pwd, database = "psdatabase")
        print("Connected")
    except Exception as exp:
        dbError = str(exp)
    if dbError == "1049 (42000): Unknown database 'psdatabase'":
        connection = connector.connect(host = "localhost", user = "root", password = pwd)
        dbCursor = connection.cursor()
        dbCursor.execute("create database PSDataBase;")
        print("Database Created")
        dbCursor.close()
    if dbError != None and dbError != "1049 (42000): Unknown database 'psdatabase'":
        print("Unsolvable Error Encountered")
    return


def get_columns_query(tablename: str, columns: list, constraint: tuple = None, limit: int|str = None, order_by_col: list[str,] = None, order_by_asc: list[bool,] = None) -> str:
    if limit is not None:
        if not (isinstance(limit, (int, str))): return []
    query = f'select {", ".join(columns)} from {tablename}'
    if constraint is not None:
        if constraint[1] == "NULL":
            query += f" where {constraint[0]} is null"
        else:
            query += f" where {constraint[0]} like \"{constraint[1]}\""
    if order_by_col is not None:
        if len(order_by_col) == len(order_by_asc): 
            query += ' order by'
            for (col_name, order) in zip(order_by_col, order_by_asc):
                query += f" {col_name} {'asc' if order else 'desc'}"
    if limit is not None:
         query += f" limit {limit!s}"
    query += ';'
    return query

    
def get_columns(tablename: str, columns: list, constraint: tuple = None, limit: int|str = None, order_by_col: list[str,] = None, order_by_asc: list[bool,] = None) -> str:
    query = get_columns_query(tablename=tablename, columns=columns, constraint=constraint, limit=limit, order_by_col=order_by_col, order_by_asc=order_by_asc)
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return data


def createTable():
    tableCursor = connection.cursor()
    tableError = None
    tableCursor.execute("use psdatabase;")
    try:
        tableCursor.execute("select * from data;")
        garbage = tableCursor.fetchall()
    except Exception as exp:
        tableError = str(exp)
    if tableError == "1146 (42S02): Table 'psdatabase.data' doesn't exist":
        tableCursor.execute("create table data(location varchar(80), latitudeL double, longitudeL double, sourceType varchar(20), nearestSubstation varchar(80), latitudeSS double, longitudeSS double, plantOwner varchar(80), plantCapacity double);")
        print(tableCursor.fetchall())
        connection.commit()
        print("Table created")
    if tableError == None:
        print("Table detected")
    tableCursor.close()
    return


def readFile():
    global dataList
    dataList = []
    textFile = open("powerSources.txt", 'r')
    fileList = textFile.readlines()
    for i in fileList:
        tempList = []
        for j in i.split('|'):
            tempList.append(j.strip())
        dataList.append(tempList)
    textFile.close()
    return


def addValues():
    global dataList
    inputCursor = connection.cursor()
    inputCursor.execute("delete from data;")
    connection.commit()
    for i in range(len(dataList)):
        if dataList[i][7] == "None":
            dataList[i].append("NULL")
        tempList = dataList[i]
        inputCursor.execute(f"insert into data values(\"{tempList[0]}\", {tempList[1]}, {tempList[2]}, \"{tempList[3]}\", \"{tempList[4]}\", {tempList[5]}, {tempList[6]}, \"{tempList[7]}\", {tempList[8]});")
        connection.commit()
    inputCursor.close()
    print("Data has been updated")
    return


#__main()__

init_db()
createTable()
readFile()
addValues()