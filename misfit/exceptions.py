import json


class MisfitException(Exception):
    pass


class MisfitHttpException(MisfitException):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super(MisfitHttpException, self).__init__(self, message)

    @staticmethod
    def build_exception(exc):
        code = exc.response.status_code if hasattr(exc, 'response') else 500
        message = exc.message if hasattr(exc, 'message') else 'Unknown error'
        try:
            json_content = json.loads(exc.content)
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

        if code == 404:
            raise MisfitNotFoundError(code, message)
        elif code == 400:
            raise MisfitBadRequest(code, message)
        elif code == 502:
            raise MisfitBadGateway(code, message)
        elif code == 401:
            raise MisfitUnauthorized(code, message)
        elif code == 403:
            raise MisfitForbidden(code, message)
        else:
            raise MisfitUnknownError(code, message)


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


class MisfitUnknownError(MisfitHttpException):
    pass
