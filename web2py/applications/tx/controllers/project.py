# -*- coding: utf-8 -*-

from txform import BOOTUPFORM

#from tx import *
@auth.requires_login()
def create():
	form = BOOTUPFORM(db.Project)
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

	form = BOOTUPFORM(db.Image)
	# Fill in the Project ID
	form.vars.project_id = project_id
	message = ""
	if form.process().accepted:
		redirect(URL('project', 'populate', args=project_id))
	return dict(form=form, message=message)


@auth.requires_login()
def addField():
	project_id = request.args(0)

	form = BOOTUPFORM(db.ProjectField)
	# Fill in the Project ID
	form.vars.project_id = project_id
	message = ""
	if form.process().accepted:
		redirect(URL('project', 'populate', args=project_id))
	return dict(form=form, message=message)

