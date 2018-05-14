from bson import ObjectId
from pymongo import MongoClient
from simplejson import dumps

from rasa_nlu.conversation_module.database_connector import DatabaseConnector


class MongoConnector(DatabaseConnector):
    def __init__(self, url, db_name):
        super().__init__(url)
        self.db_name = db_name
        self.database = self.connect()

    def connect(self):
        self.database = MongoClient(self.url)[self.db_name]
        return self.database

    def insert_record(self, record, collection):
        conv_id = self.database.get_collection(collection).insert(record)
        return conv_id

    @staticmethod
    def view_collection(collection):
        return dumps(list(collection.find()))

    def update_record(self, _id, record, collection):
        # for update operators https: // docs.mongodb.com / manual / reference / operator / update /
        self.database.get_collection(collection).update_one({"_id": ObjectId(_id)}, {"$set": record})

    def delete_record(self, _id, collection):
        self.database.get_collection(collection).delete_one({"_id": _id})

    def get_record_by_custom_filter(self, filter_name, filter_value, collection):
        return self.database.get_collection(collection).find_one({filter_name: filter_value})

    def get_record(self, _id, collection):
        return self.database.get_collection(collection).find_one({"_id": ObjectId(_id)})

