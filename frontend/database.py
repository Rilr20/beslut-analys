from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///../db/db.db")
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class BillsTable(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(String)
    point = Column(String)
    report = Column(String)

    votes = relationship("VotesTable", back_populates="bill")
    
class MembersTable(Base):
    """"""
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    party = Column(String)
    placement = Column(String)
    first_seen = Column(String)
    last_seen = Column(String)
    
    votes = relationship("VotesTable", back_populates="member")
    highscores = relationship("HighscoreTable", back_populates="member")
    streaks = relationship("StreakTable", back_populates="member")

class VotesTable(Base):
    """"""
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    bill_id = Column(Integer, ForeignKey("bills.id"))
    vote = Column(String)
    
    member = relationship("MembersTable", back_populates="votes")
    bill = relationship("BillsTable", back_populates="votes")
    
class HighscoreTable(Base):
    """"""
    __tablename__ = "highscores"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    highscore_type = Column(String)
    highscore_value = Column(Integer)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now()) 
    
    member = relationship("MembersTable", back_populates="highscores")

class StreakTable(Base):
    """"""
    __tablename__ = "streaks"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    highscore_type = Column(String)
    streak_value = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now()) 

    member = relationship("MembersTable", back_populates="streaks")