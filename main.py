from bs4 import BeautifulSoup
import requests
import re 
import json
import time
import sqlite3
import dateparser

def main():
    # https://data.riksdagen.se/voteringlista/?rm=2023%2F24&rm=2022%2F23&bet=&punkt=&valkrets=&rost=&iid=0327372175911&sz=10000&utformat=HTML&gruppering=
    # scrape info
    url = "https://data.riksdagen.se/voteringlista/?rm=2023%2F24&rm=2022%2F23&bet=&punkt=&valkrets=&rost=&iid=0327372175911&sz=10000&utformat=HTML&gruppering="
    # Åkesson https://data.riksdagen.se/voteringlista/?rm=2021%2F22&rm=2020%2F21&rm=2019%2F20&rm=2018%2F19&rm=2017%2F18&rm=2016%2F17&rm=2015%2F16&rm=2014%2F15&rm=2013%2F14&rm=2012%2F13&rm=2011%2F12&rm=2010%2F11&bet=&punkt=&valkrets=&rost=&iid=051207517226&sz=10000&utformat=HTML&gruppering=
    # Ohly https://data.riksdagen.se/voteringlista/?rm=2009%2F10&rm=2008%2F09&rm=2007%2F08&rm=2006%2F07&rm=2005%2F06&rm=2004%2F05&rm=2003%2F04&rm=2002%2F03&bet=&punkt=&valkrets=&rost=&iid=0371688419616&sz=10000&utformat=HTML&gruppering=
    urls = ["https://data.riksdagen.se/voteringlista/?rm=2023%2F24&rm=2022%2F23&bet=&punkt=&valkrets=&rost=&iid=0327372175911&sz=10000&utformat=HTML&gruppering=", "https://data.riksdagen.se/voteringlista/?rm=2021%2F22&rm=2020%2F21&rm=2019%2F20&rm=2018%2F19&rm=2017%2F18&rm=2016%2F17&rm=2015%2F16&rm=2014%2F15&rm=2013%2F14&rm=2012%2F13&rm=2011%2F12&rm=2010%2F11&bet=&punkt=&valkrets=&rost=&iid=051207517226&sz=10000&utformat=HTML&gruppering=", "https://data.riksdagen.se/voteringlista/?rm=2009%2F10&rm=2008%2F09&rm=2007%2F08&rm=2006%2F07&rm=2005%2F06&rm=2004%2F05&rm=2003%2F04&rm=2002%2F03&bet=&punkt=&valkrets=&rost=&iid=0371688419616&sz=10000&utformat=HTML&gruppering="]
    url_idx = 1
    url_len = len(urls)
    # start = False
    # start2 = False
    failed_links = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sections = soup.find_all("li")
        idx = 1
        total = len(sections)

        
        for section in sections:
                
            print(f"Url {url_idx}/{url_len} | Bill number {idx}/{total}")

            links = section.find_all("a")

            bill_name, bill_date, success = get_bill_data(links[0]['href'])
            voting_data = get_voting_data(links[1]['href'])
            # print(section)
            if success:
                bill_id = insert_bill((bill_name, links[1].text.split("votering punkt")[1], bill_date, links[0].text))
                # print(bill_id)
                # print(type(bill_id))
                if bill_id == -1:
                    print("bill already exists")
                else:
                    print("bill doesn't exist")
                    for member in voting_data:
                        member_id = member_to_db(member)
                        connect_member_to_bill(bill_id, member_id, member["vote"])
            else: 
                print(f"fails {links[0]['href']}")
                failed_links.append(links[0]['href'])

            print("----------------------------------------------------------------------")
            idx+=1
        url_idx+=1
    print(failed_links)

def connect_member_to_bill(bill_id, member_id, vote):
    """
    """
    try:
        sqliteConnection = sqlite3.connect('db/db.db')
        cursor = sqliteConnection.cursor()
        
        sqlite_get_query = """SELECT * FROM votes WHERE bill_id = ? AND member_id = ?"""
        cursor.execute(sqlite_get_query, (bill_id, member_id))
        record = cursor.fetchone()
        
        print(record)
        print(record == None)
        if record == None:
            print("insert time")
            sql_insert_query = """INSERT INTO votes (member_id, bill_id, vote) VALUES (?,?,?)""" 
            cursor.execute(sql_insert_query, (member_id, bill_id, vote))
            sqliteConnection.commit()
            
    except sqlite3.Error as error:
        print(error)

def insert_bill(bill): 
    _id = -1
    # print(bill)
    try: 
        sqliteConnection = sqlite3.connect('db/db.db')
        cursor = sqliteConnection.cursor()
        sqlite_get_query = """SELECT * FROM bills WHERE name = ? AND point = ? AND report = ?"""
        
        cursor.execute(sqlite_get_query, (bill[0], bill[1], bill[3]))
        record = cursor.fetchone()
        # print(record)
        if record == None:
            cursor = sqliteConnection.cursor()
            sqlite_insert_query = """INSERT INTO bills
                            (name, point, date, report) 
                            VALUES (?, ?,?,?);"""
            cursor_used = cursor.execute(sqlite_insert_query, bill)
            sqliteConnection.commit()
            _id = cursor_used.lastrowid

        else: 
            # If bill exists set its id.
            print("already exists")
            # _id = record[0]
            _id = -1
            # _id = "-1"

        cursor.close()
    except sqlite3.Error as error:
        print(error)
    return _id

def member_to_db(member):
    # print(member)
    _id = -1
    try: 
        sqliteConnection = sqlite3.connect('db/db.db')
        cursor = sqliteConnection.cursor()
        sqlite_get_query = """SELECT * FROM members WHERE name = ? AND party = ? AND placement = ?"""
        
        cursor.execute(sqlite_get_query, (member["name"], member["party"], member["place"]))
        record = cursor.fetchone()
        # print(record)
        if record == None:
            sqlite_insert_query = """INSERT INTO members
                            (name, placement, party) 
                            VALUES (?, ?,?);"""
            cursor_used = cursor.execute(sqlite_insert_query, (member["name"], member["place"],member["party"] ))
            sqliteConnection.commit()
            _id = cursor_used.lastrowid

        else: 
            _id = record[0]
            # print("I already exist!")
        cursor.close()
    except sqlite3.Error as error:
        print(error)

    return _id
    
def get_bill_data(url):
    """
    """
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        text = soup.find_all("span", attrs={'class': "fBeuvH"})[0]
        sections = soup.find_all("a", attrs={'class': "dbpaZU"})
        # date = "2024-01-02"
        # print(sections)
        # for section in sections:
        # print(sections[0]["href"])
        print(sections[0]["href"])
        response = requests.get(sections[0]["href"])
        soup = BeautifulSoup(response.text, 'html.parser')
        div  = soup.find_all("div", attrs={"class": "iWbaWS"})
        # print(div)
        if div == []:
            print("i'm here")
            div = soup.find_all("p", attrs={'class': "iYqHMa"})
            # print(div[0].text)
            split_string = div[0].text.split(" kl. ")
            # print()
            date = split_string[0][len(split_string) - 12:]
        else: 
            date = div[0].find_all("dd")[0].text
            # print(url)
            # print(date)
        return (text.text, date, True) 
    except:
        return ("", "", False)
def get_voting_data(url):
    """"""
    voting_data = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sections = soup.find_all("tr")
    idx = 1
    for section in sections: 
        # print(section)
        voter = {"place": idx, "vote": "", "party": "", "name":""}
        
        td = section.find_all("td")
        # print(td)
        if td != []:
            voter["vote"] = td[2].text
            voter["party"] = td[1].text
            voter["name"] = td[0].text
            voting_data.append(voter)
            idx+=1  
    # print(voting_data)
    return voting_data

def fix_dates():
    try: 
        sqliteConnection = sqlite3.connect('db/db.db')
        cursor = sqliteConnection.cursor()
        sqlite_get_query = """SELECT date, id FROM bills"""
        cursor.execute(sqlite_get_query)
        
        records = cursor.fetchall()
        # print(len(records))
        for record in records:
            # print(record)
            try:
                parsed = dateparser.parse(record[0])
                # insert into sql
                # print(parsed)
                update_query = """UPDATE bills SET date = ? WHERE id = ?"""
                cursor.execute(update_query, (parsed, record[1]))
                sqliteConnection.commit()

            except sqlite3.Error as error:
                print(f"could not parse on id: {record[1]}")
                print(f"{error}")
    except sqlite3.Error as error:
        print(error)
    
if __name__ == "__main__":
    main()
    fix_dates()