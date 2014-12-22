from __future__ import unicode_literals

import arrow
import json
import unittest
import sys

from httmock import HTTMock
from nose.tools import eq_

from misfit import Misfit, MisfitGoal, MisfitSummary
from misfit.exceptions import MisfitException

from .mocks import MisfitHttMock


class TestMisfitAPI(unittest.TestCase):
    def setUp(self):
        self.misfit = Misfit('FAKE_ID', 'FAKE_SECRET', 'FAKE_TOKEN')

    def test_goal(self):
        """ Test retrieving a goal by date range """
        goal_dict = {
            "id": "51a4189acf12e53f81000001",
            "date": "2014-10-05",
            "points": 500,
            "targetPoints": 1000,
            "timeZoneOffset": -8
        }
        end_date = '2014-10-07'
        with HTTMock(MisfitHttMock('goal').json_http):
            goal_list = self.misfit.goal(start_date=goal_dict['date'],
                                         end_date=end_date)
        eq_(len(goal_list), 3)
        goal = goal_list[0]
        eq_(type(goal), MisfitGoal)
        self.assert_misfit_string(goal, goal_dict)
        eq_(goal_list[2].date, arrow.get(end_date))
        eq_(goal.id, goal_dict['id'])
        eq_(goal.date, arrow.get(goal_dict['date']))
        eq_(goal.points, goal_dict['points'])
        eq_(goal.targetPoints, goal_dict['targetPoints'])
        eq_(goal.timeZoneOffset, goal_dict['timeZoneOffset'])
        self.assertAlmostEqual(goal.percent_complete(), 50)

        # Check that percent_complete is None if targetPoints is 0
        goal.targetPoints = 0
        assert goal.percent_complete() is None

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
        eq_(type(goal), MisfitGoal)
        self.assert_misfit_string(goal, goal_dict)
        eq_(goal.id, goal_dict['id'])
        eq_(goal.date, arrow.get(goal_dict['date']))
        eq_(goal.points, goal_dict['points'])
        eq_(goal.targetPoints, goal_dict['targetPoints'])
        eq_(goal.timeZoneOffset, goal_dict['timeZoneOffset'])
        self.assertAlmostEqual(goal.percent_complete(), 50)

        # Check that percent_complete is None if targetPoints is 0
        goal.targetPoints = 0
        assert goal.percent_complete() is None

    def test_goal_object_date_exception(self):
        """
        Check that an exception is raised when no date range or object id is
        supplied to goal
        """
        self.assertRaises(MisfitException, self.misfit.goal)

    def test_summary(self):
        """ Test retrieving a non-detail summary """
        date_range = {'start_date': '2014-12-10', 'end_date': '2014-12-17'}
        with HTTMock(MisfitHttMock('summary').json_http):
            summary = self.misfit.summary(start_date='2014-12-10',
                                          end_date='2014-12-17')

        summ_dict = {
            'activityCalories': 1449.2,
            'calories': 16310.24,
            'distance': 13.5227,
            'points': 3550,
            'steps': 34030
        }
        eq_(type(summary), MisfitSummary)
        self.assert_misfit_string(summary, summ_dict)
        eq_(summary.data, summ_dict)
        eq_(summary.activityCalories, summ_dict['activityCalories'])
        eq_(summary.calories, summ_dict['calories'])
        eq_(summary.distance, summ_dict['distance'])
        eq_(summary.points, summ_dict['points'])
        eq_(summary.steps, summ_dict['steps'])

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
        eq_(type(summary), MisfitSummary)
        self.assert_misfit_string(summary, summ_dict)
        eq_(summary_list[2].date, arrow.get(end_date))
        eq_(summary.data, summ_dict)
        eq_(summary.date, arrow.get(summ_dict['date']))
        eq_(summary.points, summ_dict['points'])
        eq_(summary.steps, summ_dict['steps'])
        eq_(summary.calories, summ_dict['calories'])
        eq_(summary.activityCalories, summ_dict['activityCalories'])
        eq_(summary.distance, summ_dict['distance'])

    def assert_misfit_string(self, obj, data):
        """
        The string representing the misfit object should be the classname,
        followed by a ":", followed by the json data
        """
        parts = ('%s' % obj).split(': ', 1)
        eq_(parts[0], '%s' % type(obj))
        eq_(json.loads(parts[1]), data)
