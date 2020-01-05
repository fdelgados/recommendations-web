from . import db
import numpy as np
import math
import datetime
from typing import List, Dict
from sqlalchemy.sql import text


def find_neighbours(user_id: str):
    query = '''SELECT another_user_id
                FROM users_similarities 
                WHERE a_user_id = :user_id
                ORDER BY similarity DESC'''

    result = db.engine.execute(text(query), user_id=user_id)

    return result.fetchall()


class Paginator:
    def __init__(self, page, items_per_page):
        self.current_page = page
        self.items_per_page = items_per_page
        self.offset = (page - 1) * items_per_page
        self.row_count = 0
        self.page_count = 0

    def set_counts(self, sql: str, **params):
        result = db.engine.execute(text(sql), **params)

        self.row_count = result.rowcount
        self.page_count = int(math.ceil(self.row_count / self.items_per_page))


class Repository:
    def __init__(self, paginator: Paginator = None):
        self.paginator = paginator

    def paginated_query(self, query: str, **params):
        if self.paginator:
            self.paginator.set_counts(query, **params)
            query = '{} limit {}, {}'.format(query, self.paginator.offset, self.paginator.items_per_page)

        return query

    def execute_query(self, query: str, **kwargs) -> 'ResultProxy':
        if 'limit' in kwargs and kwargs['limit']:
            query = '{} LIMIT :limit'.format(query)
        else:
            query = self.paginated_query(query, **kwargs)

        return db.engine.execute(text(query), **kwargs)


class Category:
    def __init__(self, id: int, name: str, num_courses: int = None):
        self.id = id
        self.name = name
        self.num_courses = num_courses

    def set_num_courses(self, num_courses: int):
        self.num_courses = num_courses


class CategoryRepository(Repository):
    def find_all(self, max_rows: int = None) -> Dict[int, Category]:
        categories = {}

        query = '''SELECT cat.id, cat.name, count(c.category_id) AS num_courses
                     FROM categories cat
                     JOIN courses c ON cat.id = c.category_id
                     GROUP BY cat.id, cat.name
                     ORDER BY num_courses DESC'''

        result = self.execute_query(query, limit=max_rows)

        for row in result:
            categories[row['id']] = Category(row['id'], row['name'], row['num_courses'])

        return categories

    def find_popular(self, max_rows: int = None) -> Dict[int, Category]:
        categories = {}

        query = '''SELECT cat.id, cat.name, SUM(c.number_of_leads) AS number_of_leads
                     FROM categories cat
                     JOIN courses c ON cat.id = c.category_id
                     GROUP BY cat.id, cat.name
                     ORDER BY number_of_leads DESC'''

        result = self.execute_query(query, limit=max_rows)

        for row in result:
            categories[row['id']] = Category(row['id'], row['name'])

        return categories


class Course:
    def __init__(self, id: str, title: str, category: Category, center: str):
        self.id = id
        self.title = title
        self.description = None
        self.category = category
        self.center = center
        self.number_of_reviews = None
        self.weighted_rating = None
        self.number_of_leads = None

    def set_number_of_leads(self, number_of_leads: int):
        self.number_of_leads = number_of_leads

    def set_number_of_reviews(self, number_of_reviews: int):
        self.number_of_reviews = number_of_reviews

    def set_weighted_rating(self, avg_rating: float):
        self.weighted_rating = avg_rating

    def set_description(self, description: str):
        self.description = description

    @property
    def category_name(self) -> str:
        return self.category.name

    @property
    def category_id(self) -> int:
        return self.category.id


class CourseRepository(Repository):
    def find_sorted_by_leads(self, category: int = None,
                             max_rows: int = None,
                             exclude: str = None,
                             min_number_of_leads: int = 1) -> Dict[str, Course]:
        query = '''SELECT c.id, c.title, c.description, c.category_id, cat.name AS category_name, c.center,
                        c.number_of_leads, c.num_reviews, ROUND(c.weighted_rating, 2) AS weighted_rating
                   FROM courses c 
                   JOIN categories cat ON c.category_id = cat.id
                   WHERE c.number_of_leads >= :min_number_of_leads'''

        if category:
            query = '{} AND c.category_id = :category_id'.format(query)

        if exclude:
            query = '{} AND c.id <> :course_id'.format(query)

        query = '{} {}'.format(query, 'ORDER BY number_of_leads DESC, weighted_rating DESC, num_reviews DESC')

        return self.populate(query, limit=max_rows,
                             category_id=category,
                             course_id=exclude,
                             min_number_of_leads=min_number_of_leads)

    def find_sorted_by_rating(self, category: int = None,
                              max_rows: int = None,
                              exclude: str = None,
                              min_weighted_rating: float = 5.0) -> Dict[str, Course]:
        query = '''SELECT c.id, c.title, c.description, c.category_id, cat.name AS category_name, c.center,
                        c.number_of_leads, c.num_reviews, ROUND(c.weighted_rating, 2) AS weighted_rating
                   FROM courses c
                   JOIN categories cat ON c.category_id = cat.id
                   WHERE c.weighted_rating >= :min_weighted_rating'''

        if category:
            query = '{} AND c.category_id = :category_id'.format(query)

        if exclude:
            query = '{} AND c.id <> :course_id'.format(query)

        query = '{} {}'.format(query, 'ORDER BY weighted_rating DESC, num_reviews DESC, number_of_leads DESC')

        return self.populate(query, limit=max_rows,
                             course_id=exclude,
                             category_id=category,
                             min_weighted_rating=min_weighted_rating)

    def find_similar_by_leads(self, course_id: str, max_rows: int = None) -> Dict[str, Course]:
        query = '''SELECT r.recommended as id, c.title, c.description, c.category_id, cat.name AS category_name,
                    c.center, c.number_of_leads, c.num_reviews, ROUND(c.weighted_rating, 2) AS weighted_rating
                FROM recommended_courses_by_leads r
                JOIN courses c on r.recommended = c.id
                JOIN categories cat on cat.id = c.category_id
                WHERE r.course = :course_id
                ORDER BY number_of_leads DESC, weighted_rating DESC, num_reviews DESC'''

        return self.populate(query, course_id=course_id, limit=max_rows)

    def find_similar_by_content(self, course_id: str, max_rows: int = None) -> Dict[str, Course]:
        query = '''SELECT cs.another_course_id as id, c.title, c.description, c.category_id, cat.name AS category_name,
                    c.center, c.number_of_leads, c.num_reviews, ROUND(c.weighted_rating, 2) AS weighted_rating 
                FROM courses_similarities cs
                JOIN courses c on cs.another_course_id = c.id
                JOIN categories cat on cat.id = c.category_id
                WHERE cs.a_course_id = :course_id
                ORDER BY cs.similarity DESC'''

        return self.populate(query, course_id=course_id, limit=max_rows)

    def find_by_user_leads(self, user_id: str) -> Dict[str, Course]:
        query = '''SELECT c.id, c.title, c.description, c.center, c.category_id, cat.name as category_name,
                   c.number_of_leads, c.num_reviews, ROUND(c.weighted_rating, 2) AS weighted_rating
                FROM clean_leads l
                JOIN courses c ON l.course_id = c.id
                JOIN categories cat ON c.category_id = cat.id
                WHERE user_id = :user_id'''

        return self.populate(query, user_id=user_id)

    def find(self, course_id: str) -> Course:
        query = '''SELECT c.id, title, description, center, category_id, c.center,
                cat.name AS category_name,  c.number_of_leads,
                c.weighted_rating, c.num_reviews
                FROM courses c JOIN categories cat ON c.category_id = cat.id
                WHERE c.id = :course_id
                GROUP BY c.id'''

        courses = self.populate(query, course_id=course_id)

        return list(courses.values())[0]

    def populate(self, query: str, **kwargs) -> Dict[str, Course]:
        courses = {}
        result = self.execute_query(query, **kwargs)

        for row in result:
            course = Course(row['id'],
                            row['title'],
                            Category(row['category_id'], row['category_name']),
                            row['center'])

            if row['description']:
                course.set_description(row['description'])

            course.set_weighted_rating(row['weighted_rating'])
            course.set_number_of_reviews(row['num_reviews'])
            course.set_number_of_leads(row['number_of_leads'])

            courses[course.id] = course

        return courses


class Lead:
    def __init__(self, user_id: str, course: Course, created_on: str = None):
        self.user_id = user_id
        self.course = course
        self.created_on = datetime.datetime.now() if created_on is None else created_on

    @property
    def course_id(self):
        return self.course.id


class LeadRepository(Repository):
    def save(self, lead: Lead):
        insert_sql = '''INSERT INTO leads (user_id, course_id, course_title, 
                        course_description, center, course_category, created_on)
                        VALUES (:user_id, :course_id, :course_title, :course_description,
                        :center, :course_category, :created_on)'''

        db.engine.execute(text(insert_sql),
                          user_id=lead.user_id,
                          course_id=lead.course.id,
                          course_title=lead.course.title,
                          course_description=lead.course.description,
                          center=lead.course.center,
                          course_category=lead.course.category_name,
                          created_on=lead.created_on)


class Recommendations:
    def __init__(self):
        self.by_leads = {}
        self.by_content = {}
        self.by_rating = {}
        self.by_number_of_leads = {}
        self.by_user = {}
        self.course_repository = CourseRepository()

    def make_recommendations_by_course(self, course_id, max_recommendations: int = 10) -> 'Recommendations':
        self.by_leads = self.course_repository.find_similar_by_leads(course_id, max_recommendations)
        self.by_content = self.course_repository.find_similar_by_content(course_id, max_recommendations)

        return self

    def make_rank_recommendations(self, category_id: int = None, course_id: str = None,
                                  max_recommendations: int = 10) -> 'Recommendations':
        self.by_rating = self.course_repository.find_sorted_by_rating(category=category_id,
                                                                      max_rows=max_recommendations,
                                                                      exclude=course_id)
        self.by_number_of_leads = self.course_repository.find_sorted_by_leads(category=category_id,
                                                                              max_rows=max_recommendations,
                                                                              exclude=course_id)

        return self

    def make_recommendations_by_user(self, user_id: str = None, max_recommendations: int = 10) -> 'Recommendations':
        if not user_id:
            return self

        user_courses = self.course_repository.find_by_user_leads(user_id)
        user_courses_ids = np.array(list(user_courses.keys()))

        if len(user_courses_ids) == 0:
            return self

        rec_courses_ids = np.array([])
        neighbours_courses = {}

        similar_users = find_neighbours(user_id)
        for user in similar_users:
            neighbour_courses = self.course_repository.find_by_user_leads(user['another_user_id'])
            neighbours_courses.update(neighbour_courses)

            new_recs = np.setdiff1d(np.array(list(neighbour_courses.keys())), user_courses_ids, assume_unique=True)
            rec_courses_ids = np.unique(np.concatenate([new_recs, rec_courses_ids], axis=0))

            if len(rec_courses_ids) > max_recommendations:
                break

        if len(rec_courses_ids) == 0:
            return self

        self.by_user = {course_id: course for (course_id, course) in neighbours_courses.items()
                        if course_id in rec_courses_ids}

        return self
