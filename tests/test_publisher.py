import base64
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

p=Path(__file__).resolve().parents[1]/'host/publisher.py'
spec=importlib.util.spec_from_file_location('publisher',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Response(io.BytesIO):
    status=200

class PublisherTests(unittest.TestCase):
    def test_public_document_contains_only_hostname_metadata(self):
        requests=[]
        def opened(req,**kwargs):
            requests.append(req)
            return Response(b'{"sha":"previous-sha"}') if len(requests)==1 else Response(b'{}')
        with tempfile.TemporaryDirectory() as directory:
            token=Path(directory)/'token';token.write_text('private-test-credential')
            with patch.object(m,'TOKEN_FILE',token),patch.object(m.OPENER,'open',side_effect=opened):
                m.publish('latest.trycloudflare.com',datetime(2026,11,17,tzinfo=timezone.utc))
        payload=json.loads(requests[1].data)
        document=json.loads(base64.b64decode(payload['content']))
        self.assertEqual(document['hostname'],'latest.trycloudflare.com')
        self.assertTrue(document['online'])
        self.assertNotIn('private-test-credential',json.dumps(payload))
        self.assertEqual(payload['sha'],'previous-sha')
        self.assertEqual(requests[1].headers['Authorization'],'Bearer private-test-credential')
    def test_backend_not_addon_ready_is_not_published(self):
        with patch.object(m,'fetch',side_effect=[{'hostname':'valid.trycloudflare.com'},{'status':'ok'}]):
            self.assertIsNone(m.candidate())

if __name__=='__main__':unittest.main()
