import pymongo

print("something")

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]

print("db names: " + myclient.list_database_names())

dblist = myclient.list_database_names()
if "mydatabase" in dblist:
    print("The database exists.")

print("done...")
