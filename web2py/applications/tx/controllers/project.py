# -*- coding: utf-8 -*-

from txform import BOOTUPFORM

#from tx import *

def create():
	form = BOOTUPFORM(db.Project)
	message = ""
	if form.process().accepted:
		redirect(URL('project', 'populate'))
	return dict(form=form, message=message)
    
def populate():
	return dict()