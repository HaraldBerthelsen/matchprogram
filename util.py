import sys, re
from urllib.request import urlopen
from bs4 import BeautifulSoup

def loadFromSF(matchid,season):
    info = {}
    url = "http://svenskfotboll.se/allsvenskan/information/?scr=result&fmid=%d" % matchid
    page = urlopen(url)
    soup = BeautifulSoup(page, "lxml")
    
    game_info = soup.find("div", attrs={"class":"game-info-page"})

    (info["finished"], info["date"], info["arena"], info["referee"], info["spectators"], info["spectators_away"], info["home_team"], info["away_team"]) = getMatchInfo(game_info)
    
    (info["home_score"], info["away_score"]) = getScore(game_info)

    if info["home_team"] == "Hammarby":
        bajen_is_home_team = True
    else:
        bajen_is_home_team = False

    if matchid in season.info["sc"]:
        cup = True
        cup_mapping = season.info["sc_map"]
    else:
        cup = False
        cup_mapping = []
        
    info["players"] = getPlayers(game_info, bajen_is_home_team,cup=cup, cup_mapping=cup_mapping)
    
    #print(json.dumps(info, default=jdefault, indent=4))
    return info





def getMatchInfo(game_info):
    #Match
    timer = game_info.find("div", attrs={"class":"timer"}).span.text.strip()
    if timer == "Avslutad":
        finished = True
    else:
        finished = False

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

    return (finished, date, arena, referee, spectators, spectators_away, home_team, away_team)


def getScore(game_info):
    scoreboard = game_info.find("div", attrs={"class":"scoreboard"})
    score = scoreboard.find_all("span")
    home_score = score[0].text.strip()
    away_score = score[1].text.strip()
    return (home_score, away_score)


def getPlayers(game_info, bajen_is_home_team,cup=False, cup_mapping=[]):

    if bajen_is_home_team:
        goals_class = "home"
        squad_class = "hometeam-squad"
        stats_class = "hometeam"
    else:
        goals_class = "away"
        squad_class = "awayteam-squad"
        stats_class = "awayteam"
        
    try:
        hif_goals = game_info.find("div", attrs={"class":goals_class}).find("ul", attrs={"class":"goals"}).find_all("li")
    except:
        hif_goals = []

    for hif_goal in hif_goals:
        time = hif_goal.find("span", attrs={"class":"time"}).text
        player = hif_goal.a.text
        #print("%s\t%s" % (time,player))


    try:
        hif_squad = game_info.find("div", attrs={"class":squad_class}).find_all("ul")
        lineup = hif_squad[0].find_all("li")
        subs = hif_squad[1].find_all("li")
    except:
        lineup = []
        subs = []

    players = {}
    for player in lineup:
        nr = int(re.sub(".\s*$", "", player.find("span", attrs={"class":"number"}).text))
        number = "%02d" % nr
        if cup and number in cup_mapping:
            number = cup_mapping[number]
        name = player.find("span", attrs={"class":"name"}).text
        players[number] = {"name":name, "start":1}

    for player in subs:
        nr = int(re.sub(".\s*$", "", player.find("span", attrs={"class":"number"}).text))
        number = "%02d" % nr
        if cup and number in cup_mapping:
            number = cup_mapping[number]
        name = player.find("span", attrs={"class":"name"}).text
        players[number] = {"name":name, "start":0}

    match_squad = lineup+subs

    for player in match_squad:
        nr = int(re.sub(".\s*$", "", player.find("span", attrs={"class":"number"}).text))
        number = "%02d" % nr
        if cup and number in cup_mapping:
            number = cup_mapping[number]
        goals = len(player.find_all("span",attrs={"data-symbol":"goal"}))
        if player.find("span",attrs={"data-symbol":"sub-out"}):
            sub_out = 1
        else:
            sub_out = 0
        if player.find("span",attrs={"data-symbol":"sub-in"}):
            sub_in = 1
        else:
            sub_in = 0

        if player.find("span",attrs={"data-symbol":"yellow"}):
            yellow_card = 1
        else:
            yellow_card = 0
        if player.find("span",attrs={"data-symbol":"red"}):
            red_card = 1
        else:
            red_card = 0
            
        players[number]["goals"] = goals
        players[number]["sub_out"] = sub_out
        players[number]["sub_in"] = sub_in
        players[number]["yellow_card"] = yellow_card
        players[number]["red_card"] = red_card


        
    playerstats_section = game_info.find("div", attrs={"class":"playerstats-section"})
    #It's not always there - not for the cup games apparently
    if playerstats_section:
    
        hifteam = playerstats_section.find("div",  attrs={"class":stats_class})
        tbody = hifteam.find("tbody")
        player_stats_table = tbody.find_all("tr")
        for player_stat_tr in player_stats_table:
            tds = player_stat_tr.find_all("td")
            nr = int(tds[0].span.text)
            number = "%02d" % nr
            if cup and number in cup_mapping:
                number = cup_mapping[number]
            #name = tds[1]
            #goals = [tds2]

            players[number]["pas"] = int(tds[3].text)
            players[number]["sko"] = int(tds[4].text)
            players[number]["sks"] = int(tds[5].text)
            players[number]["off"] = int(tds[6].text)
            players[number]["orf"] = int(tds[7].text)
            players[number]["tif"] = int(tds[8].text)
    
        

    return players

