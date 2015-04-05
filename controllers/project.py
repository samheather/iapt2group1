# -*- coding: utf-8 -*-

from txform import BOOTSTRAPFORM

# from tx import *
@auth.requires_login()
def create():
    # Set the page title
    response.title = T('Create Project 1 of 2 | TransXribe')

    form = BOOTSTRAPFORM(db.Project)
    message = ""
    if form.process().accepted:
        redirect(URL('project', 'populate', args=form.vars.id))
    return dict(form=form, message=message)

@auth.requires_login()
def populate():
    # Set the page title
    response.title = T('Create Project 2 of 2 | TransXribe')

    project_id = request.args(0)
    project = db((db.Project.id == project_id)).select()[0]
    
    canClickCreate = True
    canClickCreateMessage = ''
    if (len(project.customFields()) == 0):
        canClickCreate = False
        canClickCreateMessage = 'Please add some fields to this project to be able to submit.'
    elif (len(project.images()) == 0):
        canClickCreate = False
        canClickCreateMessage = 'Please upload some images to this project to be able to submit.'
    if (len(project.customFields()) == 0) and (len(project.images()) == 0):
        canClickCreate = False
        canClickCreateMessage = 'Please add fields and images to this project to be able to submit.'
    
    return dict(project=project,
                canClickCreate=canClickCreate,
                canClickCreateMessage=canClickCreateMessage)

@auth.requires_login()
def addImage():
    # Set the page title
    response.title = T('Add Images | TransXribe')

    project_id = request.args(0)

    form = BOOTSTRAPFORM(db.Image, submit_button = "Upload image and return to Create Project")
    # Fill in the Project ID
    form.vars.project_id = project_id
    message = ""
    if form.process().accepted:
        redirect(URL('project', 'populate', args=project_id))
    return dict(form=form, message=message,projectid=project_id)

@auth.requires_login()
def addField():
    # Set the page title
    response.title = T('Add Fields | TransXribe')

    project_id = request.args(0)

    form = BOOTSTRAPFORM(db.ProjectField, submit_button = "Add field and return to Create Project")
    # Fill in the Project ID
    form.vars.project_id = project_id
    message = ""
    if form.process().accepted:
        redirect(URL('project', 'populate', args=project_id))
    return dict(form=form, message=message,projectid=project_id)

def view():
    # Set the page title
    response.title = T('View Project | TransXribe')
    message = session.message or ""
    session.message = ""

    # Check if the URL has an argument; If not go to homepage
    project_id = request.args(0) or redirect(URL('default', 'index'))

    #Check if there is a project in the database with that ID. If not,
    # go to the homepage.
    project = db.Project(project_id) or redirect(URL('default', 'index'))

    # Only display projects which are open to the public
    #if project.ProjectOpen:
    images = db(db.Image.project_id == project_id).select()
    fields = db(db.ProjectField.project_id == project_id).select()
    owner = db.auth_user(project.owner_id)
    return dict(project=project
                , images=images
                , fields=fields
                , owner=owner
                , message=message)

@auth.requires_login()
def transcribe():
    # Set the page title
    response.title = T('Transcribe | TransXribe')

    error_message = ''
    image_id = request.args(0) or 0
    if image_id == 0:
        redirect(URL('default', 'index'))
    else:
        image = db.Image(image_id)
        fields_no_html = db((db.ProjectField.project_id == image.project_id)
                            & (db.ProjectField.type_id == db.TranscriptionFieldType.id)) \
            .select()

        form = BOOTSTRAPFORM.generate(fields_no_html)

        #If form is posted
        if form.accepts(request.vars):
            atLeastOneFieldSet = False

            #Create a transcription object
            tx=db.Transcription.insert(image_id=image.id
                                       ,transcriber_id=auth.user_id
                                       ,rejected=None)

            for var in fields_no_html:
                if str(request.vars[str(var.ProjectField.id)]):
                    atLeastOneFieldSet=True

                    #Store the field value
                    db.TranscriptionField.insert(projectField_id=var.ProjectField.id
                                                 ,transcription_id=tx
                                                 ,value=str(request.vars[str(var.ProjectField.id)]))

            if atLeastOneFieldSet:
                session.message = "You've successfully added your transcription for this document."
                redirect(URL('project','view',args=image.project_id))
            else:
                #If no fields are set, then just rollback
                error_message = "You must fill in at least one field to submit a transcription."
                db.rollback()


        return dict(image=image, form=form, error_message=error_message)

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

def open():
    # Set the page title
    response.title = T('Open Project | TransXribe')
    project_id = request.args(0)

    project = db(db.Project.id == project_id).select()[0]

    if not project.canOpen():
        raise ("Unable to open this project")

    form = BOOTSTRAPFORM.confirm('Open', 'btn-primary', {'Back': URL('default', 'dashboard')})
    if form.accepted:
        db(db.Project.id == project_id).update(projectOpen=True)
        redirect(URL('project', 'view', args=project_id))
    return dict(project=project, form=form)

def close():
    # Set the page title
    response.title = T('Close Project | TransXribe')

    project_id = request.args(0)
    project = db(db.Project.id == project_id).select()[0]

    if not project.canClose():
        raise ("Unable to close this project")

    form = BOOTSTRAPFORM.confirm('Close', 'btn-primary', {'Back': URL('default', 'dashboard')})
    if form.accepted:
        db(db.Project.id == project_id).update(projectOpen=False)
        redirect(URL('default', 'dashboard'))

    return dict(project=project, form=form)

# Download the image from the web2py uploads folder
def img():
    return response.download(request, db)
