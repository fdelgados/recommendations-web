from ..models import CourseRepository, CategoryRepository, Paginator
from ..models import Lead, LeadRepository, Recommendations
from typing import Dict
import hashlib


class RetrieveCourseCatalogCommand:
    def __init__(self, page: int, sort_by: str, category: int):
        self.page = int(page)
        self.sort_by = sort_by
        self.category = category


class RetrieveCourseCatalog:
    @staticmethod
    def execute(command: RetrieveCourseCatalogCommand) -> Dict:
        courses = []
        page = command.page
        sort_by = command.sort_by
        category_id = None

        if command.category is not None:
            category_id = int(command.category)

        courses_per_page = 20
        paginator = Paginator(page, items_per_page=courses_per_page)
        course_repository = CourseRepository(paginator)

        if sort_by == 'leads':
            courses = course_repository.find_sorted_by_leads(category_id)
        if sort_by == 'rating':
            courses = course_repository.find_sorted_by_rating(category_id)

        prev_page = page - 1 if page >= 1 else None
        next_page = page + 1 if page < paginator.page_count else None

        category_repository = CategoryRepository()

        categories = category_repository.find_all(10)

        category_name = None
        if category_id is not None:
            for _, category in categories.items():
                if category.id == category_id:
                    category_name = category.name
                    break

        return {'courses': courses,
                'categories': categories,
                'category_id': category_id,
                'category_name': category_name,
                'current_page': page,
                'total_pages': paginator.page_count,
                'next_page': next_page,
                'prev_page': prev_page,
                'sort_by': sort_by}


class RetrieveCourseDataCommand:
    def __init__(self, course_id: int):
        self.course_id = course_id


class RetrieveCourseData:
    @staticmethod
    def execute(command: RetrieveCourseDataCommand):
        course_repository = CourseRepository()

        course = course_repository.find(command.course_id)
        recommendations = Recommendations()
        recommendations.make_recommendations_by_course(course.id).make_rank_recommendations(course.category_id,
                                                                                            course.id)

        return {'course': course,
                'recommendations': recommendations}


class PlaceAnInfoRequestCommand:
    def __init__(self, course_id: str, email: str):
        self.course_id = course_id
        self.email = email


class PlaceAnInfoRequest:
    @staticmethod
    def execute(command: PlaceAnInfoRequestCommand):
        course_repository = CourseRepository()
        lead_repository = LeadRepository()

        course = course_repository.find(command.course_id)
        # Hashing the user email
        user_id = hashlib.md5(command.email.encode()).hexdigest()
        lead = Lead(user_id, course)

        success = True
        recommendations = Recommendations()
        try:
            lead_repository.save(lead)
            recommendations.make_recommendations_by_course(course.id)
        except Exception:
            success = False

        return {
            'success': success,
            'user_id': user_id,
            'course_id': course.id,
            'course_title': course.title,
            'recommendations': recommendations
        }


class RetrieveHomeRecommendationsCommand:
    def __init__(self, user_id: str = None):
        self.user_id = user_id


class RetrieveHomeRecommendations:
    @staticmethod
    def execute(command: RetrieveHomeRecommendationsCommand) -> Dict:
        recommendations = Recommendations()
        recommendations.make_rank_recommendations().make_recommendations_by_user(command.user_id)

        return {'recommendations': recommendations}


class RetrieveCategories:
    @staticmethod
    def execute() -> Dict:
        category_repository = CategoryRepository()

        return {'categories': category_repository.find_all()}
