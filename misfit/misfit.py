import slumber

from oauthlib.oauth2 import Client
from requests_oauthlib import OAuth2


API_URL = 'https://api.misfitwearables.com/'


class Misfit:
    def __init__(self, client_id, client_secret, access_token, user_id=None):
        auth = OAuth2(client_id, Client(client_id),
                      {'access_token': access_token})
        user = user_id if user_id else 'me'
        self.api = slumber.API('%smove/resource/v1/user/%s/' %
                               (API_URL, user), auth=auth)

    def profile(self, object_id=None):
        return self._get_object(self.api.profile, object_id)

    def device(self, object_id=None):
        return self._get_object(self.api.device, object_id)

    def goal(self, start_date, end_date, object_id=None):
        return self._get_object(
            self.api.activity.goals, object_id,
            start_date=start_date, end_date=end_date)

    def summary(self, start_date, end_date, detail=False, object_id=None):
        return self._get_object(
            self.api.activity.summary, object_id,
            start_date=start_date, end_date=end_date,
            detail='true' if detail else 'false')

    def session(self, start_date, end_date, object_id=None):
        return self._get_object(
            self.api.activity.sessions, object_id,
            start_date=start_date, end_date=end_date)

    def sleep(self, start_date, end_date, object_id=None):
        return self._get_object(
            self.api.activity.sleeps, object_id,
            start_date=start_date, end_date=end_date)

    def _get_object(self, api_section, object_id=None, **kwargs):
        api_object = api_section
        if object_id:
            api_object = api_section(object_id)
        return api_object.get(**kwargs)
