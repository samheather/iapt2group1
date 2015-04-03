# -*- coding: utf-8 -*-

import datetime

#from tx import *

def index():
    # Set the page title
    response.title = T('Home | TransXribe')

    # Get the five oldest projects from the database
    projects = db(db.ProjectsForTranscription.id>0).select(orderby=db.ProjectsForTranscription.id, limitby=(0, 5))
    return dict(projects=projects)

def browse():
    # Set the page title
    response.title = T('Browse Projects | TransXribe')

    # Get all projects from the database
    projects = db(db.ProjectsForTranscription.id>0).select(orderby=db.ProjectsForTranscription.id)
    return dict(projects=projects)

def search():
    # Set the page title
    response.title = T('Search | TransXribe')

    projects = dict()
    term = request.vars['q'].strip()

    if term != '':
        projects = db(((db.ProjectsForTranscription.title.like('%'+term+'%'))
                     | (db.ProjectsForTranscription.requestDescription.like('%'+term+'%')))
                     & (db.ProjectsForTranscription.projectOpen == 'T'))\
            .select()

        # for project in projects:
        #     project['image'] = db(db.Image.project_id == project.id).select().first()['image']

    return dict(projects=projects, term=term)

def login():
    redirect(URL('user','login',args='invalid'))


@auth.requires_login()
def dashboard():
    # Set the page title
    response.title = T('Dashboard | TransXribe')

    if len(request.args) ==0:
        justAddedProject_id=0
    else:
        justAddedProject_id = int(request.args(0))

    user = db((db.auth_user.id == auth.user_id)).select()[0]
    projects = user.projects()
#     for project in projects:
#         project['image'] = db(db.Image.project_id == project.Project.id).select().first()['image']
    return dict(projects=projects,justAddedProject_id=justAddedProject_id)


# def auth_user():
# 	auth.settings.formstyle = 'bootstrap3_stacked'
# 
# 	# Shipping and billing addresses are edited elsewhere in the application.  We never
# 	# show ID since it is a unique primary key.  
# 	
# 	# Originally it was assumed Birthdate would never change.  This is because a user may
# 	# try and make their birthdate earlier in the past after realising that they don't
# 	# qualify for some parts of the application (e.g. because they are under the age of
# 	# 18).  This was achieved by simply setting the Birthdate attribute readable and 
# 	# writeable to False, as has been done below with ID.
# 	# The decision was not taken, since the assessment document says that a user should be
# 	# able to chance all information stored on them.
# 	
# 	db.auth_user.shippingAddress.readable = db.auth_user.shippingAddress.writable = False
# 	db.auth_user.paymentMethod.readable = db.auth_user.paymentMethod.writable = False
# 	db.auth_user.id.readable = db.auth_user.id.writable = False
# 
# 	# Set redirect URL for after logging-in to the page that the user was on before (if
# 	# this variable was passed in).	
# 	auth.settings.login_next = request.vars['_next']
# 
# 	return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
