import json


class MisfitException(Exception):
    pass


class MisfitHttpException(MisfitException):
    """
    Base class for all HTTP exceptions raised by the Misfit API. All exceptions
    will have three attributes.

    - code: The status code of the HTTP response, defaults to 500
    - message: The messages returned from the Misfit API
    - response: If we have one, this attribute will be the response object, of
      type :code:`requests.models.Response`. It's useful to have access to this
      because each response contains useful headers. For example, if the
      library throws an exception of type :code:`MisfitRateLimitError` you can
      retrieve a time stamp for when the rate limit resets with the following
      code: :code:`exc.response.headers['x-ratelimit-reset']`
    """
    def __init__(self, code, message, response=None):
        self.code = code
        self.message = message
        self.response = response
        super(MisfitHttpException, self).__init__(self, message)

    @staticmethod
    def build_exception(exc):
        code = exc.response.status_code if hasattr(exc, 'response') else 500
        message = exc.message if hasattr(exc, 'message') else 'Unknown error'
        try:
            json_content = json.loads(exc.content.decode('utf8'))
        except ValueError:
            pass
        else:
            # Loading the content to json succeeded, try to get the
            # code/message from there
            if 'message' in json_content:
                message = json_content['message']
            elif 'error_message' in json_content:
                message = json_content['error_message']
            if 'code' in json_content:
                code = json_content['code']
            elif 'error_code' in json_content:
                code = json_content['error_code']

        exceptions = {
            400: MisfitBadRequest,
            401: MisfitUnauthorized,
            403: MisfitForbidden,
            404: MisfitNotFoundError,
            429: MisfitRateLimitError,
            500: MisfitUnknownError,
            502: MisfitBadGateway
        }
        raise exceptions[code](code, message, getattr(exc, 'response', None))


class MisfitNotFoundError(MisfitHttpException):
    pass


class MisfitBadRequest(MisfitHttpException):
    pass


class MisfitBadGateway(MisfitHttpException):
    pass


class MisfitUnauthorized(MisfitHttpException):
    pass


class MisfitForbidden(MisfitHttpException):
    pass


class MisfitRateLimitError(MisfitHttpException):
    pass


class MisfitUnknownError(MisfitHttpException):
    pass
