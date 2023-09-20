from turtle import distance
import mysql.connector as connector
import matplotlib.pyplot as plt
import numpy as np
import smtplib
from email.message import EmailMessage
import random


"""
User - tEst, password - pAss
Exceptions:
Exception for database does not exist - 1049 (42000): Unknown database 'psdatabase'
Exception for table does not exist - 1146 (42S02): Table 'psdatabase.data' doesn't exist

demand energy is in GigaWatt hours

Format for table:
Location|Latitude|Longitude|Type of source|Nearest Power Substation|Latitude of SS|Longituse of SS|If active plant exists|If yes power supply capacity else none

Create Table command:
create table plantStationData(
location varchar(150),
latitudeL double,
longitudeL double,
sourceType varchar(20),
nearestSubstation varchar(150),
latitudeSS double,
longitudeSS double,
plantOwner varchar(150),
plantCapacity double
);

create table demandData(
location varchar(150),
latitude double,
longitude double,
powerDemand double,
growthRate float
);

create table users(
emailID varchar(40),
pass varchar(40)
);
"""

pwd = "0409"


def init_db():
    global connection
    dbError = None
    try:
        connection = connector.connect(host="localhost", user="root", password=pwd, database="psdatabase")
        # print("Connected to database")
    except Exception as exp:
        dbError = str(exp)
    if dbError == "1049 (42000): Unknown database 'psdatabase'":
        connection = connector.connect(host="localhost", user="root", password=pwd)
        dbCursor = connection.cursor()
        dbCursor.execute("create database PSDataBase;")
        # print("Database Created")
        dbCursor.close()
        
    createTable("users", "emailID varchar(40), pass varchar(40)")
    createTable("plantStationData", "location varchar(150), latitudeL double, longitudeL double, sourceType varchar(20), nearestSubstation varchar(150), latitudeSS double, longitudeSS double, plantOwner varchar(150), plantCapacity double")
    plantDataList = readFile("powerSources")
    addPlantValues(plantDataList)
    createTable("demandData", "location varchar(150), latitude double, longitude double, powerDemand double, growthRate float")
    demandDataList = readFile("demand")
    addDemandValues(demandDataList)
    return


def get_columns_query(tablename: str, columns: list, constraint: tuple=None, limit: int|str=None, order_by_col: list[str,]=None, order_by_asc: list[bool,]=None) -> str:
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

    
def get_columns(tablename: str, columns: list, constraint: tuple=None, limit: int|str=None, order_by_col: list[str,]=None, order_by_asc: list[bool,]=None) -> str:
    query = get_columns_query(tablename=tablename, columns=columns, constraint=constraint, limit=limit, order_by_col=order_by_col, order_by_asc=order_by_asc)
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return data


def createTable(tableName, columns):
    tableCursor = connection.cursor()
    tableError = None
    tableCursor.execute("use psdatabase;")
    try:
        tableCursor.execute(f"select * from {tableName};")
        garbage = tableCursor.fetchall()
    except Exception as exp:
        tableError = str(exp)
    if tableError == f"1146 (42S02): Table 'psdatabase.{tableName.lower()}' doesn't exist":
        tableCursor.execute(f"create table {tableName}({columns});")
        # print(tableCursor.fetchall())
        connection.commit()
        # print(f"{tableName} table created")
    tableCursor.close()
    return


def emailClient(receiver):
    server = smtplib.SMTP(host="smtp.gmail.com", port=587)
    server.ehlo()
    server.starttls()
    sender = "sujay.karpur2@gmail.com"
    passwd = "ztspqpohmfqthzhg"
    # receiver = "bobisasecretagent@gmail.com"

    msg = EmailMessage()
    msg.set_content(f"Your Sustainable Energy Interface OTP is {random.randint(1000,9999)}")
    msg['Subject'] = "SEI One-Time Password"
    msg['From'] = "sujay.karpur2@gmail.com"
    msg['To'] = receiver

    server.login(sender, passwd)
    server.send_message(msg)
    server.close()
    return


def readFile(fileName):
    dataList = []
    textFile = open(f"{fileName}.txt", 'r')
    fileList = textFile.readlines()
    for i in fileList:
        tempList = []
        for j in i.split('|'):
            tempList.append(j.strip())
        dataList.append(tempList)
    textFile.close()
    return dataList


def addPlantValues(dataList):
    inputCursor = connection.cursor()
    inputCursor.execute("delete from plantStationData;")
    connection.commit()
    for i in range(len(dataList)):
        if dataList[i][7] == "None":
            dataList[i].append("NULL")
        tempList = dataList[i]
        inputCursor.execute(f"insert into plantStationData values(\"{tempList[0]}\", {tempList[1]}, {tempList[2]}, \"{tempList[3]}\", \"{tempList[4]}\", {tempList[5]}, {tempList[6]}, \"{tempList[7]}\", {tempList[8]});")
        connection.commit()
    inputCursor.close()
    # print("plantStationData has been updated")
    return


def addDemandValues(dataList):
    inputCursor = connection.cursor()
    inputCursor.execute("delete from demandData;")
    connection.commit()
    for i in dataList:
        inputCursor.execute(f"insert into demandData values(\"{i[0]}\", {i[1]}, {i[2]}, {i[3]}, {i[4]})")
        connection.commit()
    inputCursor.close()
    # print("demandData has been updated")
    return
    


def findDistance(x1, y1, x2, y2):
    distance = (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5
    return distance


def closestSubstation(x, y):
    distanceSS = []
    listSS = []
    closestCursor = connection.cursor()
    closestCursor.execute("select nearestSubstation, latitudeSS, longitudeSS from plantStationData;")
    data = closestCursor.fetchall()
    for substationInfo in data:
        distanceSS.append(findDistance(x, y, substationInfo[1], substationInfo[2]))
        listSS.append(substationInfo[0])
    return listSS[distanceSS.index(min(distanceSS))]


def demandIncrease(demandLocation):
    extractionCursor = connection.cursor()
    extractionCursor.execute(f"select location, powerDemand, growthRate from demandData where location like \"{demandLocation}\";")
    extracted = extractionCursor.fetchall()[0]
    currentDemand = extracted[1]
    rateOfIncrease = extracted[2]
    projectedDemand = [currentDemand]
    for i in range(1, 5):
        projectedDemand.append(projectedDemand[i - 1] * (1 + (rateOfIncrease/100)))
    return projectedDemand


def graphing(demandLoc):
    yValues = demandIncrease(demandLoc)
    xpoints = np.array([i for i in range(2023, 2028)])
    ypoints = np.array([i for i in yValues])
    plt.plot(xpoints, ypoints)
    plt.ylabel("Energy consumption in GWh per year")
    plt.xlabel("Year")
    plt.title("Projection for increase in power demand using past growth")
    plt.show()
    return


if __name__ == "__main__":
    init_db()
