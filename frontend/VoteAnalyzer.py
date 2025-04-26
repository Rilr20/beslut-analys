
class VoteAnalyzer:
    def __init__(self, session):
        self.session = session
    def analyze_member(self, member_id):
        votes = self.session.query(VotesTable).filter_by(member_id=member_id).all()
        print("checking when seen")  
        self.when_seen(votes)
        print("counting score")  
        self.count_score(votes)
        print("counting absent")  
        self.absent(votes)
    
    def count_score(self, member_votes):
        """"""
        c = Counter(getattr(member,'vote') for member in member_votes)
        # print(c)
        for attr in c:
            # print(c[attr])
            if attr != "Frånvarande":
                self.add_to_highscore_table(attr,c[attr], member_votes[0].member_id)

    def absent(self, votes):
        bill_ids = [vote.bill_id for vote in votes]
        bills = self.session.query(BillsTable).filter(BillsTable.id.in_(bill_ids)).all()
        sorted_bills = sorted(bills,key=lambda bill: (bill.date, bill.point))
        member_id = votes[0].member_id
        streaks = []
        streak = {"type": "", "count": 0, "start": "", "end": ""}
        
        seen_dates = set()
        bill_dates = [bill for bill in sorted_bills if bill.date not in seen_dates and not seen_dates.add(bill.date)]
        missed_count = 0
        absent_days = 0
        
        for date in bill_dates:
            matching_bills = [bill for bill in bills if bill.date == date.date]
            
            votes_for_date = [vote for vote in votes if any(bill.id == vote.bill_id for bill in matching_bills)]
            c = Counter(getattr(member,'vote') for member in votes_for_date)
            if len(c) != 1 or c["Frånvarande"] == 0:
                #start new streak
                if streak["type"] != "":
                    streak["end"] = date.date
                    streak["count"] = get_days(streak["start"],streak["end"])
                    streaks.append(streak)
                streak = {"type": "", "count": 0, "start": "", "end": ""}
            else: 
                # Continue current streak
                streak["type"] = "Frånvarande"
                streak["count"] = streak["count"] + 1
                if streak["start"] == "":
                    streak["start"] = date.date

            if len(c) == 1 and c["Frånvarande"] != 0:
                # print(c)
                absent_days+= 1
                # print("I have been absent: " + str(absent_days) + " days.")
            if len(c) > 1 and c["Frånvarande"] != 0:
                # print(c)
                missed_count+=1
        
        filtered_streaks = [streak for streak in streaks if streak["count"] > 1]
        sorted_streak = sorted(filtered_streaks, key=lambda streak: streak["count"], reverse=True)
        for streak in sorted_streak:
            self.add_to_streak_table(streak["type"],streak["count"],streak["start"],streak["end"],member_id)
        
        self.add_to_highscore_table("missed", missed_count, member_id)
        self.add_to_highscore_table("Frånvarande", absent_days, member_id)
        
    def add_to_highscore_table(self, type, count,member_id):
        """"""
        highscore = HighscoreTable(highscore_type=type, highscore_value=count,member_id=member_id)
        self.session.add(highscore)
        self.session.commit()

    def add_to_streak_table(self, type, count, start_date, end_date,member_id):
        """"""
        start_time = datetime.strptime(start_date.split(" ")[0], "%Y-%m-%d")
        end_time = datetime.strptime(end_date.split(" ")[0], "%Y-%m-%d")
        streak = StreakTable(highscore_type=type, streak_value=count,start_date=start_time,end_date=end_time,member_id=member_id)
        self.session.add(streak)
        self.session.commit()

    def update_member(self, first_seen, last_seen, member_id):
        self.session.query(MembersTable).filter(MembersTable.id == member_id).update({
            "first_seen":first_seen,
            "last_seen":last_seen
        })
        self.session.commit()
    
    def when_seen(self, member_votes):
        """
        """
        bill_ids = [vote.bill_id for vote in member_votes]
        bills = session.query(BillsTable).filter(BillsTable.id.in_(bill_ids)).all()
        
        first_seen = bills[0].date
        last_seen  = bills[0].date
        member_id = member_votes[0].member_id
        
        for bill in bills:
            if first_seen == "":
                first_seen = bill.date
            if last_seen == "":
                last_seen = bill.date
                
            if first_seen > bill.date:
                first_seen = bill.date
            if last_seen < bill.date:
                last_seen = bill.date
        self.update_member(first_seen,last_seen,member_id)

