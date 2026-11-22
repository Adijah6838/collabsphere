# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Project, Member
engine = create_engine("sqlite:///./collab.db", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
def seed():
    s = Session()
    if s.query(Project).count() == 0:
        s.add(Project(name="Website Redesign", desc="Q4 relaunch"))
        s.add(Project(name="Mobile App", desc="iOS + Android"))
        s.add(Member(name="Ada", role="admin"))
        s.add(Member(name="Bob", role="member"))
        s.add(Member(name="Cara", role="viewer"))
        s.commit()
    s.close()
seed()
