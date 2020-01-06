from flask import render_template, request, abort, session, redirect, url_for
from . import main
from .use_cases import RetrieveCourseCatalog, RetrieveCourseCatalogCommand
from .use_cases import RetrieveCourseData, RetrieveCourseDataCommand
from .use_cases import PlaceAnInfoRequest, PlaceAnInfoRequestCommand
from .use_cases import RetrieveHomeRecommendations, RetrieveHomeRecommendationsCommand
from .use_cases import RetrieveCategories

user_id = '001d7fed950bc1f5834b2d4af75b1879'


@main.route('/', methods=['GET'])
def home():
    command = RetrieveHomeRecommendationsCommand(user_id=user_id)
    response = RetrieveHomeRecommendations.execute(command)

    return render_template('home.html',
                           recommendations=response['recommendations'],
                           categories=response['categories'])


@main.route('/categories', methods=['GET'])
def categories():
    response = RetrieveCategories.execute()

    return render_template('categories.html', response=response)


@main.route('/catalog', methods=['GET'])
def catalog():
    command = RetrieveCourseCatalogCommand(page=request.args.get('page', default=1),
                                           sort_by=request.args.get('sort_by', default='leads'),
                                           category=request.args.get('category'))

    response = RetrieveCourseCatalog.execute(command)

    return render_template('course-catalog.html', response=response)


@main.route('/course/<int:course_id>', methods=['GET'])
def course(course_id):
    command = RetrieveCourseDataCommand(course_id)

    response = RetrieveCourseData.execute(command)

    return render_template('course.html',
                           course=response['course'],
                           recommendations=response['recommendations'])


@main.route('/request-information', methods=['POST'])
def request_information():
    email = request.form.get('email')
    course_id = request.form.get('courseId')

    command = PlaceAnInfoRequestCommand(course_id, email)
    response = PlaceAnInfoRequest.execute(command)

    if not response['success']:
        return abort(500)

    return render_template('request-information.html', response=response)
