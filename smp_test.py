# -*- coding: utf-8 -*-
import sys, re, json, urllib2
from bs4 import BeautifulSoup


class Season(object):

    def __init__(self, year, matches):
        self.year = year 
        #sf_name : smp_name
        self.teams = {
            "Halmstad":"Halmstad BK",
            "Hammarby":"Hammarby IF"
        }
        self.matches = matches

    def loadFromSF(self):
        for matchid in self.matches:
            match = Match(matchid)
            match.loadFromSF()

    def saveJson(self, filename):
        fh = open(filename)
        fh.write(json.dumps(self))
        fh.close()


    def loadJson(self, filename):
        fh = open(filename)
        self = json.loads(fh.read())
        fh.close()

    
    def writeToFile(self, filename):
        pass
    
        
class Match(object):
    def __init__(self, nr, matchid):
        self.nr = nr
        self.matchid = matchid
        #home 
        #away 
        #date
        #arena
        #referee
        #linesmen
        #assistant referee
        #attendance
        #attendance_away
        #home_lineup
        #home_subs
        #away_lineup
        #away_subs

    def loadFromSF(self):
        url = "http://svenskfotboll.se/allsvenskan/information/?scr=result&fmid=%d" % self.matchid
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page, "lxml")

        game_info = soup.find("div", attrs={"class":"game-info-page"})

        (self.date, self.arena, self.referee, self.spectators, self.spectators_away) = getMatchInfo(game_info)

        (self.home_score, self.away_score) = getScore(game_info)

        self.players = getPlayers(game_info)


    
    def printForSMP(self):
        pass
    
class Player(object):
    def __init__(self, nr, name, playerid):
        self.nr = nr
        self.name = name
        self.playerid = playerid
        #position
        #citizenship
        #birth_date
        #length
        #weight
        #club_origin
        #total_matches
        #total_goals
        #match_stats
        #season_stats
        #total_stats

    def loadFromSF(self):
        pass

    def loadJson(self, filename):
        pass

    def saveJson(self, filename):
        pass

    def printForSMP(self):
        pass

class PlayerStats(object):
    def __init__(self, playerid):
        self.playerid = playerid
        self.stats = {}

    def getStat(self, stat):
        if stat in self.stats:
            return self.stats[stat]
        else:
            return None

    def setStat(self, stat, value):
        self.stats[stat] = value

    def loadJson(self, filename):
        pass

    def saveJson(self, filename):
        pass
    
    def printForSMP(self):
        pass

def getMatchInfo(game_info):
    #Match
    date = game_info.find("div", attrs={"class":"start-time"}).span.text.strip() 
    arena = game_info.find("div", attrs={"class":"stadium"}).span.text.strip()
    referee = game_info.find("div", attrs={"class":"referee"}).span.text.strip()
    
    try:
        spectators = game_info.find("div", attrs={"class":"spectators"}).span.text.strip()
    except:
        spectators = "-"
    try:
        spectators_away = game_info.find("div", attrs={"class":"spectators-away"}).span.text.strip()  #Finns den här informationen någonstans?
    except:
        spectators_away = "-"
            
            
    home_team = game_info.find("div", attrs={"class":"home"}).find("span", attrs={"class":"name"}).text
    away_team = game_info.find("div", attrs={"class":"away"}).find("span", attrs={"class":"name"}).text

    return (date, arena, referee, spectators, spectators_away, home_team, away_team)


def getScore(game_info):
    scoreboard = game_info.find("div", attrs={"class":"scoreboard"})
    score = scoreboard.find_all("span")
    home_score = score[0].text.strip()
    away_score = score[1].text.strip()
    return (home_score, away_score)


def getPlayers(game_info):
    try:
        home_goals = game_info.find("div", attrs={"class":"home"}).find("ul", attrs={"class":"goals"}).find_all("li")
    except:
        home_goals = []

    for home_goal in home_goals:
        time = home_goal.find("span", attrs={"class":"time"}).text
        player = home_goal.a.text
        #print("%s\t%s" % (time,player))


    try:
        home_squad = game_info.find("div", attrs={"class":"hometeam-squad"}).find_all("ul")
        lineup = home_squad[0].find_all("li")
        subs = home_squad[1].find_all("li")
    except:
        lineup = []
        subs = []

    players = {}
    for player in lineup:
        number = int(re.sub(".\s*$", "", player.find("span", attrs={"class":"number"}).text))
        name = player.find("span", attrs={"class":"name"}).text
        goals = len(player.find_all("span",attrs={"data-symbol":"goal"}))
        if player.find("span",attrs={"data-symbol":"sub-out"}):
            sub_out = True
        else:
            sub_out = False
        players[number] = {"name":name, "start":True, "goals":goals, "sub_out":sub_out, "sub_in":False}

    for player in subs:
        number = int(re.sub(".\s*$", "", player.find("span", attrs={"class":"number"}).text))
        name = player.find("span", attrs={"class":"name"}).text
        goals = len(player.find_all("span",attrs={"data-symbol":"goal"}))
        if player.find("span",attrs={"data-symbol":"sub-in"}):
            sub_in = True
        else:
            sub_in = False
        players[number] = {"name":name, "start":False,"goals":goals, "sub_out":False, "sub_in":sub_in}

    return players

#TODO
    
#testar med två matcher 2017
matches = [3491041, 3491183]
season = Season(2017, matches)
#sen med 2018
#matches = [3795745]
#season = new Season(2018, matches)

#season.loadFromSF()
#season.saveJson("season2017_test.json")
#season.loadJson("season2017_test.json")
#season.printForSmp()

def main_first_test():
    matchid = 3491041 #Hammarby-Djurgarden 2017
    #matchid = 3491183 #Hammarby-Halmstad 2017
    #matchid = 3795745 #Hammarby-Sirius 2018

    url = "http://svenskfotboll.se/allsvenskan/information/?scr=result&fmid=%d" % matchid

    page = urllib2.urlopen(url)

    soup = BeautifulSoup(page, "lxml")

    game_info = soup.find("div", attrs={"class":"game-info-page"})

    (date, arena, referee, spectators, spectators_away, home_team, away_team) = getMatchInfo(game_info)
    
    (home_score, away_score) = getScore(game_info)
    
    players = getPlayers(game_info)

    # #Match
    # date = game_info.find("div", attrs={"class":"start-time"}).span.text.strip() 
    # arena = game_info.find("div", attrs={"class":"stadium"}).span.text.strip()
    # referee = game_info.find("div", attrs={"class":"referee"}).span.text.strip()

    # try:
    #     spectators = game_info.find("div", attrs={"class":"spectators"}).span.text.strip()
    # except:
    #     spectators = "-"
    # try:
    #     spectators_away = game_info.find("div", attrs={"class":"spectators-away"}).span.text.strip()  #Finns den här informationen någonstans?
    # except:
    #     spectators_away = "-"


    # home_team = game_info.find("div", attrs={"class":"home"}).find("span", attrs={"class":"name"}).text
    # away_team = game_info.find("div", attrs={"class":"away"}).find("span", attrs={"class":"name"}).text



    # scoreboard = game_info.find("div", attrs={"class":"scoreboard"})
    # score = scoreboard.find_all("span")
    # home_score = score[0].text.strip()
    # away_score = score[1].text.strip()



    # try:
    #     home_goals = game_info.find("div", attrs={"class":"home"}).find("ul", attrs={"class":"goals"}).find_all("li")
    # except:
    #     home_goals = []

    # for home_goal in home_goals:
    #     time = home_goal.find("span", attrs={"class":"time"}).text
    #     player = home_goal.a.text
    #     #print("%s\t%s" % (time,player))


    # try:
    #     home_squad = game_info.find("div", attrs={"class":"hometeam-squad"}).find_all("ul")
    #     lineup = home_squad[0].find_all("li")
    #     subs = home_squad[1].find_all("li")
    # except:
    #     lineup = []
    #     subs = []

    # players = {}
    # for player in lineup:
    #     number = int(re.sub(".\s*$", "", player.find("span", attrs={"class":"number"}).text))
    #     name = player.find("span", attrs={"class":"name"}).text
    #     goals = len(player.find_all("span",attrs={"data-symbol":"goal"}))
    #     if player.find("span",attrs={"data-symbol":"sub-out"}):
    #         sub_out = True
    #     else:
    #         sub_out = False
    #     players[number] = {"name":name, "start":True, "goals":goals, "sub_out":sub_out, "sub_in":False}

    # for player in subs:
    #     number = int(re.sub(".\s*$", "", player.find("span", attrs={"class":"number"}).text))
    #     name = player.find("span", attrs={"class":"name"}).text
    #     goals = len(player.find_all("span",attrs={"data-symbol":"goal"}))
    #     if player.find("span",attrs={"data-symbol":"sub-in"}):
    #         sub_in = True
    #     else:
    #         sub_in = False
    #     players[number] = {"name":name, "start":False,"goals":goals, "sub_out":False, "sub_in":sub_in}




    #Utskrift:

    #1: Matchstatistik
    #datum d/m
    #motståndare, fetstil om hemma
    #resultat (bajen först? KOLLA) x-x
    #publik (bortasupportrar inom parentes - finns den infon?)
    #för varje spelare i nummerordning:
    #S grön prick, startelvan
    #I gul prick, inbytt
    #U ? prick, utbytt (? Inte med nu)
    #Siffra efter för antal mål
    #R rött kort
    #G gult kort (? inte med nu)

    #Det här har bara med utskriften att göra, spara inte informationen så här
    if home_team == "Hammarby":
        opponent = away_team
        bajen_is_home = True
    elif away_team == "Hammarby":
        opponent = home_team
        bajen_is_home = False
    else:
        print("knas: hemmalag - %s, bortalag - %s" % (home_team, away_team))
        sys.exit()

    if bajen_is_home:
        bajen_score = home_score
        opponent_score = away_score
    else:
        bajen_score = away_score
        opponent_score = home_score



    m = re.match("^[0-9]{4}-0?([1-9]+)-0?([1-9]+)", date)
    if m:
        month = m.group(1)
        day = m.group(2)
    date_to_print = "%s/%s" % (day, month)

    header_to_print = "datum\tmotståndare\tres\tåskådare" 
    match_stats_to_print = "%s\t%s\t%s-%s\t%s (%s)" % (date_to_print, opponent, bajen_score, opponent_score, spectators, spectators_away)

    player_stats_to_print = []
    for player in sorted(players):
        player_match_info = players[player]
        print("%s %s" % (player, player_match_info))

        info_to_print = ""
        if player_match_info["start"]:
            info_to_print = "S"
        if player_match_info["sub_in"]:
            info_to_print = "I"
        if player_match_info["sub_out"]:
            info_to_print = "U"


        if player_match_info["goals"] > 0:
            info_to_print = "%s%d" % (info_to_print, player_match_info["goals"])

        player_stats_to_print.append(info_to_print)
        header_to_print += "\t%d" % player

    print(header_to_print)
    print("%s\t%s" % (match_stats_to_print, "\t".join(player_stats_to_print)))


    #2: Spelarstatistik
    #Summerat alla matcher, för varje spelare i nummerordning:
    #matcher (mål) Räknas inbytt? KOLLA
    #skott
    #skott på mål
    #orsakat frispark
    #gula kort
    #röda kort
    #Obs finns mer info i spelarstatistiken, ta med allting och spara!
    #Finns detta summerat för varje spelare på svensk fotboll?

    #3: Spelarpres
    #Matcher totalt i bajen
    #mål totalt i bajen
    #Det är alla tävlingsmatcher? as, cup, internationella? KOLLA Finns den infon på svenskfotboll?


if __name__ == "__main__":
    main_first_test()
