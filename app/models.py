from . import db
import math
from typing import List


class Paginator:
    def __init__(self, page, items_per_page):
        self.current_page = page
        self.items_per_page = items_per_page
        self.offset = (page - 1) * items_per_page
        self.row_count = 0
        self.page_count = 0

    def set_counts(self, sql: str):
        result = db.engine.execute(sql)

        self.row_count = result.rowcount
        self.page_count = int(math.ceil(self.row_count / self.items_per_page))


class Repository:
    def __init__(self, paginator: Paginator = None):
        self.paginator = paginator

    def paginated_query(self, query: str):
        if self.paginator:
            self.paginator.set_counts(query)
            query = '{} limit {}, {}'.format(query, self.paginator.offset, self.paginator.items_per_page)

        return query


class Course:
    def __init__(self, id: str, title: str, category: str, center: str):
        self.id = id
        self.title = title
        self.description = None
        self.category = category
        self.center = center
        self.number_of_reviews = None
        self.avg_rating = None
        self.number_of_leads = None

    def set_number_of_leads(self, number_of_leads: int):
        self.number_of_leads = number_of_leads

    def set_number_of_reviews(self, number_of_reviews: int):
        self.number_of_reviews = number_of_reviews

    def set_avg_rating(self, avg_rating: float):
        self.avg_rating = avg_rating

    def set_description(self, description: str):
        self.description = description


class CourseRepository(Repository):
    def find_sorted_by_leads(self, category: int = None):
        courses = []
        query = 'SELECT c.id, c.title, c.description, cat.name AS category, c.center, ' \
                'count(cl.user_id) AS num_request ' \
                'FROM courses c JOIN clean_leads cl ON c.id = cl.course_id ' \
                'JOIN categories cat ON c.category_id = cat.id ' \

        if category:
            query = '{} WHERE c.category_id = {}'.format(query, category)

        query = '{} {} {}'.format(query,
                                  'GROUP BY c.id, c.title, c.description, c.category_id',
                                  'ORDER BY num_request DESC')

        result = self.__execute_query__(query)

        for row in result:
            course = Course(row['id'], row['title'], row['category'], row['center'])
            course.set_number_of_leads(row['num_request'])
            if row['description']:
                course.set_description(row['description'])

            courses.append(course)

        return courses

    def find_sorted_by_rating(self, category: int = None):
        courses = []
        query = 'SELECT c.id, c.title, c.description, cat.name AS category, c.center, cr.weighted_rating_average, ' \
                'cr.num_reviews' \
                ' FROM courses c JOIN clean_reviews cr ON c.id = cr.course_id ' \
                ' JOIN categories cat ON cat.id = c.category_id '

        if category:
            query = '{} WHERE c.category_id = {}'.format(query, category)

        query = '{} {}'.format(query,
                               'GROUP BY c.id ORDER BY cr.weighted_rating_average DESC')

        result = self.__execute_query__(query)

        for row in result:
            course = Course(row['id'], row['title'], row['category'], row['center'])
            if row['description']:
                course.set_description(row['description'])

            course.set_avg_rating(row['weighted_rating_average'])
            course.set_number_of_reviews(row['num_reviews'])

            courses.append(course)

        return courses

    def __execute_query__(self, query: str):
        if self.paginator:
            self.paginator.set_counts(query)
            query = '{} limit {}, {}'.format(query, self.paginator.offset, self.paginator.items_per_page)

        return db.engine.execute(query)


class Category:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class CategoryRepository(Repository):
    def find_all(self) -> List[Category]:
        categories = []

        query = self.paginated_query('SELECT id, name FROM categories ORDER BY name')

        result = db.engine.execute(query)
        for row in result:
            categories.append(Category(row['id'], row['name']))

        return categories
