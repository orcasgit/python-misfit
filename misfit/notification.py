import arrow
import json
import requests

from base64 import standard_b64decode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15

from .misfit import MisfitObject


def string_to_sign(data):
    """ Build a signed SNS string from a dict """
    strings = []
    for key in ('Message', 'MessageId', 'Subject', 'SubscribeURL', 'Timestamp',
                'Token', 'TopicArn', 'Type'):
        if key in data:
            strings += [key, data[key]]
    strings.append("")
    return '\n'.join(strings).encode('utf8')


class MisfitNotification(MisfitObject):
    def __init__(self, data):
        """ Load the JSON to a dict and verify the signature if applicable """
        data_dict = json.loads(data.decode('utf8'))
        super(MisfitNotification, self).__init__(data_dict)
        if hasattr(self, 'Signature'):
            self.verify_signature()
        if self.Type == 'Notification':
            # Load the messages into a list of dicts, with arrow objects for
            # dates
            messages = json.loads(self.Message)
            for i, message in enumerate(messages):
                messages[i]['updatedAt'] = arrow.get(message['updatedAt'])
            self.Message = messages
        elif self.Type == 'SubscriptionConfirmation':
            # If the notification is a subscription confirmation, fetch the
            # subscribe URL
            requests.get(self.SubscribeURL)

    def verify_signature(self):
        """
        Verify the signature of the SNS message.

        raises cryptography.exceptions.InvalidSignature
        """
        # Get the signing certificate and public key from the specified URL
        cert_url = self.data['SigningCertURL']
        cert_str = requests.get(cert_url).content.encode('utf8')
        cert = default_backend().load_pem_x509_certificate(cert_str)
        pubkey = cert.public_key()
        # Verify the signature
        signature = standard_b64decode(self.data['Signature'].encode('utf8'))
        verifier = pubkey.verifier(signature, PKCS1v15(), hashes.SHA1())
        verifier.update(string_to_sign(self.data))
        # verify returns None on success, raises InvalidSignature on failure
        assert verifier.verify() is None
