# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Xigua.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import XiguaCommon_pb2 as XiguaCommon__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='Xigua.proto',
  package='',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=b'\n\x0bXigua.proto\x1a\x11XiguaCommon.proto\"\xa8\x01\n\tXiguaLive\x12\x1d\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x0f.XiguaLive.Data\x12\x0e\n\x06\x63ursor\x18\x02 \x02(\t\x12\x16\n\x0e\x66\x65tch_interval\x18\x03 \x01(\x05\x12\x0b\n\x03now\x18\x04 \x01(\x05\x12\x14\n\x0cinternal_ext\x18\x05 \x02(\t\x1a\x31\n\x04\x44\x61ta\x12\x0e\n\x06method\x18\x01 \x02(\t\x12\x19\n\x07message\x18\x02 \x02(\x0b\x32\x08.Message'
  ,
  dependencies=[XiguaCommon__pb2.DESCRIPTOR,])




_XIGUALIVE_DATA = _descriptor.Descriptor(
  name='Data',
  full_name='XiguaLive.Data',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='method', full_name='XiguaLive.Data.method', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message', full_name='XiguaLive.Data.message', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=154,
  serialized_end=203,
)

_XIGUALIVE = _descriptor.Descriptor(
  name='XiguaLive',
  full_name='XiguaLive',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='data', full_name='XiguaLive.data', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cursor', full_name='XiguaLive.cursor', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fetch_interval', full_name='XiguaLive.fetch_interval', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='now', full_name='XiguaLive.now', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='internal_ext', full_name='XiguaLive.internal_ext', index=4,
      number=5, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_XIGUALIVE_DATA, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=35,
  serialized_end=203,
)

_XIGUALIVE_DATA.fields_by_name['message'].message_type = XiguaCommon__pb2._MESSAGE
_XIGUALIVE_DATA.containing_type = _XIGUALIVE
_XIGUALIVE.fields_by_name['data'].message_type = _XIGUALIVE_DATA
DESCRIPTOR.message_types_by_name['XiguaLive'] = _XIGUALIVE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

XiguaLive = _reflection.GeneratedProtocolMessageType('XiguaLive', (_message.Message,), {

  'Data' : _reflection.GeneratedProtocolMessageType('Data', (_message.Message,), {
    'DESCRIPTOR' : _XIGUALIVE_DATA,
    '__module__' : 'Xigua_pb2'
    # @@protoc_insertion_point(class_scope:XiguaLive.Data)
    })
  ,
  'DESCRIPTOR' : _XIGUALIVE,
  '__module__' : 'Xigua_pb2'
  # @@protoc_insertion_point(class_scope:XiguaLive)
  })
_sym_db.RegisterMessage(XiguaLive)
_sym_db.RegisterMessage(XiguaLive.Data)


# @@protoc_insertion_point(module_scope)
