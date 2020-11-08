import sys, os, re
from bs4 import BeautifulSoup

#http --download https://www.svenskfotboll.se/serier-cuper/spelprogram/elitettan-2020/82419/ -o matcher.html

def main():
    with open("matcher.html") as fh:
        html_doc = fh.read()

    data = BeautifulSoup(html_doc, 'html.parser')
    games = data.find_all(href=re.compile("hammarby-"))

    season = []
    squad = {}

    for game in games:

        try:
            match_info = getMatchInfo(game)
        except:
            break
        season.append(match_info)
        #printMatchPlayerInfo(match_info["match_players"])

        squad = updateSquadInfo(squad, match_info["match_players"])
        
        #stop after first game for dev
        #break

    printSeason(season, squad)

def updateSquadInfo(squad, match_info):
    for nr in match_info:
        if nr not in squad:
            squad[nr] = {"name": match_info[nr]["name"], "played": 0}

        squad[nr]["played"] += 1
        #squad[nr]["goals"] += match_info[nr]["goal"]
            
    

    return squad
    

def printSeason(season, squad):

    header = ["Motståndare", "Tid", "Plats", "HIF", "Inte HIF"]
    for nr in sorted(squad.keys()):
        header.append("%s %s" % (str(nr), squad[nr]["name"]))
    print("\t".join(header))
    
    for match in season:
        to_print = []
        to_print.append(match["opponent"]),
        to_print.append(match["time"]),
        to_print.append(match["location"]),
        to_print.append(match["hif_score"]),
        to_print.append(match["other_score"])

        for nr in sorted(squad.keys()):
            if nr not in match["match_players"]:
                to_print.append("-")
            else:
                to_print.append("%s%s%s" % (match["match_players"][nr]["sub"], match["match_players"][nr]["goals"], match["match_players"][nr]["yellow"]))

        print("\t".join(to_print))
                            


def getMatchInfo(game):
    #print(game['href'])

    
    matchid = re.sub("^.*/", "", game['href'])

    #print(matchid)

    if not os.path.exists("%s.html" % matchid):
        cmd = "http --download https://www.svenskfotboll.se/%s" % game['href']
        print(cmd)
        os.system(cmd)


    with open("%s.html" % matchid) as fh:
        html_match = fh.read()
    match_data = BeautifulSoup(html_match, 'html.parser')

    if "/hammarby-" in game['href']:
        homegame = True
    else:
        homegame=False
    #print(homegame)

    teams = match_data.find_all("span", class_="match-hero__name")
    for team in teams:
        if team.text != "Hammarby":
            other_team = team.text


    result = match_data.find_all("span", class_="match-hero__results")[0].text
    #print(result)
    (home_score, _, away_score) = result.split(" ")
    if homegame:
        hif_score = home_score
        other_score = away_score
    else:
        hif_score = away_score
        other_score = home_score


    location = match_data.find("p", class_="match-hero__location").text.strip()
    time = match_data.find("time").text.strip()
    
    #print("%s\t%s\t%s\t%s - %s" % (other_team, location, time, hif_score, other_score))

    squads = match_data.find_all("div", class_="match-formation__team")
    for squad in squads:
        if squad.find("h3", string="Hammarby"):
            hif = squad.find_all("ul", class_="formation-list__items")
            starting_players = hif[0]
            subs = hif[1]


    match_players = {}
    players = starting_players.find_all("div", class_="formation-list-player")
    for player in players:
        (nr, info) = getPlayerInfo(player)
        match_players[nr] = info
    players = subs.find_all("div", class_="formation-list-player")
    for player in players:
        (nr, info) = getPlayerInfo(player, sub=True)
        match_players[nr] = info

    match_info = {
        "id": matchid,
        "home": homegame,
        "opponent": other_team,
        "location": location,
        "time": time,
        "hif_score": hif_score,
        "other_score": other_score,
        "match_players": match_players
    }
            
    return match_info
    

def getPlayerInfo(player, sub=False):
    number = int(player.find("span", class_="formation-list-player__number").text.strip())
    name = player.find("a", class_="formation-list-player__link").text.strip()

    #print("%s %s" % (number, name))
    #print("starting")
    if sub:
        sub = "B"
    else:
        sub = "S"

    if player.find("use", attrs={"xlink:href": "#icon-substitution-out"}):
        sub = "U"
        out_time = player.find("span", class_="formation-list-player__substitution-text").text.strip()
        #print("ut: %s" % out)

    if player.find("use", attrs={"xlink:href": "#icon-substitution-in"}):
        sub = "I"
        in_time = player.find("span", class_="formation-list-player__substitution-text").text.strip()
        #print("ut: %s" % inn)

    yellow = ""
    if player.find("use", attrs={"xlink:href": "#icon-card-yellow"}):
        yellow = "G"
        #print("yellow")

    goals = ""
    goalicons = len(player.find_all("use", attrs={"xlink:href": "#icon-football"}))
    if goalicons > 0:
        goals = goalicons
        #print("goal")

        
    info = {
        "name": name,
        "sub": sub,
        "goals": goals,
        "yellow": yellow
    }

    return (number, info)


def printMatchPlayerInfo(match_players):
    for nr in match_players:
        print("%s\t%s\t%s%s%s" % (nr, match_players[nr]["name"], match_players[nr]["sub"], match_players[nr]["goal"], match_players[nr]["yellow"])) 



if __name__ == "__main__":
    main()
