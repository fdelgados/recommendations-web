from datetime import datetime
from flask import render_template, request, session, redirect, url_for
from . import main
from . use_cases import RetrieveSortedCourses, RetrieveSortedCoursesCommand
from . use_cases import RetrieveCourseData, RetrieveCourseDataCommand


@main.route('/', methods=['GET'])
def index():

    command = RetrieveSortedCoursesCommand(page=request.args.get('page', default=1),
                                           sort_by=request.args.get('sort_by', default='leads'),
                                           category=request.args.get('category'))

    response = RetrieveSortedCourses.execute(command)

    return render_template('home.html', response=response)


@main.route('/course/<int:course_id>', methods=['GET'])
def course(course_id):
    command = RetrieveCourseDataCommand(course_id)

    course = RetrieveCourseData.execute(command)

    return render_template('course.html', course=course)
