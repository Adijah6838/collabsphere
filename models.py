# models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
import datetime
Base = declarative_base()
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    desc = Column(Text, default="")
class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, default="member")
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String, nullable=False)
    desc = Column(Text, default="")
    status = Column(String, default="todo")
    priority = Column(String, default="medium")
    assignee = Column(String, default="")
    due = Column(String, default="")
    version = Column(Integer, default=1)
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    author = Column(String, default="anon")
    text = Column(Text)
    created = Column(DateTime, default=datetime.datetime.utcnow)
class Activity(Base):
    __tablename__ = "activity"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    actor = Column(String, default="system")
    action = Column(String)
    detail = Column(Text, default="")
    created = Column(DateTime, default=datetime.datetime.utcnow)
