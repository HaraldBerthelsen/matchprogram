#tre olika sätt (eller fler?)
#1) matchstatistik - csv med samma som season.csv men förenklad
#2) spelarstatistik - mål, kort, speltid osv
#3) matchinfo årskrönikan, laguppställning, mål båda lagen, byten..

import sys, re
import csv


firstplayer = 14

def readCsvFile(csvfile):
    season = []
    with open(csvfile, newline='') as fh:
        reader = csv.DictReader(fh, delimiter='\t')
        for row in reader:
            season.append(row)
    return season

def printMatchStatistics(season):
    fieldnames = ["Typ","Datum","Motståndare", "HIF", "Inte HIF"]
    players = list(season[0].keys())[firstplayer:]
    fieldnames.extend(players)
    print("\t".join(fieldnames))
    for match in season:
        row = []
        row.append(match['Typ'])
        row.append(match['Datum'])
        row.append(match['Motståndare'])
        row.append(match['HIF'])
        row.append(match['Inte HIF'])
        for playerinfo in list(match.keys())[firstplayer:]:
            row.append(getMatchStatisticsPlayerInfo(match[playerinfo]))
        print("\t".join(row))

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
    match = season[0]
    for player in list(match.keys())[firstplayer:]:
        row = []

        row.append(player)        
        row.append(getNrMatches(player,season, type))
        row.append(getNrGoals(player,season, type))
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
                    m = re.match("U\(([0-9+]+)a?\)", info)
                    time = m.group(1)
                    if "+" in time:
                        (t1,t2) = time.split("+")
                        time = int(t1)+int(t2)
                        if time > playedtime:
                            time = playedtime
                    minutes += int(time)
                elif "I" in info:
                    m = re.match("I\(([0-9+]+)a?\)", info)
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

def getNrCards(colour, player, season, type=None):
    cards = 0
    for match in season:
        if type == None or match["Typ"] == type:
            playerinfo = match[player]
            for info in playerinfo.split("-"):
                if colour in info:
                    cards += 1
    return str(cards)

        
if __name__ == "__main__":
    csvfile = sys.argv[1]
    season = readCsvFile(csvfile)
    printMatchStatistics(season)
    #printPlayerStatistics(season, type="Allsvenskan")
    printPlayerStatistics(season)
    #printMatchInfo(season)
    
