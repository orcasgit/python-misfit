import json

from httmock import urlmatch


class MisfitHttMock:
    def __init__(self, file_name_base):
        """ Build the response template """
        self.headers = {'content-type': 'application/json; charset=utf-8'}
        self.response_tmpl = {'status_code': 200, 'headers': self.headers}
        self.file_name_base = file_name_base

    @urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
    def json_http(self, *args):
        """ Generic method to return the contents of a json file """
        response = self.response_tmpl
        file_path = 'tests/files/responses/%s.json' % self.file_name_base
        with open(file_path) as json_file:
            response['content'] = json_file.read().encode('utf8')
        return response


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def not_found(*args):
    """ Mock requests to Misfit with 404 """
    return {'status_code': 404,
            'content': 'Cannot GET /move/resource/v1/user/me/profile/404/\n'}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def invalid_parameters(*args):
    """ Mock requests to Misfit with invalid parameters: 400 """
    json_content = {'error_message': 'Invalid parameters'}
    return {'status_code': 400, 'content': json.dumps(json_content)}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def bad_gateway(*args):
    """ Mock requests to Misfit with Bad Gateway error: 502 """
    json_content = {'error_code': 502, 'error_message': 'Bad Gateway'}
    return {'status_code': 502, 'content': json.dumps(json_content)}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def unauthorized(*args):
    """ Mock requests to Misfit with Unauthorized error: 401 """
    json_content = {'code': 401, 'message': 'Invalid Access Token'}
    return {'status_code': 401, 'content': json.dumps(json_content)}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def forbidden(*args):
    """ Mock requests to Misfit with Forbidden error: 403 """
    json_content = {'error_code': 403, 'error_message': 'Forbidden'}
    return {'status_code': 403, 'content': json.dumps(json_content)}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def rate_limit(*args):
    """ Mock requests to Misfit with rate limit error: 429 """
    headers = {
        'x-ratelimit-limit': '150',
        'x-ratelimit-remaining': '148',
        'x-ratelimit-reset': '1418424178'
    }
    json_content = {'error_code': 429, 'error_message': 'Rate limit exceeded'}
    return {'status_code': 429, 'content': json.dumps(json_content),
            'headers': headers}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def unknown_error1(*args):
    """ Mock requests to Misfit with Unknown error 1: 500 """
    return {'status_code': 500, 'content': "I HAVE NO IDEA WHAT'S GOING ON!"}


@urlmatch(scheme='https', netloc=r'api\.misfitwearables\.com')
def unknown_error2(*args):
    """ Mock requests to Misfit with Unknown error 2: 500 """
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
