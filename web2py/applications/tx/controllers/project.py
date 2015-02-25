# -*- coding: utf-8 -*-

from txform import BOOTUPFORM

#from tx import *

def create():
	form = BOOTUPFORM(db.Project)
	message = ""
	if form.process().accepted:
		redirect(URL('project', 'populate', args=form.vars.id))
	return dict(form=form, message=message)
	
def populate():
	project_id = request.args(0)
	project = db((db.Project.id == project_id)).select()[0]
	return dict(project=project)
	
def addImage():
	project_id = request.args(0)
	# Hide project ID Field
	db.Image.project_id.readable = db.Image.project_id.writable = False
	form = BOOTUPFORM(db.Image)
	# Fill in the Project ID
	form.vars.project_id = project_id
	message = ""
	if form.process().accepted:
		redirect(URL('project', 'populate', args=project_id))
	return dict(form=form, message=message)
	
def addField():
	project_id = request.args(0)
	# Hide project ID Field
	db.ProjectField.project_id.readable = db.ProjectField.project_id.writable = False
	form = BOOTUPFORM(db.ProjectField)
	# Fill in the Project ID
	form.vars.project_id = project_id
	message = ""
	if form.process().accepted:
		redirect(URL('project', 'populate', args=project_id))
	return dict(form=form, message=message)	