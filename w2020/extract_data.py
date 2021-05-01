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

        #try:
        match_info = getMatchInfo(game)
        #except:
        #    print("ERROR: game %s" % game["href"])
        #    break
        season.append(match_info)
        #printMatchPlayerInfo(match_info["match_players"])

        squad = updateSquadInfo(squad, match_info["match_players"])
        
        #stop after first game for dev
        #break

    #printSeason(season, squad)
    printPlayerStats(season)
    printSeasonFormatted(season, squad)

    
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

            #Only players that played..
            if players[nr]["timePlayed"] == 0:
                continue

            if nr not in match["match_players"]:
                to_print.append("-")
            elif match["match_players"][nr]["sub"] in ["I", "U"]:
                #to_print.append("%s(%s)%s%s" % (match_players[nr]["sub"], match_players[nr]["sub_time"], match_players[nr]["goal"], match_players[nr]["yellow"]))
                to_print.append("%s(%s)%s%s" % (match["match_players"][nr]["sub"], match["match_players"][nr]["sub_time"], match["match_players"][nr]["goals"], match["match_players"][nr]["yellow"]))
            else:
                to_print.append("%s%s%s" % (match["match_players"][nr]["sub"], match["match_players"][nr]["goals"], match["match_players"][nr]["yellow"]))

        print("\t".join(to_print))
                            

def initials(fullname):
    ini = []
    names = fullname.split(" ")
    for name in names:
        ini.append(name[0])
    return "".join(ini)
        
def printSeasonFormatted(season, squad):

    print("%-20s\t%-20s\t%-25s\t%s\t%-10s" % ("Motståndare", "Tid", "Plats", "HIF", "Inte HIF"), end='\t')
    header = []
    for nr in sorted(squad.keys()):
        #Only players that played
        if players[nr]["timePlayed"] == 0:
            continue

        printnr = nr.split("-")[0]
        #Initials
        #header.append("%s %s" % (printnr, initials(squad[nr]["name"])))
        #Full name
        header.append("%s %s" % (printnr, squad[nr]["name"]))
    print("\t".join(header))
    
    for match in season:
        
        print("%-20s\t%-20s\t%-25s\t%s\t%-10s" % (match["opponent"], match["time"], match["location"], match["hif_score"], match["other_score"]), end='\t')

        to_print = []
        for nr in sorted(squad.keys()):
            printSubTime = False

            #Only players that played
            if players[nr]["timePlayed"] == 0:
                continue
            
            if nr not in match["match_players"]:
                to_print.append("-")
                
            elif printSubTime and match["match_players"][nr]["sub"] in ["I", "U"]:
                to_print.append("%s(%s)%s%s%s" % (match["match_players"][nr]["sub"], match["match_players"][nr]["sub_time"], match["match_players"][nr]["goals"], match["match_players"][nr]["yellow"], match["match_players"][nr]["red"]))
            else:
                to_print.append("%s%s%s%s" % (match["match_players"][nr]["sub"], match["match_players"][nr]["goals"], match["match_players"][nr]["yellow"], match["match_players"][nr]["red"]))

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

    #Korrigera "Okänd spelare" i Sunnanå-Hammarby
    if matchid == "4420269":
        sys.stderr.write("%s\n" % match_players.keys())
        for p in match_players.keys():
            if p.startswith("28"):
                raiza = match_players[p]
                raiza["sub"] = "I"
                raiza["sub_time"] = 74
                sys.stderr.write("%s\n" % raiza)

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

    #print(match_info)
    return match_info
    

def getPlayerInfo(player, sub=False):
    number = int(player.find("span", class_="formation-list-player__number").text.strip())
    name = player.find("a", class_="formation-list-player__link").text.strip()

    name = re.sub("\s+\(.+\)\s*$", "", name)
    
    if number == 26 and name == "Emma Westin":
        number = 21
    if number == 3 and name == "Ida Egegård":
        number = 4
    if number == 4 and name == "Moa Ekmyr Garpenbeck":
        number = 5


    
    #print("%s %s" % (number, name))
    #print("starting")
    if sub:
        sub = "B"
    else:
        sub = "S"

    sub_time = 0
    if player.find("use", attrs={"xlink:href": "#icon-substitution-out"}):
        sub = "U"
        sub_expr = player.find("span", class_="formation-list-player__substitution-text").text.strip()
        if "+" in sub_expr:
            sub_time = 89
        else:
            sub_time = int(sub_expr)
        #print("ut: %s" % out)

    if player.find("use", attrs={"xlink:href": "#icon-substitution-in"}):
        sub = "I"
        sub_expr = player.find("span", class_="formation-list-player__substitution-text").text.strip()
        if "+" in sub_expr:
            sub_time = 89
        else:
            sub_time = int(sub_expr)
        #print("ut: %s" % inn)

    yellow = ""
    if player.find("use", attrs={"xlink:href": "#icon-card-yellow"}):
        yellow = "G"
        #print("yellow")

    red = ""
    if player.find("use", attrs={"xlink:href": "#icon-card-red"}):
        red = "R"

    goals = ""
    goalicons = len(player.find_all("use", attrs={"xlink:href": "#icon-football"}))
    if goalicons > 0:
        goals = goalicons
        #print("goal")

        
    info = {
        "name": name,
        "sub": sub,
        "sub_time": sub_time,
        "goals": goals,
        "red": red,
        "yellow": yellow
    }

    return ("%02d-%s" % (number, name), info)


def printMatchPlayerInfo(match_players):
    for nr in match_players:
        #Only players that played
        if players[nr]["timePlayed"] == 0:
            continue

        print("%s\t%s" % (nr, match_players[nr]["sub"]))

        printnr = nr.split("-")[0]
        
        if match_players[nr]["sub"] in ["I", "U"]:
            print("%s\t%s\t%s(%s)%s%s" % (printnr, match_players[nr]["name"], match_players[nr]["sub"], match_players[nr]["sub_time"], match_players[nr]["goal"], match_players[nr]["yellow"]))
        else:
            print("%s\t%s\t%s%s%s" % (printnr, match_players[nr]["name"], match_players[nr]["sub"], match_players[nr]["goal"], match_players[nr]["yellow"])) 




def printPlayerStats(season):
     for match_info in season:
         #print(match_info)
         for nr in match_info["match_players"]:
             #update_info(player, match_info["total_time"])
             player = match_info["match_players"][nr]
             update_info(player, nr)
         #print(players[25])

     print_player_stats_by_number()

players = {}
def update_info(player, nr, match_time=90):
    #nr = player["number"]
    #if nr == 25:
    #    print(player)
    if nr in players:
        p = players[nr]
    else:
        #if type(p) == type(""):
        #first appearance if this player        
        p = {
            "name": player["name"],
            "nMatches": 0,
            "nGoals": 0,
            "nAssists": 0,
            "nShots": 0,
            "nYellow": 0,
            "nRed": 0,
            "timePlayed": 0
        }
        
    if player["sub"] in ["S", "I", "U"]:
            p["nMatches"] += 1 
    if "goals" in player and player["goals"] != "":
            p["nGoals"] += int(player["goals"])
    if "yellow" in player and player["yellow"] != "":
            p["nYellow"] += 1
    if "red" in player and player["red"] != "":
            p["nRed"] += 1

    if player["sub"] == "I":
        p["timePlayed"] += match_time-player["sub_time"]
    elif player["sub"] == "U":
        if player["sub_time"] > match_time:
            sys.stderr.write("UT: %s %s %s" % (player["name"], player["sub_time"], match_time))                                                  
        p["timePlayed"] += match_time-(match_time-player["sub_time"])
    elif player["sub"] == "S":
        p["timePlayed"] += match_time
            
    players[nr] = p

            
def print_player_stats_by_number():
    #print("nr                              namn	spel/mål assist	skott speltid gula kort röda kort")
    print("nr                              namn	spel/mål speltid gula kort röda kort")
    for nr in sorted(players):
        #Print only players that played :)
        if players[nr]["timePlayed"] == 0:
            continue            
        
        printnr = nr.split("-")[0]        
        #1	Johan Wiland	7/0	0	0	568	0	0
        #print("%s\t%30s\t%s/%s\t%s\t%s\t%s\t%s\t%s" % (printnr, players[nr]["name"], players[nr]["nMatches"], players[nr]["nGoals"], players[nr]["nAssists"], players[nr]["nShots"], players[nr]["timePlayed"], players[nr]["nYellow"], players[nr]["nRed"]))
        print("%s\t%30s\t%s/%s\t%s\t%s\t%s" % (printnr, players[nr]["name"], players[nr]["nMatches"], players[nr]["nGoals"], players[nr]["timePlayed"], players[nr]["nYellow"], players[nr]["nRed"]))


        
if __name__ == "__main__":
    main()
