from pymongo import MongoClient
from pymongo.server_api import ServerApi
from mongo_config import MONGO_CLUSTER

class MongoDBService:
    def __init__(self, db_name):
        self.client = MongoClient(MONGO_CLUSTER, server_api=ServerApi('1'))
        self.db = self.client[db_name]
        self.collection = self.db['user_summaries']

    def save_summary(self, user_id, summary):
        """
        Save user's 'wrapped' or summary to the database
        """
        self.collection.update_one(
            {'user_id': user_id},
            {'$push': {'summary_list': summary}},
            upsert=True  # create document if it doesn't exist
        )

    
    def get_summaries(self, user_id):
        user_data = self.collection.find_one({'user_id' : user_id})
        if user_data:
            return user_data.get('summary_list', [])
        return []
    

    def get_summary_by_index(self, user_id, index):
        """
        Get a single summary from the summary list at the specified index.
        """
        # find the document for the user
        summary_list = self.get_summaries(user_id)
        summary_len = len(summary_list)

        # Check if the user document exists and if the index is valid
        if summary_list and index >= 0 and index < summary_len:
            return summary_list[index]
        else:
            return {'error' : f'Index out {index} of range for summary list of length {summary_len}'}

    

    def delete_all_summaries(self, user_id):
        self.collection.update_one(
            {'user_id': user_id},
            {'$set': {'summary_list': []}}
        )
        return self.get_summaries(user_id)
    

    def delete_summary_by_index(self, user_id, index):
        # Execute the update operation
        summary_len = len(self.get_summaries(user_id))
        if index >= summary_len or index < 0:
            return {'error' : f'Index out {index} of range for summary list of length {summary_len}'}

        self.collection.update_one(
            {'user_id': user_id},
            {'$unset': {f'summary_list.{index}': ''}}
        )

        # $pull operation to remove the nulls from list
        self.collection.update_one(
            {'user_id': user_id},
            {'$pull': {'summary_list': None}}
        )

        # return updated list 
        return self.get_summaries(user_id)