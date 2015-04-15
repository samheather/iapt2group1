from mark_mandatory import *

# Add the asteriks to the fields in the user table
mark_not_empty(auth.table_user())

def login():
    # Set the page title
    response.title = T('Login | TransXribe')

    request.args.insert(0,"login")

    auth.settings.formstyle = 'bootstrap3_stacked'

    return dict(form=auth())


def logout():
    request.args.append("logout")
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())

def register():
    # Set the page title
    response.title = T('Register | TransXribe')

    request.args.append("register")
    auth.settings.formstyle = 'bootstrap3_stacked'
    auth.settings.register_next = URL('default', 'index', args='newUser')
    return dict(form=auth())

def reset():
    # Set the page title
    response.title = T('Reset Password | TransXribe')

    request.args.append("request_reset_password")
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())