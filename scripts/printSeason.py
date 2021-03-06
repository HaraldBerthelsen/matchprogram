#tre olika sätt (eller fler?)
#1) matchstatistik - csv med samma som season.csv men förenklad
#2) spelarstatistik - mål, kort, speltid osv
#3) matchinfo årskrönikan, laguppställning, mål båda lagen, byten..

import sys, re
import csv


firstplayer = 15
stopdate = "30/5"

def readCsvFile(csvfile):
    season = []
    with open(csvfile, newline='') as fh:
        reader = csv.DictReader(fh, delimiter='\t')
        for row in reader:
            season.append(row)

    for match in season:
        #print(match["Typ"])
        if match["Typ"] == "OBOS Damallsvenskan":
            match["Typ"] = "Allsvenskan"
    return season

def printMatchStatistics(season):
    fieldnames = ["Typ","Datum","Motståndare", "Resultat", "Publik (bortalag)"]
    players = list(season[0].keys())[firstplayer:]
    fieldnames.extend(players)
    print("\t".join(fieldnames))
    for match in season:
        row = []
        row.append(match['Typ'])
        row.append(match['Datum'])
        row.append(match['Motståndare'])
        row.append(match['HIF']+"-"+match['Inte HIF'])

        publik = match['Publik']
        if publik == "":
            publik = 0
        bortapublik = match['Publik bortalag']
        if bortapublik == "":
            bortapublik = 0        
        row.append(f"{publik} ({bortapublik})")
        
        for playerinfo in list(match.keys())[firstplayer:]:
            row.append(getMatchStatisticsPlayerInfo(match[playerinfo]))
        print("\t".join(row))

        if match["Datum"] == stopdate:
            sys.exit()

        
def getMatchStatisticsPlayerInfo(playerinfo):
    #if "G" in playerinfo:
    #    print(playerinfo)
    lineup = "-"
    goals = 0
    yellow = 0
    red = ""


    if playerinfo == "B":
        #På bänken hela matchen
        lineup = "B"
    else:
        for info in playerinfo.split("-"):
            #if "G" in playerinfo:
            #    print(info)
            if info.startswith("S"):
                lineup = "S"
            elif info.startswith("U"):
                lineup = "U"
            elif info.startswith("I"):
                lineup = "I"
            elif info.startswith("G"):
                goals += 1
            elif info.startswith("Y"):
                yellow += 1
            elif info.startswith("R"):
                red = "R"

    if yellow == 2:
        red = "R"
        yellow = ""
    elif yellow == 1:
        yellow = "G"
    elif yellow == 0:
        yellow = ""

    if goals == 0:
        goals = ""


    playerinfo = f"{lineup}{goals}{yellow}{red}"
    #print(playerinfo)
    #sys.exit()
    return playerinfo

    

def printPlayerStatistics(season, type=None):
    print("Spelare\tMatcher\tMål\tAssist\tMinuter\tRöda\tGula")
    match = season[0]
    for player in list(match.keys())[firstplayer:]:
        row = []

        row.append(player)        
        row.append(getNrMatches(player,season, type))
        row.append(getNrGoals(player,season, type))
        row.append(getNrAssists(player,season, type))
        row.append(getPlayedMinutes(player,season, type))        
        row.append(getNrCards("Y",player,season, type))
        row.append(getNrCards("R",player,season, type))

        print("\t".join(row))

def getNrMatches(player, season, type=None):
    matches = 0
    for match in season:
        if type == None or match["Typ"] == type:
            playerinfo = match[player]
            if "S" in playerinfo:
                matches += 1
            elif "I" in playerinfo:
                matches += 1
            elif "U" in playerinfo:
                matches += 1
    return str(matches)


def getPlayedMinutes(player, season, type=None):
    minutes = 0
    for match in season:

        playedtime = 90
        if "Speltid" in match and match["Speltid"] != "":
            playedtime = int(match["Speltid"])

        if type == None or match["Typ"] == type:
            playerinfo = match[player]
            #print(playerinfo)
            for info in playerinfo.split("-"):
                if "S" in info:
                    minutes += playedtime
                elif "U" in info:
                    m = re.match("U\(([0-9+]+)[ab]?\)", info)
                    time = m.group(1)
                    if "+" in time:
                        (t1,t2) = time.split("+")
                        time = int(t1)+int(t2)
                        if time > playedtime:
                            time = playedtime
                    minutes += int(time)
                elif "I" in info:
                    m = re.match("I\(([0-9+]+)[ab]?\)", info)
                    time = m.group(1)
                    if "+" in time:
                        (t1,t2) = time.split("+")
                        time = int(t1)+int(t2)
                        if time > playedtime:
                            time = playedtime-1
                    minutes += playedtime-int(time)
    return str(minutes)


def getNrGoals(player, season, type=None):
    goals = 0
    for match in season:
        if type == None or match["Typ"] == type:
            playerinfo = match[player]
            for info in playerinfo.split("-"):
                if "G" in info:
                    goals += 1
    return str(goals)

def getNrAssists(player, season, type=None):
    assists = 0
    for match in season:
        if type == None or match["Typ"] == type:
            playerinfo = match[player]
            for info in playerinfo.split("-"):
                if "P" in info:
                    assists += 1
    return str(assists)

def getNrCards(colour, player, season, type=None):
    cards = 0
    for match in season:
        if type == None or match["Typ"] == type:
            playerinfo = match[player]
            for info in playerinfo.split("-"):
                if colour in info:
                    cards += 1
    return str(cards)


def printMatchInfo(season, type=None):
    for match in season:
        if type != None and match["Typ"] != type:
            continue
        arena = match["Plats"]
        referee = match["Domare"]
        date = match["Datum"]
        time = match["Tid"]
        attendance = match["Publik"]
        if arena in ["Söderstadion","Hammarby IP"] and match["Kommentar"] != "DIF hemma":
            home = "Hammarby"
            away = match["Motståndare"]
            homeresult = match["HIF"]
            awayresult = match["Inte HIF"]
            homehalftime = match["Halvtid HIF"]
            awayhalftime = match["Halvtid inte HIF"]
            opponent_goals = getOppGoals(match["Händelser motståndare"], "A")
            hif_goals = getHifGoals(match, "H")
        else:
            home = match["Motståndare"]
            away = "Hammarby"
            homeresult = match["Inte HIF"]
            awayresult = match["HIF"]
            homehalftime = match["Halvtid inte HIF"]
            awayhalftime = match["Halvtid HIF"]
            opponent_goals = getOppGoals(match["Händelser motståndare"], "H")
            hif_goals = getHifGoals(match, "A")


        out = f"""
{date} {time}, {arena}: 
{home}-{away} {homeresult}-{awayresult} ({homehalftime}-{awayhalftime})
Domare: {referee}, Publik: {attendance}
"""
        print(out)
        #print(opponent_goals)
        #print(hif_goals)

        goals = {**hif_goals, **opponent_goals}
        h = 0
        a = 0
        for time in sorted(goals.keys()):
            (goaltype, player, comment, home_away, assist) = goals[time]
            if comment == ",str":
                comment = " (straff)"
            if comment.startswith("+"):
                time = f"{time}{comment}"
                comment = ""
            if home_away == "H":
                h += 1
            else:
                a += 1
            if assist == None:
                assist = ""
            else:
                assist = "("+assist+")"
            print(f"{h}-{a} ({time}) {player}{comment} {assist}") 

        print()
        try:
            lineup = getLineup(match)
        except:
            continue
        print(lineup)
            
        if date == stopdate:
            sys.exit()

def getOppGoals(opp_events, home_away):
    goals = {}
    for info in opp_events.split("-"):
        #print(info)
        m = re.match("(O?G)\(([0-9]+),([^,\)]+)(,?[^,\)]*)\)", info)
        if m:
            goaltype = m.group(1)
            time = int(m.group(2))
            lastname = m.group(3)
            comment = m.group(4)
            home_away_this_goal = home_away
            if goaltype == "OG":
                if home_away == "H":
                    home_away_this_goal = "A"
                elif home_away == "A":
                    home_away_this_goal = "H"
            goals[time] = (goaltype, lastname, comment, home_away_this_goal, None)
    return goals
            
def getHifGoals(match, home_away):    
    goals = {}
    for player in list(match.keys())[firstplayer:]:
        #print(player)
        playerinfo = match[player].split("-")
        #print(playerinfo)
        for info in playerinfo:
            #print(info)
            m = re.match("(O?G)\(([0-9]+)(,?[^,\)]*)\)", info)
            if m:
                goaltype = m.group(1)
                time = int(m.group(2))
                lastname = player.split(" ")[-1]
                comment = m.group(3)
                home_away_this_goal = home_away
                if goaltype == "OG":
                    comment = " (självmål)"
                    if home_away == "H":
                        home_away_this_goal = "A"
                    elif home_away == "A":
                        home_away_this_goal = "H"
                goals[time] = [goaltype, lastname, comment, home_away_this_goal, None]

    #Find assist
    for player in list(match.keys())[firstplayer:]:
        #print(player)
        playerinfo = match[player].split("-")
        #print(playerinfo)
        for info in playerinfo:
            #print(info)
            m = re.match("P\(([0-9]+)(,?[^,\)]*)\)", info)
            if m:
                time = int(m.group(1))
                lastname = player.split(" ")[-1]
                comment = m.group(2)
                goals[time][4] = lastname+comment


                

    return goals

def getLineup(match):
    fields = {"B":{}, "M":{}, "A":{}}

    for player in list(match.keys())[firstplayer:]:
        #print(player)
        playerinfo = match[player].split("-")
        #print(playerinfo)
        for info in playerinfo:
            #print(info)
            if info == "K":
                fields["K"] = " ".join(player.split(" ")[1:])

            else:
                m = re.match("([BMA])([0-9])", info)
                if m:
                    field = m.group(1)
                    nr = int(m.group(2))
                    printplayer = " ".join(player.split(" ")[1:])
                    fields[field][nr] = printplayer
                    if "U" in match[player]:
                        #print(match[player])
                        m = re.search("U\(([0-9][0-9][ab]?)\)", match[player])
                        subtime = m.group(1)
                        for player2 in list(match.keys())[firstplayer:]:
                            if f"I({subtime})" in match[player2]:
                                if subtime.endswith("a"):
                                    printsubtime = subtime[:-1]
                                elif subtime.endswith("b"):
                                    printsubtime = subtime[:-1]
                                else:
                                    printsubtime = subtime
                                printplayer2 = " ".join(player2.split(" ")[1:])
                                fields[field][nr] += f" ({printplayer2}, {printsubtime})"

                                           

    lineup = []
    lineup.append(fields["K"])
    for field in ["B","M","A"]:
        fieldlist = []
        for pos in sorted(fields[field].keys()):
            fieldlist.append(fields[field][pos])
        lineup.append(", ".join(fieldlist))
    return "\n".join(lineup)


        
if __name__ == "__main__":
    match = False
    player = False
    info = False
    if "-m" in sys.argv:
        match = True
        sys.argv.remove("-m")
    if "-p" in sys.argv:
        player = True
        sys.argv.remove("-p")
    if "-i" in sys.argv:
        info = True
        sys.argv.remove("-i")
        
    csvfile = sys.argv[1]
    season = readCsvFile(csvfile)
    if match:
        printMatchStatistics(season)
    if player:
        printPlayerStatistics(season, type="Allsvenskan")
        #printPlayerStatistics(season)
    if info:
        printMatchInfo(season, type="Allsvenskan")
        #printMatchInfo(season)
    
