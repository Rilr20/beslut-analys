
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import engine, Base, MembersTable, VotesTable, HighscoreTable,StreakTable,BillsTable
from collections import Counter
from datetime import datetime
from VoteAnalyzer import VoteAnalyzer

def get_days(start,end):
    """
    """
    start_time = datetime.strptime(start.split(" ")[0], "%Y-%m-%d")
    end_time = datetime.strptime(end.split(" ")[0], "%Y-%m-%d")
    return (end_time-start_time).days

def clean_highscores():
    """
    """
    session.query(HighscoreTable).delete()
    session.query(StreakTable).delete()
    session.commit()

if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    session = Session()
    analyzer = VoteAnalyzer(session)
    
    print("cleaning old scores")
    clean_highscores()
    
    member_ids = session.query(MembersTable.id).all()
    for idx, (member_id,) in enumerate(member_ids):
        print(f"{idx+1} / {len(member_ids)}: analyzing {member_id}")
        analyzer.analyze_member(member_id) 
