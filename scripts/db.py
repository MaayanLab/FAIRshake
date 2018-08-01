from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Float, ForeignKey, Integer, Table, Text, text
import json
Base = declarative_base()
metadata = Base.metadata

class Average(Base):
    __tablename__ = 'average'

    resource_id = Column('resource_id', Integer, primary_key=True)
    q_id = Column('q_id', Integer, primary_key=True)
    avg = Column('avg', Float(asdecimal=True))
    project_id = Column('project_id', Integer, server_default=text("'1'"), primary_key=True)

    def to_json(self):
        return {
            'resource_id': self.resource_id,
            'q_id': self.q_id,
            'avg': self.avg,
            'project_id': self.project_id,
        }

class Evaluation(Base):
    __tablename__ = 'evaluation'

    user_id = Column('user_id', Integer, primary_key=True)
    resource_id = Column('resource_id', Integer, primary_key=True)
    q_id = Column('q_id', Integer, primary_key=True)
    answer = Column('answer', Text)
    url_comment = Column('url_comment', Text)
    comment = Column('comment', Text)
    project_id = Column('project_id', Integer, server_default=text("'1'"), primary_key=True)

    def to_json(self):
        return {
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'q_id': self.q_id,
            'answer': self.answer,
            'url_comment': self.url_comment,
            'comment': self.comment,
            'project_id': self.project_id,
        }
class ResourceInProject(Base):
    __tablename__ = 'resource_in_project'

    resource_id = Column('resource_id', ForeignKey('resource.resource_id', onupdate='CASCADE'), primary_key=True, nullable=False)
    project_id = Column('project_id', ForeignKey('project.project_id', onupdate='CASCADE'), primary_key=True, nullable=False, index=True)

    def to_json(self):
        return {
            'resource_id': self.resource_id,
            'project_id': self.project_id,
        }

class Project(Base):
    __tablename__ = 'project'

    project_id = Column(Integer, primary_key=True)
    project_name = Column(Text)
    project_description = Column(Text)
    project_img = Column(Text)

    resources = relationship('Resource', secondary='resource_in_project')

    def to_json(self):
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'project_description': self.project_description,
            'project_img': self.project_img,
            'resources': [rc.to_json() for rc in self.resources],
        }

class Question(Base):
    __tablename__ = 'question'

    q_id = Column(Integer, primary_key=True)
    num = Column(Integer)
    version = Column(Integer, server_default=text("'1'"))
    content = Column(Text)
    F = Column(Text)
    A = Column(Text)
    I = Column(Text)
    R = Column(Text)
    res_type = Column(Text)

    def to_json(self):
        return {
            'q_id': self.q_id,
            'num': self.num,
            'version': self.version,
            'content': self.content,
            'F': self.F,
            'A': self.A,
            'I': self.I,
            'R': self.R,
            'res_type': self.res_type,
        }
class QuestionOld(Base):
    __tablename__ = 'question_old'

    q_id = Column(Integer, primary_key=True)
    num = Column(Integer)
    version = Column(Integer, server_default=text("'1'"))
    content = Column(Text)
    F = Column(Text)
    A = Column(Text)
    I = Column(Text)
    R = Column(Text)
    res_type = Column(Text)

    def to_json(self):
        return {
            'q_id': self.q_id,
            'num': self.num,
            'version': self.version,
            'content': self.content,
            'F': self.F,
            'A': self.A,
            'I': self.I,
            'R': self.R,
            'res_type': self.res_type,
        }
class Resource(Base):
    __tablename__ = 'resource'

    resource_id = Column(Integer, primary_key=True)
    resource_name = Column(Text)
    url = Column(Text)
    resource_type = Column(Text)
    description = Column(Text)
    project_id = Column(Integer, server_default=text("'1'"))

    def to_json(self):
        return {
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'url': self.url,
            'resource_type': self.resource_type,
            'description': self.description,
            'project_id': self.project_id,
        }
    
class Users(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    role_evaluator = Column(Text)
    role_starter = Column(Text)

    def to_json(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role_evaluator': self.role_evaluator,
            'role_starter': self.role_starter,
        }

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)

def get_db_engine(uri):
    from sqlalchemy import create_engine
    return create_engine(uri)

def get_db_session(uri):
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(bind=get_db_engine(uri))()

def create_db():
    Base.metadata.create_all(get_db_engine())
