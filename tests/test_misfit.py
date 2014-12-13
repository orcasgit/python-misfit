from __future__ import unicode_literals

import arrow
import json
import unittest
import sys

from httmock import HTTMock
from nose.tools import eq_

from misfit import Misfit

from .mocks import MisfitHttMock


class TestMisfitAPI(unittest.TestCase):
    def setUp(self):
        self.misfit = Misfit('FAKE_ID', 'FAKE_SECRET', 'FAKE_TOKEN')

    def test_goal_single(self):
        """ Test retrieving a goal by object_id """
        goal_dict = {
            "id": "51a4189acf12e53f81000001",
            "date": "2014-10-05",
            "points": 500,
            "targetPoints": 1000,
            "timeZoneOffset": -8
        }
        with HTTMock(MisfitHttMock('goal_single').json_http):
            goal = self.misfit.goal(object_id=goal_dict['id'])
        eq_(goal.id, goal_dict['id'])
        eq_(goal.date, arrow.get(goal_dict['date']))
        eq_(goal.points, goal_dict['points'])
        eq_(goal.targetPoints, goal_dict['targetPoints'])
        eq_(goal.timeZoneOffset, goal_dict['timeZoneOffset'])
        self.assertAlmostEqual(goal.percent_complete(), 50)

        # Check that percent_complete is None if targetPoints is 0
        goal.targetPoints = 0
        assert goal.percent_complete() is None

    def test_summary_detail(self):
        summ_dict = {
            "date": "2014-10-05",
            "points": 394.4,
            "steps": 3650,
            "calories": 1687.4735,
            "activityCalories": 412.3124,
            "distance": 1.18
        }
        end_date = "2014-10-07"
        with HTTMock(MisfitHttMock('summary_detail').json_http):
            summary_list = self.misfit.summary(
                start_date=summ_dict['date'], end_date=end_date, detail=True)
        eq_(len(summary_list), 3)
        summary = summary_list[0]
        eq_(summary.date, arrow.get(summ_dict['date']))
        eq_(summary_list[2].date, arrow.get(end_date))
        eq_(summary.points, summ_dict['points'])
        eq_(summary.steps, summ_dict['steps'])
        eq_(summary.calories, summ_dict['calories'])
        eq_(summary.activityCalories, summ_dict['activityCalories'])
        eq_(summary.distance, summ_dict['distance'])
