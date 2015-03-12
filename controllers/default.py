# -*- coding: utf-8 -*-

import datetime

#from tx import *

def index():
    return dict()

def search():
    searchTerm="%"+request.vars.searchTerm+"%"
    return dict()

def user():
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())

@auth.requires_login()
def dashboard():
	justAddedProject_id = int(request.args(0))
	user = db((db.auth_user.id == auth.user_id)).select()[0]
	return dict(user=user,justAddedProject_id=justAddedProject_id)


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