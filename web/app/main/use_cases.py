from ..models import CourseRepository, CategoryRepository, Paginator
from typing import Dict


class RetrieveSortedCoursesCommand:
    def __init__(self, page: int, sort_by: str, category: int):
        self.page = int(page)
        self.sort_by = sort_by
        self.category = category


class RetrieveSortedCourses:
    @staticmethod
    def execute(command: RetrieveSortedCoursesCommand) -> Dict:
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

        categories = category_repository.find_all()

        category_name = None
        if category_id is not None:
            for category in categories:
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
