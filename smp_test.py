# -*- coding: utf-8 -*-
import sys, re, urllib2
from bs4 import BeautifulSoup

matchid = 3491041 #Hammarby-Djurgarden 2017
#matchid = 3491183 #Hammarby-Halmstad 2017
#matchid = 3795745 #Hammarby-Sirius 2018

url = "http://svenskfotboll.se/allsvenskan/information/?scr=result&fmid=%d" % matchid

page = urllib2.urlopen(url)

soup = BeautifulSoup(page, "lxml")

game_info = soup.find("div", attrs={"class":"game-info-page"})


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



scoreboard = game_info.find("div", attrs={"class":"scoreboard"})
score = scoreboard.find_all("span")
home_score = score[0].text.strip()
away_score = score[1].text.strip()



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
