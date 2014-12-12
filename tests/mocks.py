import json

from httmock import urlmatch


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def not_found(*args):
    """ Mock requests to Misfit with 404 """
    return {'status_code': 404,
            'content': 'Cannot GET /move/resource/v1/user/me/profile/404/\n'}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def invalid_parameters(*args):
    """ Mock requests to Misfit with invalid parameters """
    json_content = {'error_message': 'Invalid parameters'}
    return {'status_code': 400, 'content': json.dumps(json_content)}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def bad_gateway(*args):
    """ Mock requests to Misfit with Bad Gateway error """
    json_content = {'error_code': 502, 'error_message': 'Bad Gateway'}
    return {'status_code': 502, 'content': json.dumps(json_content)}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def unauthorized(*args):
    """ Mock requests to Misfit with Unauthorized error """
    json_content = {'code': 401, 'message': 'Invalid Access Token'}
    return {'status_code': 401, 'content': json.dumps(json_content)}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def forbidden(*args):
    """ Mock requests to Misfit with Forbidden error """
    json_content = {'error_code': 403, 'error_message': 'Forbidden'}
    return {'status_code': 403, 'content': json.dumps(json_content)}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def unknown_error1(*args):
    """ Mock requests to Misfit with Unknown error 1 """
    return {'status_code': 500, 'content': "I HAVE NO IDEA WHAT'S GOING ON!"}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def unknown_error2(*args):
    """ Mock requests to Misfit with Unknown error 2 """
    return {'status_code': 500, 'content': "{}"}


@urlmatch(scheme='https', netloc='sns.us-east-1.amazonaws.com')
def sns_certificate(*args):
    """ Mock requests to retrieve the SNS signing certificate """
    with open('tests/files/certificate.pem') as cert_file:
        cert = cert_file.read()
    return cert


@urlmatch(scheme='https', netloc='example-subscribe-url.com')
def sns_subscribe(*args):
    """ Mock requests to the SNS SubscribeURL """
    return ''
