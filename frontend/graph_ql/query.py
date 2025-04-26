import graphene
from database import BillsTable, MembersTable, VotesTable, HighscoreTable, StreakTable
from graph_ql.typesdefs import Bills, Members, Votes, Highscore, Streak
from sqlalchemy import func, desc


class BillsCount(graphene.ObjectType):
    count_type = graphene.String()
    count = graphene.Int()

class MemberVote(graphene.ObjectType):
    member_id = graphene.Int()
    vote_id = graphene.Int()
    bill_id = graphene.Int()
    name = graphene.String()
    placement = graphene.String()
    party = graphene.String()
    vote = graphene.String()
    bill_date = graphene.String()
    first_seen = graphene.String()
    last_seen = graphene.String()

class Query(graphene.ObjectType):
    hello = graphene.String(
        name = graphene.Argument(graphene.String, default_value="World")
    )
    def resolve_hello(self, info, name):
        return 'Hello' + name
    
    get_votes = graphene.List(
        Votes, 
        id=graphene.Int(required=False), 
        bill_id=graphene.Int(required=False)
    )
    
    get_members =  graphene.List(
        Members, 
        id=graphene.Int(required=False), 
        name=graphene.String(required=False), 
        party=graphene.String(required=False), 
        placement=graphene.String(required=False)
    )
    
    get_bills = graphene.List(
        Bills, 
        id=graphene.Int(required=False),
        name=graphene.String(required=False), 
        report=graphene.String(required=False), 
        year=graphene.String(required=False),
        date=graphene.String(required=False)
    )
    
    get_highscore_type = graphene.List(
        Highscore, 
        highscore_type=graphene.String(), 
        max=graphene.Int(default_value=100)
    )
    
    get_streak = graphene.List(
        Streak, 
        max=graphene.Int(default_value=100)
    )
    
    def resolve_get_bills(self, info, **args):
        _id = args.get('id')
        name = args.get('name')
        report = args.get('report')
        year = args.get('year')
        date = args.get('date')
        bills_query = Bills.get_query(info)

        if _id:
            bills_query = bills_query.filter(BillsTable.id == _id)
        if name:
            bills_query = bills_query.filter(BillsTable.name.ilike(f"%{name}%"))
        if report:
            bills_query = bills_query.filter(BillsTable.report.ilike(f"%{report}%"))
        if year:
            bills_query = bills_query.filter(BillsTable.date.like(f"{year}%"))
        if date:
            bills_query = bills_query.filter(BillsTable.date == date)
        
        return bills_query.all()
    
    def resolve_get_members(self,info,**args):
        _id = args.get('id')
        name = args.get('name')
        party = args.get('party')
        placement = args.get('placement')
        members_query = Members.get_query(info)
        if _id:
            members_query = members_query.filter(MembersTable.id == _id)
        if name:
            members_query = members_query.filter(MembersTable.name.ilike(f"%{name}%"))
        if party:
            members_query = members_query.filter(MembersTable.party == _id)
        if placement:
            members_query = members_query.filter(MembersTable.placement == _id)
        

        return members_query.all()

    def resolve_get_votes(self,info,**args):
        member_id = args.get('member_id')
        bill_id = args.get('bill_id')
        votes_query = Votes.get_query(info)
        
        if member_id:
            votes_query = votes_query.filter(VotesTable.member_id == member_id)

        if bill_id:
            votes_query = votes_query.filter(VotesTable.bill_id == bill_id)
            
        return votes_query.all()

    def resolve_get_highscore_type(self, info, **args):
        """"""
        max_limit = args.get('max')
        highscore_type = args.get('highscore_type')
        
        hs_query = Highscore.get_query(info)
        return hs_query.filter(HighscoreTable.highscore_type == highscore_type).order_by(desc(HighscoreTable.highscore_value)).limit(max_limit)

    def resolve_get_streak(self, info, **args):
        """"""
        max_limit = args.get('max')
        
        streak_query = Streak.get_query(info)
        return streak_query.order_by(desc(StreakTable.streak_value)).limit(max_limit)