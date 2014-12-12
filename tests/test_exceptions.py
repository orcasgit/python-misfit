import arrow
import json
import sys
import unittest

from freezegun import freeze_time
from httmock import HTTMock

from misfit import Misfit
from misfit.exceptions import (
    MisfitException,
    MisfitBadRequest,
    MisfitNotFoundError,
    MisfitBadGateway,
    MisfitUnauthorized,
    MisfitForbidden,
    MisfitRateLimitError,
    MisfitUnknownError
)

from .mocks import (
    not_found,
    invalid_parameters,
    bad_gateway,
    unauthorized,
    forbidden,
    rate_limit,
    unknown_error1,
    unknown_error2
)


class TestMisfitExceptions(unittest.TestCase):
    def setUp(self):
        self.misfit = Misfit('FAKE_ID', 'FAKE_SECRET', 'FAKE_TOKEN')

    def test_not_found(self):
        with HTTMock(not_found):
            self.assertRaises(MisfitNotFoundError, self.misfit.profile, '404')

    def test_invalid_parameters(self):
        with HTTMock(invalid_parameters):
            self.assertRaises(MisfitBadRequest, self.misfit.goal,
                              'BAD_START_DATE', 'BAD_END_DATE')

    def test_bad_gateway(self):
        with HTTMock(bad_gateway):
            self.assertRaises(MisfitBadGateway, self.misfit.profile)

    def test_unauthorized(self):
        with HTTMock(unauthorized):
            self.assertRaises(MisfitUnauthorized, self.misfit.profile)

    def test_forbidden(self):
        with HTTMock(forbidden):
            self.assertRaises(MisfitForbidden, self.misfit.profile)

    @freeze_time("2014-12-12 22:00:01")
    def test_rate_limit(self):
        with HTTMock(rate_limit):
            try:
                self.misfit.profile()
            except MisfitRateLimitError:
                headers = sys.exc_info()[1].response.headers
                self.assertEqual(headers['x-ratelimit-limit'], '150')
                self.assertEqual(headers['x-ratelimit-remaining'], '148')
                reset = arrow.get(headers['x-ratelimit-reset'])
                self.assertEqual((reset - arrow.now()).seconds, 2577)
            else:
                self.assertFail('Should have thrown MisfitRateLimitError')

    def test_unknown_error1(self):
        with HTTMock(unknown_error1):
            self.assertRaises(MisfitUnknownError, self.misfit.profile)

    def test_unknown_error2(self):
        with HTTMock(unknown_error2):
            self.assertRaises(MisfitUnknownError, self.misfit.profile)
