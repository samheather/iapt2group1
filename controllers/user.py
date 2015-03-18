def login():
    request.args.append("login")
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())


def logout():
    request.args.append("logout")
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())

def register():
    request.args.append("register")
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())

def reset():
    request.args.append("request_reset_password")
    auth.settings.formstyle = 'bootstrap3_stacked'
    return dict(form=auth())