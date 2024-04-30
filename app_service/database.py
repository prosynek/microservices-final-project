from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi
from mongo_config import MONGO_CLUSTER

class MongoDBService:
    def __init__(self, db_name):
        self.client = MongoClient(MONGO_CLUSTER, server_api=ServerApi('1'))
        self.db = self.client[db_name]
        self.collection = self.db['user_summaries']

    def save_summary(self, user_id, summary):
        """
        Save user's wrap/summary to the database.

        :param user_id: spotify user_id (also the user_id in the db)
        :param summary: summary ('wrap') to save to the db
        """
        try:
            self.collection.update_one(
                {'user_id': user_id},
                {'$push': {'summary_list': summary}},
                upsert=True  # create document if it doesn't exist
            )
        except PyMongoError as e:
            return {'error': str(e)}


    def get_summaries(self, user_id):
        """
        Gets all of the saved summaries for a user.

        :param user_id: spotify user_id to retrieve the summaries for
        :return: array of the user's stored summaries
        """
        try:
            user_data = self.collection.find_one({'user_id': user_id})
            if user_data:
                return user_data.get('summary_list', [])
            return []
        except PyMongoError as e:
            return {'error': str(e)}


    def get_summary_by_index(self, user_id, index):
        """
        Gets a saved user summary by index.

        :param user_id: spotify user_id to retrieve the summaries for
        :param index: index of the summary to retrieve
        :return: summary at the specified index
        """
        try:
            summary_list = self.get_summaries(user_id)
            summary_len = len(summary_list)
            if summary_list and 0 <= index < summary_len:
                return summary_list[index]
            else:
                return {'error': f'Index out {index} of range for summary list of length {summary_len}'}
        except PyMongoError as e:
            return {'error': str(e)}


    def delete_all_summaries(self, user_id):
        """
        Deletes all summaries for a user in the MongoDB database.

        :param user_id: spotify user_id to delete the summaries for
        :return: users summaries, should be empty
        """
        try:
            self.collection.update_one(
                {'user_id': user_id},
                {'$set': {'summary_list': []}}
            )
            return self.get_summaries(user_id)
        except PyMongoError as e:
            return {'error': str(e)}


    def delete_summary_by_index(self, user_id, index):
        """
        Deletes a saved user summary by index.

        :param user_id: spotify user_id to retrieve the summaries for
        :param index: index of the summary to delete
        :return: updated list of user's summaries
        """
        try:
            summary_len = len(self.get_summaries(user_id))
            if not (0 <= index < summary_len):
                return {'error': f'Index out {index} of range for summary list of length {summary_len}'}
            self.collection.update_one(
                {'user_id': user_id},
                {'$unset': {f'summary_list.{index}': ''}}
            )
            self.collection.update_one(
                {'user_id': user_id},
                {'$pull': {'summary_list': None}}
            )
            return self.get_summaries(user_id)
        except PyMongoError as e:
            return {'error': str(e)}
