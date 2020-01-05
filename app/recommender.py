import pandas as pd
import numpy as np
from typing import List
from .models import LeadRepository, Lead


class Recommender:
    def __init__(self, lead_repository: LeadRepository, user_item_matrix_file: str):
        self.lead_repository = lead_repository
        self.user_item_matrix_file = user_item_matrix_file

    def read_leads_user_item_matrix(self, chunk_size: int = 500):
        return pd.read_csv(self.user_item_matrix_file, chunksize=chunk_size).set_index('user_id')

    def find_similar_users(self, user_id: str, user_item_matrix: pd.DataFrame) -> np.ndarray:
        """
        Creates an array of similar users based on leads generated on the same courses

        :param user_id: User id for which we want to find similar users
        :param user_item_matrix: Leads user-item matrix

        :return: Array of similar users sorted by similarity
        """

        user = np.array(user_item_matrix.loc[user_id])

        similarities = dict()

        for another_user_id, courses in user_item_matrix.iterrows():
            if user_id == another_user_id:
                continue

            similarities[another_user_id] = np.dot(user, np.array(courses))

        sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)

        return np.array([id for (id, similarity) in sorted_similarities])

    def get_user_leads(self, user_id: str) -> List[Lead]:
        """
        Returns a list of courses to which the user has generated lead

        :param user_id: User id for which we want to find generated leads

        :return list: List of courses to which the user has generated lead
        """

        return self.lead_repository.find_by_user(user_id)

    def leads_based_recommendations(self, course_id: str, max_recs: int = 10):
        """
        Returns an array of recommended courses for a user based on generated leads

        :param course_id: User id for which we want to make the recommendations
        :param max_recs: Maximum number of recommendations

        :return numpy.array: Array of courses recommended based on generated leads
        """
        similar_users = np.array([])

        leads_user_item_matrix = self.read_leads_user_item_matrix()

        for df in leads_user_item_matrix:
            similar_users = np.concatenate([similar_users, df[df.loc[:, course_id] == 1].index], axis=0)

        user_courses = np.array(course_id)

        recs = np.array([])

        for user in similar_users:
            neighbs_leads = self.get_user_leads(user)

            new_recs = np.setdiff1d(neighbs_leads, user_courses, assume_unique=True)
            recs = np.unique(np.concatenate([new_recs, recs], axis=0))

            if len(recs) > max_recs:
                break

        return recs[:max_recs]
