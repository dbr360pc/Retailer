from pymongo import MongoClient

class MongoLib:

    def __init__(self,db_name='ProductDB'):

        self.client = MongoClient('mongodb://RAY_USER:dbr360pc%401998@31.97.230.82:27017/?authMechanism=SCRAM-SHA-1&authSource=admin')

        self.db = self.client[db_name]

        self.db_name = db_name

    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def create_database(self, db_name):
        return self.client[db_name]
    

    def check_and_create_entry(self, collection_name, query,data):
        collection = self.get_collection(collection_name)
        existing_entry = collection.find_one(query)
        if existing_entry:
            print("Entry already exists:", existing_entry)
            return existing_entry
        else:
            result = collection.insert_one(data)
            print("Created new entry:", result.inserted_id)
            return data
