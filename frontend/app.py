from flask import Flask, render_template, g,request, jsonify
from flask_graphql import GraphQLView as View
from database import db_session
from graph_ql.schema import schema

import sqlite3

app = Flask(__name__)
app.debug = True
app.add_url_rule("/graph", view_func=View.as_view("graphql", graphiql=True, schema=schema))

DATABASE = '../db/db.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connetion(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/", methods=["GET", "POST"])
def main():
    """main route"""
    if request.method == "POST":
        data_type = request.json.get('data_type')
        if data_type == "bills":
            year = request.json.get('year')
            query = f'''query {{ getBills(year: "{year}") {{ id, name, report }} }}'''
            result = schema.execute(query)
            bills = result.data['getBills']
            return jsonify(bills)
        elif data_type == "bill_report":
            bill_report = request.json.get('bill_report')
            year = request.json.get('year')
            query = f'''
                query {{ getBills(report: "{bill_report}", year: "{year}") {{ id, point }} }}
            '''
            result = schema.execute(query)
            
            sub_bills = result.data['getBills']
            return jsonify(sub_bills)
        elif data_type == "votes":
            bill_id = request.json.get('bill_id')
            query = f'''
                query {{ 
                    getBills(id: {bill_id}) {{
                        date
                        name
                        report
                        votes {{
                            vote
                            member {{
                                name
                                party
                                placement
                            }}
                        }}
                    }}
                }}
            '''
            result = schema.execute(query)
            return jsonify(result.data['getBills'][0])

    query = '''
        query { getBills(id: 1)  {
                        date
                        name
                        report
                        votes {
                            vote
                            member {
                                name
                                party
                                placement
                            }
                        }
                    }
                }
    '''
    bills = schema.execute(query)

    years = list(range(2003, 2024))
    years.sort(reverse=True)

    return render_template("index.html", years=years,data=bills.data["getBills"][0])

@app.route('/representative/<int:rep_id>')
def show_representative(rep_id):
    """
    """

    query = f'''query {{getMembers(id: {rep_id}) {{
            id
            name
            party
            placement
            firstSeen
            lastSeen
            votes {{
                vote
                bill {{
                    name
                    report
                    point
                    date
                }}
            }}
            }}
        }}'''
    member = schema.execute(query)

    return render_template("member.html", member=member.data["getMembers"][0])

    
@app.route('/highscore', methods=["GET", "POST"])
def show_highscore():
    """
    """
    hs_type = "Ja"
    if request.method == "POST":
        """"""
        hs_type = request.json.get('type')
        if hs_type != "streak":
            query = f'''
                {{ 
                    getHighscoreType(highscoreType:"{hs_type}"){{
                        highscoreType
                        highscoreValue
                            member {{
                                name
                                party
                                placement
                                firstSeen
                                lastSeen
                        }}
                    }}
                }}
            '''
            highscore = schema.execute(query)
            highscore = highscore.data['getHighscoreType']
        else: 
            query = f'''
                {{ 
                    getStreak {{
                        highscoreType
                        streakValue
                        startDate
                        endDate
                        member {{
                            name
                            party
                            placement
                            firstSeen
                            lastSeen
                        }}
                    }}
                }}
            '''
            highscore = schema.execute(query)
            highscore = highscore.data['getStreak']
        return jsonify(highscore)
    else:   
        query = f'''
            {{ 
                getHighscoreType(highscoreType:"{hs_type}"){{
                    highscoreType
                    highscoreValue
                        member {{
                            name
                            party
                            placement
                            firstSeen
                            lastSeen
                        }}
                    }}
                }}
        '''
        highscore = schema.execute(query)

    return render_template("highscore.html", highscore=highscore.data["getHighscoreType"])    


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def internal_server_error(e):
    """internal server error"""
    return "<p>Flask500<pre>" + traceback.format_exc()

if __name__ == "__main__":
    app.run(debug=True)