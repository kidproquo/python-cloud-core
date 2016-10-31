# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest


class Test__compute_type_url(unittest.TestCase):

    def _callFUT(self, klass, prefix=None):
        from google.cloud.operation import _compute_type_url
        if prefix is None:
            return _compute_type_url(klass)
        return _compute_type_url(klass, prefix)

    def test_wo_prefix(self):
        from google.protobuf.struct_pb2 import Struct
        from google.cloud.operation import _GOOGLE_APIS_PREFIX

        type_url = self._callFUT(Struct)

        self.assertEqual(
            type_url,
            '%s/%s' % (_GOOGLE_APIS_PREFIX, Struct.DESCRIPTOR.full_name))

    def test_w_prefix(self):
        from google.protobuf.struct_pb2 import Struct
        PREFIX = 'test.google-cloud-python.com'

        type_url = self._callFUT(Struct, PREFIX)

        self.assertEqual(
            type_url,
            '%s/%s' % (PREFIX, Struct.DESCRIPTOR.full_name))


class Test_register_type_url(unittest.TestCase):

    def _callFUT(self, type_url, klass):
        from google.cloud.operation import register_type_url
        register_type_url(type_url, klass)

    def test_simple(self):
        from google.cloud import operation as MUT
        from google.cloud._testing import _Monkey
        TYPE_URI = 'testing.google-cloud-python.com/testing'
        klass = object()
        type_url_map = {}

        with _Monkey(MUT, _TYPE_URL_MAP=type_url_map):
            self._callFUT(TYPE_URI, klass)

        self.assertEqual(type_url_map, {TYPE_URI: klass})

    def test_w_same_class(self):
        from google.cloud import operation as MUT
        from google.cloud._testing import _Monkey
        TYPE_URI = 'testing.google-cloud-python.com/testing'
        klass = object()
        type_url_map = {TYPE_URI: klass}

        with _Monkey(MUT, _TYPE_URL_MAP=type_url_map):
            self._callFUT(TYPE_URI, klass)

        self.assertEqual(type_url_map, {TYPE_URI: klass})

    def test_w_conflict(self):
        from google.cloud import operation as MUT
        from google.cloud._testing import _Monkey
        TYPE_URI = 'testing.google-cloud-python.com/testing'
        klass, other = object(), object()
        type_url_map = {TYPE_URI: other}

        with _Monkey(MUT, _TYPE_URL_MAP=type_url_map):
            with self.assertRaises(ValueError):
                self._callFUT(TYPE_URI, klass)

        self.assertEqual(type_url_map, {TYPE_URI: other})


class OperationTests(unittest.TestCase):

    OPERATION_NAME = 'operations/projects/foo/instances/bar/operations/123'

    def _getTargetClass(self):
        from google.cloud.operation import Operation
        return Operation

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        client = _Client()
        operation = self._makeOne(
            self.OPERATION_NAME, client)
        self.assertEqual(operation.name, self.OPERATION_NAME)
        self.assertIs(operation.client, client)
        self.assertIsNone(operation.target)
        self.assertIsNone(operation.response)
        self.assertIsNone(operation.error)
        self.assertIsNone(operation.metadata)
        self.assertEqual(operation.caller_metadata, {})

    def test_ctor_explicit(self):
        client = _Client()
        operation = self._makeOne(
            self.OPERATION_NAME, client, foo='bar')

        self.assertEqual(operation.name, self.OPERATION_NAME)
        self.assertIs(operation.client, client)
        self.assertIsNone(operation.target)
        self.assertIsNone(operation.response)
        self.assertIsNone(operation.error)
        self.assertIsNone(operation.metadata)
        self.assertEqual(operation.caller_metadata, {'foo': 'bar'})

    def test_from_pb_wo_metadata_or_kw(self):
        from google.longrunning import operations_pb2
        client = _Client()
        operation_pb = operations_pb2.Operation(name=self.OPERATION_NAME)
        klass = self._getTargetClass()

        operation = klass.from_pb(operation_pb, client)

        self.assertEqual(operation.name, self.OPERATION_NAME)
        self.assertIs(operation.client, client)
        self.assertIsNone(operation.metadata)
        self.assertEqual(operation.caller_metadata, {})

    def test_from_pb_w_unknown_metadata(self):
        from google.longrunning import operations_pb2
        from google.protobuf.any_pb2 import Any
        from google.protobuf.json_format import ParseDict
        from google.protobuf.struct_pb2 import Struct
        from google.cloud._testing import _Monkey
        from google.cloud import operation as MUT

        type_url = 'type.googleapis.com/%s' % (Struct.DESCRIPTOR.full_name,)
        client = _Client()
        meta = ParseDict({'foo': 'Bar'}, Struct())
        metadata_pb = Any(type_url=type_url, value=meta.SerializeToString())
        operation_pb = operations_pb2.Operation(
            name=self.OPERATION_NAME, metadata=metadata_pb)
        klass = self._getTargetClass()

        with _Monkey(MUT, _TYPE_URL_MAP={type_url: Struct}):
            operation = klass.from_pb(operation_pb, client)

        self.assertEqual(operation.name, self.OPERATION_NAME)
        self.assertIs(operation.client, client)
        self.assertEqual(operation.metadata, meta)
        self.assertEqual(operation.caller_metadata, {})

    def test_from_pb_w_metadata_and_kwargs(self):
        from google.longrunning import operations_pb2
        from google.protobuf.any_pb2 import Any
        from google.protobuf.struct_pb2 import Struct
        from google.protobuf.struct_pb2 import Value
        from google.cloud import operation as MUT
        from google.cloud._testing import _Monkey

        type_url = 'type.googleapis.com/%s' % (Struct.DESCRIPTOR.full_name,)
        type_url_map = {type_url: Struct}

        client = _Client()
        meta = Struct(fields={'foo': Value(string_value=u'Bar')})
        metadata_pb = Any(type_url=type_url, value=meta.SerializeToString())
        operation_pb = operations_pb2.Operation(
            name=self.OPERATION_NAME, metadata=metadata_pb)
        klass = self._getTargetClass()

        with _Monkey(MUT, _TYPE_URL_MAP=type_url_map):
            operation = klass.from_pb(operation_pb, client, baz='qux')

        self.assertEqual(operation.name, self.OPERATION_NAME)
        self.assertIs(operation.client, client)
        self.assertEqual(operation.metadata, meta)
        self.assertEqual(operation.caller_metadata, {'baz': 'qux'})

    def test_complete_property(self):
        client = _Client()
        operation = self._makeOne(self.OPERATION_NAME, client)
        self.assertFalse(operation.complete)
        operation._complete = True
        self.assertTrue(operation.complete)
        with self.assertRaises(AttributeError):
            operation.complete = False

    def test_poll_already_complete(self):
        client = _Client()
        operation = self._makeOne(self.OPERATION_NAME, client)
        operation._complete = True

        with self.assertRaises(ValueError):
            operation.poll()

    def test_poll_false(self):
        from google.longrunning import operations_pb2

        response_pb = operations_pb2.Operation(done=False)
        client = _Client()
        stub = client._operations_stub
        stub._get_operation_response = response_pb
        operation = self._makeOne(self.OPERATION_NAME, client)

        self.assertFalse(operation.poll())

        request_pb = stub._get_operation_requested
        self.assertIsInstance(request_pb, operations_pb2.GetOperationRequest)
        self.assertEqual(request_pb.name, self.OPERATION_NAME)

    def test_poll_true(self):
        from google.longrunning import operations_pb2

        response_pb = operations_pb2.Operation(done=True)
        client = _Client()
        stub = client._operations_stub
        stub._get_operation_response = response_pb
        operation = self._makeOne(self.OPERATION_NAME, client)

        self.assertTrue(operation.poll())

        request_pb = stub._get_operation_requested
        self.assertIsInstance(request_pb, operations_pb2.GetOperationRequest)
        self.assertEqual(request_pb.name, self.OPERATION_NAME)

    def test__update_state_done(self):
        from google.longrunning import operations_pb2

        operation = self._makeOne(None, None)
        self.assertFalse(operation.complete)
        operation_pb = operations_pb2.Operation(done=True)
        operation._update_state(operation_pb)
        self.assertTrue(operation.complete)

    def test__update_state_metadata(self):
        from google.longrunning import operations_pb2
        from google.protobuf.any_pb2 import Any
        from google.protobuf.struct_pb2 import Value
        from google.cloud._testing import _Monkey
        from google.cloud import operation as MUT

        operation = self._makeOne(None, None)
        self.assertIsNone(operation.metadata)

        val_pb = Value(number_value=1337)
        type_url = 'type.googleapis.com/%s' % (Value.DESCRIPTOR.full_name,)
        val_any = Any(type_url=type_url, value=val_pb.SerializeToString())
        operation_pb = operations_pb2.Operation(metadata=val_any)

        with _Monkey(MUT, _TYPE_URL_MAP={type_url: Value}):
            operation._update_state(operation_pb)

        self.assertEqual(operation.metadata, val_pb)

    def test__update_state_error(self):
        from google.longrunning import operations_pb2
        from google.rpc.status_pb2 import Status
        from google.cloud._testing import _Monkey

        operation = self._makeOne(None, None)
        self.assertIsNone(operation.error)
        self.assertIsNone(operation.response)

        error_pb = Status(code=1)
        operation_pb = operations_pb2.Operation(error=error_pb)
        operation._update_state(operation_pb)

        self.assertEqual(operation.error, error_pb)
        self.assertIsNone(operation.response)

    def test__update_state_response(self):
        from google.longrunning import operations_pb2
        from google.protobuf.any_pb2 import Any
        from google.protobuf.struct_pb2 import Value
        from google.cloud._testing import _Monkey
        from google.cloud import operation as MUT

        operation = self._makeOne(None, None)
        self.assertIsNone(operation.error)
        self.assertIsNone(operation.response)

        response_pb = Value(string_value='totes a response')
        type_url = 'type.googleapis.com/%s' % (Value.DESCRIPTOR.full_name,)
        response_any = Any(type_url=type_url,
                           value=response_pb.SerializeToString())
        operation_pb = operations_pb2.Operation(response=response_any)

        with _Monkey(MUT, _TYPE_URL_MAP={type_url: Value}):
            operation._update_state(operation_pb)

        self.assertIsNone(operation.error)
        self.assertEqual(operation.response, response_pb)

    def test__update_state_no_result(self):
        from google.longrunning import operations_pb2

        operation = self._makeOne(None, None)
        self.assertIsNone(operation.error)
        self.assertIsNone(operation.response)

        operation_pb = operations_pb2.Operation()
        operation._update_state(operation_pb)

        # Make sure nothing changed.
        self.assertIsNone(operation.error)
        self.assertIsNone(operation.response)


class _OperationsStub(object):

    def GetOperation(self, request_pb):
        self._get_operation_requested = request_pb
        return self._get_operation_response


class _Client(object):

    def __init__(self):
        self._operations_stub = _OperationsStub()
