from graphene import ObjectType, String, Field, Int, List
from graphene_sqlalchemy import SQLAlchemyObjectType
from database import BillsTable, MembersTable, VotesTable, HighscoreTable, StreakTable, db_session

class Bills(SQLAlchemyObjectType):
    class Meta:
        model = BillsTable

    id = Int()
    name = String()
    point = String()
    date = String()
    report = String()
    votes = List(lambda: Votes)


class Members(SQLAlchemyObjectType):
    class Meta:
        model = MembersTable

    id = Int()
    name = String()
    party = String()
    placement = Int()
    first_seen = String()
    last_seen = String()
    
    votes = List(lambda: Votes)
    highscores = List(lambda: Highscore)
    streaks = List(lambda: Streak)

class Votes(SQLAlchemyObjectType):
    class Meta:
        model = VotesTable
    
    id = Int()
    member_id = Int()
    bill_id = Int()
    vote = String()

    member = Field(lambda: Members)
    bill = Field(lambda: Bills)
        
class Highscore(SQLAlchemyObjectType):
    class Meta:
        model = HighscoreTable
    id = Int()
    member_id = Int()
    highscore_type = String()
    highscore_value = Int()
    last_updated = String()

    member = Field(lambda: Members)
    
class Streak(SQLAlchemyObjectType):
    class Meta:
        model = StreakTable
    member_id = Int()
    highscore_type = String()
    streak_value = Int()
    start_date = String()
    end_date = String()
    last_updated = String()
    
    member = Field(lambda: Members)