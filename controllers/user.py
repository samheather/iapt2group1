def login():
    # Set the page title
    response.title = T('Login | ') + request.application

    request.args.insert(0,"login")

    auth.settings.formstyle = 'bootstrap3_stacked'

    return dict(form=auth())


def logout():
    request.args.append("logout")
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())

def register():
    # Set the page title
    response.title = T('Register | ') + request.application

    request.args.append("register")
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())

def reset():
    # Set the page title
    response.title = T('Reset Password | ') + request.application

    request.args.append("request_reset_password")
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())