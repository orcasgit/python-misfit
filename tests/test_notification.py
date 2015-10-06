from __future__ import unicode_literals

import arrow
import json
import unittest
import sys

from base64 import standard_b64encode
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from httmock import HTTMock
from nose.tools import eq_, ok_

from misfit.notification import MisfitNotification

from .mocks import sns_certificate, sns_subscribe


class TestMisfitNotification(unittest.TestCase):
    def setUp(self):
        self.confirmation = {
            'Timestamp': '2014-12-11T19:21:18.852Z',
            'SubscribeURL': 'https://example-subscribe-url.com/path/to/verify_endpoint?verify_token=long_token&challenge=challenge',
            'Token': 'very_long_token',
            'Message': 'You have chosen to subscribe to the topic arn:aws:sns:us-east-1:<number>:topic.\nTo confirm the subscription, visit the SubscribeURL included in this message.',
            'Type': 'SubscriptionConfirmation',
            'TopicArn': 'arn:aws:sns:us-east-1:<number>:topic'
        }
        self.signed_confirmation = {
            'Timestamp': '2014-12-11T19:21:18.852Z',
            'SubscribeURL': 'https://example-subscribe-url.com/path/to/verify_endpoint?verify_token=long_token&challenge=challenge',
            'Token': 'very_long_token',
            'Message': 'You have chosen to subscribe to the topic arn:aws:sns:us-east-1:<number>:topic.\nTo confirm the subscription, visit the SubscribeURL included in this message.',
            'MessageId': 'message-id',
            'Type': 'SubscriptionConfirmation',
            'SignatureVersion': '1',
            'SigningCertURL': 'https://sns.us-east-1.amazonaws.com/SimpleNotificationService-d6d679a1d18e95c2f9ffcf11f4f9e198.pem',
            'TopicArn': 'arn:aws:sns:us-east-1:<number>:topic'
        }
        self.notification = {
            "Type": "Notification",
            "MessageId": "message-id",
            "TopicArn": "topic-arn",
            "Message": "[{\"type\":\"goals\",\"id\":\"scrubbed\",\"ownerId\":\"scrubbed\",\"action\":\"updated\",\"updatedAt\":\"2014-12-11T20:23:43Z\"}]",
            "Timestamp": "2014-12-11T20:23:44.182Z",
            "SignatureVersion": "1",
            "SigningCertURL": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-d6d679a1d18e95c2f9ffcf11f4f9e198.pem",
            "UnsubscribeURL": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=subscription-arn"
        }
        # Generate a signature for the necessary messages
        # privkey.pem created with the following command:
        # openssl req -nodes -sha1 -x509 -newkey rsa:2048 -days 999999 \
        #   -keyout tests/files/privkey.pem -out tests/files/certificate.pem
        # and given a password of 'test'
        with open('tests/files/privkey.pem') as key_file:
            key_content = key_file.read().encode('utf8')
        key = default_backend().load_pem_private_key(key_content, None)
        strings_to_sign = {
            # Hardcode these so our test suite is less of an echo chamber
            'signed_confirmation': 'Message\nYou have chosen to subscribe to the topic arn:aws:sns:us-east-1:<number>:topic.\nTo confirm the subscription, visit the SubscribeURL included in this message.\nMessageId\nmessage-id\nSubscribeURL\nhttps://example-subscribe-url.com/path/to/verify_endpoint?verify_token=long_token&challenge=challenge\nTimestamp\n2014-12-11T19:21:18.852Z\nToken\nvery_long_token\nTopicArn\narn:aws:sns:us-east-1:<number>:topic\nType\nSubscriptionConfirmation\n',
            'notification': 'Message\n[{"type":"goals","id":"scrubbed","ownerId":"scrubbed","action":"updated","updatedAt":"2014-12-11T20:23:43Z"}]\nMessageId\nmessage-id\nTimestamp\n2014-12-11T20:23:44.182Z\nTopicArn\ntopic-arn\nType\nNotification\n'
        }
        for message, string_to_sign in strings_to_sign.items():
            signer = key.signer(PKCS1v15(), hashes.SHA1())
            signer.update(string_to_sign.encode('utf8'))
            signature = standard_b64encode(signer.finalize())
            getattr(self, message)['Signature'] = signature.decode('utf8')

    def test_init(self):
        """
        Test that we can initialize MisfitNotification objects with a JSON
        string and that signatures get verified when necessary
        """
        # Unsigned SubscriptionConfirmation
        confirmation_content = json.dumps(self.confirmation).encode('utf8')
        with HTTMock(sns_subscribe):
            confirmation = MisfitNotification(confirmation_content)
        eq_(confirmation.Timestamp, arrow.get(self.confirmation['Timestamp']))
        eq_(confirmation.SubscribeURL, self.confirmation['SubscribeURL'])
        eq_(confirmation.Token, self.confirmation['Token'])
        eq_(confirmation.Message, self.confirmation['Message'])
        eq_(confirmation.Type, 'SubscriptionConfirmation')
        eq_(confirmation.TopicArn, self.confirmation['TopicArn'])

        # Signed SubscriptionConfirmation
        confirmation_str = json.dumps(self.signed_confirmation).encode('utf8')
        with HTTMock(sns_subscribe, sns_certificate):
            confirmation = MisfitNotification(confirmation_str)
        eq_(confirmation.Timestamp, arrow.get(self.signed_confirmation['Timestamp']))
        eq_(confirmation.SubscribeURL, self.signed_confirmation['SubscribeURL'])
        eq_(confirmation.Token, self.signed_confirmation['Token'])
        eq_(confirmation.Message, self.signed_confirmation['Message'])
        eq_(confirmation.MessageId, self.signed_confirmation['MessageId'])
        eq_(confirmation.Type, 'SubscriptionConfirmation')
        eq_(confirmation.TopicArn, self.signed_confirmation['TopicArn'])

        # Signed Notification
        notification_content = json.dumps(self.notification).encode('utf8')
        with HTTMock(sns_certificate):
            notification = MisfitNotification(notification_content)
        eq_(notification.Type, self.notification['Type'])
        eq_(notification.MessageId, self.notification['MessageId'])
        eq_(notification.TopicArn, self.notification['TopicArn'])
        for i, message in enumerate(json.loads(self.notification['Message'])):
            eq_(notification.Message[i].type, message['type'])
            eq_(notification.Message[i].updatedAt, arrow.get(message['updatedAt']))
            eq_(notification.Message[i].action, message['action'])
            eq_(notification.Message[i].id, message['id'])
            eq_(notification.Message[i].ownerId, message['ownerId'])
        eq_(notification.Timestamp, arrow.get(self.notification['Timestamp']))
        eq_(notification.Signature, self.notification['Signature'])
        eq_(notification.SignatureVersion,
            self.notification['SignatureVersion'])
        eq_(notification.SigningCertURL, self.notification['SigningCertURL'])
        eq_(notification.UnsubscribeURL, self.notification['UnsubscribeURL'])

        # Check that an error is raised when the signature doesn't match
        self.notification['Signature'] = 'BAD_SIGNATURE'
        notification_content = json.dumps(self.notification).encode('utf8')
        with HTTMock(sns_certificate):
            try:
                MisfitNotification(notification_content)
                self.fail('Should have raised an exception')
            except InvalidSignature:
                pass
            except Exception:
                self.fail('Should have raised InvalidSignature')
