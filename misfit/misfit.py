import arrow
import json
import slumber
import sys

from oauthlib.oauth2 import Client
from requests_oauthlib import OAuth2
from slumber.exceptions import HttpClientError, HttpServerError
from slumber.serialize import Serializer, JsonSerializer

from .exceptions import MisfitException

API_URL = 'https://api.misfitwearables.com/'


class MisfitSerializer(JsonSerializer):
    """ Override the built-in JSON serializer to handle bytes """
    def loads(self, data):
        return json.loads(data.decode('utf8'))


class Misfit:
    def __init__(self, client_id, client_secret, access_token, user_id=None):
        auth = OAuth2(client_id, Client(client_id),
                      {'access_token': access_token})
        user = user_id if user_id else 'me'
        s = Serializer(default="json", serializers=[MisfitSerializer()])
        self.api = slumber.API('%smove/resource/v1/user/%s/' % (API_URL, user),
                               auth=auth, serializer=s)

    def profile(self, object_id=None):
        return MisfitProfile(self._get_object(self.api.profile, object_id))

    def device(self, object_id=None):
        return MisfitDevice(self._get_object(self.api.device, object_id))

    def goal(self, start_date, end_date, object_id=None):
        goals = self._get_object(
            self.api.activity.goals, object_id,
            start_date=start_date, end_date=end_date)['goals']
        return [MisfitGoal(goal) for goal in goals]

    def summary(self, start_date, end_date, detail=False, object_id=None):
        summary = self._get_object(
            self.api.activity.summary, object_id,
            start_date=start_date, end_date=end_date,
            detail='true' if detail else 'false')
        if 'summary' in summary:
            return [MisfitSummary(summ) for summ in summary['summary']]
        else:
            return MisfitSummary(summary)

    def session(self, start_date, end_date, object_id=None):
        sessions = self._get_object(
            self.api.activity.sessions, object_id,
            start_date=start_date, end_date=end_date)['sessions']
        return [MisfitSession(session) for session in sessions]

    def sleep(self, start_date, end_date, object_id=None):
        sleeps = self._get_object(
            self.api.activity.sleeps, object_id,
            start_date=start_date, end_date=end_date)['sleeps']
        return [MisfitSleep(sleep) for sleep in sleeps]

    def _get_object(self, api_section, object_id=None, **kwargs):
        try:
            args = (object_id,) if object_id else tuple()
            return api_section(*args).get(**kwargs)
        except (HttpClientError, HttpServerError):
            MisfitException.build_exception(sys.exc_info()[1])


class UnicodeMixin(object):
    if sys.version_info > (3, 0):
        __str__ = lambda x: x.__unicode__()
    else:
        __str__ = lambda x: unicode(x).encode('utf-8')


class MisfitObject(UnicodeMixin):
    def __init__(self, data):
        self.data = data
        for name, value in self.data.items():
            self.set_value(name, value)

    def set_value(self, name, value):
        if name in ['date', 'datetime', 'startTime']:
            setattr(self, name, arrow.get(value))
        else:
            setattr(self, name, value)

    def __unicode__(self):
        return '%s: %s' % (type(self), json.dumps(self.data))


class MisfitProfile(MisfitObject): pass


class MisfitDevice(MisfitObject): pass


class MisfitGoal(MisfitObject): pass


class MisfitSummary(MisfitObject): pass


class MisfitSession(MisfitObject): pass


class MisfitSleepDetail(MisfitObject): pass


class MisfitSleep(MisfitObject):
    def __init__(self, data):
        super(MisfitSleep, self).__init__(data)
        sleep_details = []
        for sleep_detail in self.sleepDetails:
            sleep_details.append(MisfitSleepDetail(sleep_detail))
        self.sleepDetails = sleep_details
