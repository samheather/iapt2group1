# -*- coding: utf-8 -*-

from txform import BOOTSTRAPFORM

#from tx import *
@auth.requires_login()
def create():
    form = BOOTSTRAPFORM(db.Project)
    message = ""
    if form.process().accepted:
        redirect(URL('project', 'populate', args=form.vars.id))
    return dict(form=form, message=message)


@auth.requires_login()
def populate():
    project_id = request.args(0)
    project = db((db.Project.id == project_id)).select()[0]
    return dict(project=project)



@auth.requires_login()
def addImage():
    project_id = request.args(0)

    form = BOOTSTRAPFORM(db.Image)
    # Fill in the Project ID
    form.vars.project_id = project_id
    message = ""
    if form.process().accepted:
        redirect(URL('project', 'populate', args=project_id))
    return dict(form=form, message=message)


@auth.requires_login()
def addField():
    project_id = request.args(0)

    form = BOOTSTRAPFORM(db.ProjectField)
    # Fill in the Project ID
    form.vars.project_id = project_id
    message = ""
    if form.process().accepted:
        redirect(URL('project', 'populate', args=project_id))
    return dict(form=form, message=message)

def view():
    # Check if the URL has an argument; If not go to homepage
    project_id = request.args(0) or redirect(URL('default', 'index'))

    #Check if there is a project in the database with that ID. If not,
    # go to the homeapge.
    project = db.Project(project_id) or redirect(URL('default', 'index'))

    # Only display projects which are open to the public
    #if project.ProjectOpen:
    images = db(db.Image.project_id == project_id).select()
    fields = db(db.ProjectField.project_id == project_id).select()
    owner = db.auth_user(project.owner_id)
    return dict(project = project, images = images, fields = fields, owner = owner)

@auth.requires_login()
def deleteField():
	project_id = request.args(0)
	toDelete_id = request.args(1)
	db(db.ProjectField.id == toDelete_id).delete()
	redirect(URL('project', 'populate', args=project_id))

@auth.requires_login()
def deleteImage():
	project_id = request.args(0)
	toDelete_id = request.args(1)
	db(db.Image.id == toDelete_id).delete()
	redirect(URL('project', 'populate', args=project_id))


# Download the image from the web2py uploads folder
def img():
    return response.download(request, db)