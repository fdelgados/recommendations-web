from datetime import datetime
from flask import render_template, request, session, redirect, url_for
from . import main
from . use_cases import RetrieveSortedCourses, RetrieveSortedCoursesCommand


@main.route('/', methods=['GET'])
def index():

    command = RetrieveSortedCoursesCommand(page=request.args.get('page', default=1),
                                           sort_by=request.args.get('sort_by', default='leads'),
                                           category=request.args.get('category'))

    response = RetrieveSortedCourses.execute(command)

    return render_template(
        'home.html',
        response=response
    )
