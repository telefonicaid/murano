#    Copyright (c) 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
SQLAlchemy models for glazierapi data
"""
import anyjson

from sqlalchemy import Column, String, BigInteger, TypeDecorator, ForeignKey
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, Text
from sqlalchemy.orm import relationship, backref, object_mapper
from glazierapi.common import uuidutils

from glazierapi.openstack.common import timeutils
from glazierapi.db.session import get_session

BASE = declarative_base()


@compiles(BigInteger, 'sqlite')
def compile_big_int_sqlite(type_, compiler, **kw):
    return 'INTEGER'


class ModelBase(object):
    __protected_attributes__ = {"created", "updated"}

    created = Column(DateTime, default=timeutils.utcnow,
                     nullable=False)
    updated = Column(DateTime, default=timeutils.utcnow,
                     nullable=False, onupdate=timeutils.utcnow)

    def save(self, session=None):
        """Save this object"""
        session = session or get_session()
        session.add(self)
        session.flush()

    def update(self, values):
        """dict.update() behaviour."""
        for k, v in values.iteritems():
            self[k] = v

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        self._i = iter(object_mapper(self).columns)
        return self

    def next(self):
        n = self._i.next().name
        return n, getattr(self, n)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def to_dict(self):
        dictionary = self.__dict__.copy()
        return {k: v for k, v in dictionary.iteritems()
                if k != '_sa_instance_state'}


class JsonBlob(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        return anyjson.serialize(value)

    def process_result_value(self, value, dialect):
        return anyjson.deserialize(value)


class Environment(BASE, ModelBase):
    """Represents a Environment in the metadata-store"""
    __tablename__ = 'environment'

    id = Column(String(32), primary_key=True, default=uuidutils.generate_uuid)
    name = Column(String(255), nullable=False)
    tenant_id = Column(String(32), nullable=False)
    description = Column(JsonBlob(), nullable=False, default='{}')

    def to_dict(self):
        dictionary = super(Environment, self).to_dict()
        del dictionary['description']
        return dictionary


class Session(BASE, ModelBase):
    __tablename__ = 'session'

    id = Column(String(32), primary_key=True, default=uuidutils.generate_uuid)
    environment_id = Column(String(32), ForeignKey('environment.id'))
    environment = relationship(Environment,
                               backref=backref('session'),
                               uselist=False, lazy='joined')
    user_id = Column(String(36), nullable=False)
    state = Column(String(36), nullable=False)
    description = Column(JsonBlob(), nullable=False)

    def to_dict(self):
        dictionary = super(Session, self).to_dict()
        del dictionary['description']
        return dictionary


class Status(BASE, ModelBase):
    __tablename__ = 'status'

    id = Column(String(32), primary_key=True, default=uuidutils.generate_uuid)
    entity_id = Column(String(32), nullable=False)
    entity = Column(String(10), nullable=False)
    environment_id = Column(String(32), ForeignKey('environment.id'))
    session_id = Column(String(32), ForeignKey('session.id'))
    text = Column(Text(), nullable=False)


def register_models(engine):
    """
    Creates database tables for all models with the given engine
    """
    models = (Environment, Status, Session)
    for model in models:
        model.metadata.create_all(engine)


def unregister_models(engine):
    """
    Drops database tables for all models with the given engine
    """
    models = (Environment, Status, Session)
    for model in models:
        model.metadata.drop_all(engine)