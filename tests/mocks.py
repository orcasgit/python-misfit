from httmock import urlmatch


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def not_found(*args):
    """ Mock requests to Misfit with 404 """
    return {'status_code': 404,
            'content': 'Cannot GET /move/resource/v1/user/me/profile/404/\n'}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def invalid_parameters(*args):
    """ Mock requests to Misfit with invalid parameters """
    return {'status_code': 400,
            'content': "{'error_message': 'Invalid parameters'}"}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def bad_gateway(*args):
    """ Mock requests to Misfit with Bad Gateway error """
    return {'status_code': 502,
            'content': "{'error_code': 502, 'error_message': 'Bad Gateway'}"}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def unauthorized(*args):
    """ Mock requests to Misfit with Unauthorized error """
    return {'status_code': 401,
            'content': "{'code': 401, 'message': 'Invalid Access Token'}"}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def forbidden(*args):
    """ Mock requests to Misfit with Forbidden error """
    return {'status_code': 403,
            'content': "{'error_code': 403, 'error_message': 'Forbidden'}"}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def unknown_error1(*args):
    """ Mock requests to Misfit with Unknown error 1 """
    return {'status_code': 500, 'content': "I HAVE NO IDEA WHAT'S GOING ON!"}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def unknown_error2(*args):
    """ Mock requests to Misfit with Unknown error 2 """
    return {'status_code': 500, 'content': "{}"}
