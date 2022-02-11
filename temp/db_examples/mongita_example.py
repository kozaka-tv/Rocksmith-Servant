import mongita
from mongita import MongitaClientDisk

client = MongitaClientDisk()
hello_world_db = client.hello_world_db
mongoose_types = hello_world_db.mongoose_types
mongoose_types.insert_many([{'name': 'Meercat'}])

# mongoose_types.insert_many([{'name': 'Meercat', 'not_into', 'Snakes'}, {'name': 'Yellow mongoose': 'eats': 'Termites'}])

mongoose_types.update_one({'name': 'Meercat'}, {'$set': {"weight": 2}})

print(mongita.Database.list_collections())

# InsertResult()
print(mongoose_types.count_documents({}))
# 2

# mongoose_types.find({'weight': {'$gt': 1})


# mongoose_types.update_one({'name': 'Meercat'}, {'$set': {"weight": 2}})
# UpdateResult()
# >>> mongoose_types.find({'weight': {'$gt': 1})
# Cursor()
# >>> list(coll.find({'weight': {'$gt': 1}))
# [{'_id': 'a1b2c3d4e5f6', 'weight': 2, 'name': 'Meercat'}]
# >>> coll.delete_one({'name': 'Meercat'})
# DropResult()
