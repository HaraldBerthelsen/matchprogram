import sys, os, re
from bs4 import BeautifulSoup

#http --download https://www.allsvenskan.se/matcher/match?id=6178 -o 6178.html

with open("matcher.html") as fh:
    html_doc = fh.read()

data = BeautifulSoup(html_doc, 'html.parser')

rounds = data.find_all("div", "matchesRounds")

#print(len(rounds))


def convert_date(date):
    #"söndag 14 juni" -> "14/6"
    months = {
        "juni":6,
        "juli":7,
        "augusti":8
    }
    (_,day,month_name) = date.split(" ")
    return "%s/%s" % (day, months[month_name])
                      




match_info_list = []

#for round in rounds[0:1]:
for round in rounds:
    matches = round.find_all("a")
    #print(len(matches))

    for match in matches:
        teams_div = match.find("div", "teams")
        if not teams_div:
            continue
        teams = teams_div.text

        if teams.startswith("Hammarby -"):
            home = True
        elif teams.endswith("- Hammarby"):
            home = False
        else:
            continue

        match_id = match["class"][1][-4:]
        round = match["data-round"]
        date = match["data-start-time"]
        date = convert_date(date)
        time = match["data-time-calendar"]
        arena = match.find("div", "arena").text.strip()
        score = match.find("div", "match-score").text
        if home:
            ha = "H"
            opponent = teams.split("-")[-1].strip()
            hif_score = score.split("-")[0].strip()
            other_score = score.split("-")[1].strip()
        else:
            ha = "A"
            opponent = teams.split("-")[0].strip()
            hif_score = score.split("-")[1].strip()
            other_score = score.split("-")[0].strip()


        match_info = {
            "id": match_id,
            "round": round,
            "home/away": ha,
            "opponent": opponent,
            "date": date,
            "time": time,
            "arena": arena,
            "hif_score": hif_score,
            "other_score": other_score            
        }

        match_info_list.append(match_info)



for match_info in match_info_list:
    match_file = "%s.html" % match_info["id"]
    if os.path.exists(match_file):
        #print("READING %s" % match_file)
        
        with open(match_file) as fh:
            html_doc = fh.read()
        data = BeautifulSoup(html_doc, 'html.parser')

        #REFEREE
        details = data.find_all("div", "details")
        for detail in details:
            if "Domare" in detail.text:
                ref_names = detail.text.split(":")[1].strip().lower().split()
                ref_caps = []
                for name in ref_names:
                    ref_caps.append(name.capitalize())
                referee = " ".join(ref_caps)                
                match_info["referee"] = referee


        #ATTENDANCE
        match_info["attendance"] = "0"
        match_info["attendance_away"] = "0"
                

        #EXTRA TIME
        times = data.find_all("div", "time-after")
        m = re.search("\+([0-9]+)'", times[0].text.strip())
        if m:
            first_half_extra_time = m.group(1)
        else:
            first_half_extra_time = "0"
        match_info["first_half_extra_time"] = int(first_half_extra_time)
        
        second_half_extra_time = re.search("\+([0-9]+)'", times[2].text.strip()).group(1)
        match_info["second_half_extra_time"] = int(second_half_extra_time)
        match_info["total_time"] = 90+int(first_half_extra_time)+int(second_half_extra_time)


        #PLAYERS

        squads = data.find("table", "table__trupper")

        formation = re.search("Hammarby IF ([0-9-]+)", squads.text).group(1)
        match_info["formation"] = formation
        
        players = squads.find_all("td")
        hif_players = []
        hif_subs = []
        squad = []
        match_info["squad"] = squad
        starting = True
        for player in players:
            #"Ersättare" är en td som skiljer grupperna åt
            if "Ersättare" in player.text:
                starting = False
            if "data-page-url" in player.attrs and "hammarby" in player["data-page-url"]:
                if starting:
                    hif_players.append(player)
                else:
                    hif_subs.append(player)
                    #sys.stderr.write("%s\n" % player)
            elif "Mayckel Lahdo" in player.text:
                #ML har ingen data-page-url i 6220.html (dif)
                hif_subs.append(player)
                sys.stderr.write("%s\n" % player)
                

        i = 0
        while i+1 < len(hif_players):
            if match_info["home/away"] == "H":
                player_info1 = hif_players[i]
                player_info2 = hif_players[i+1]
            else:
                player_info2 = hif_players[i]
                player_info1 = hif_players[i+1]
                
            name = player_info1.find("span", "name").text
            number = player_info2.find("span", "number").text

            p = {
                "name": name,
                "number": int(number),
                "starting": True
                }

            out = player_info1.find("span", "subs")
            if out:
                time = out.text
                if time.endswith("'"):
                    #print("UT (%s): %s" % (time[0:-1], name))
                    p["sub-out"] = int(time[0:-1])
                
            yellow_card = player_info1.find("span", "yellow-card")
            if yellow_card:
                #print("GULT: %s" % name)
                p["yellow"] = True
            red_card = player_info1.find("span", "red-card")
            if red_card:
                #print("RÖTT: %s" % name)
                p["red"] = True
            goals = player_info1.find_all("span", "goal")
            if goals:
                #print("MÅL (%s): %s" % (len(goals), name))
                p["goals"] = len(goals)


            
            squad.append(p)
            
            #print("%s" % (p))
            i+=2
            
        i = 0
        while i+1 < len(hif_subs):
            if match_info["home/away"] == "H":
                player_info1 = hif_subs[i]
                player_info2 = hif_subs[i+1]
            else:
                player_info2 = hif_subs[i]
                player_info1 = hif_subs[i+1]
            name = player_info1.find("span", "name").text
            number = player_info2.find("span", "number").text

            p = {
                "name": name,
                "number": int(number),
                "starting": False
                }

            sub_in = player_info1.find("span", "subs")
            if sub_in:
                time = sub_in.text
                if time.endswith("'"):
                    #print("IN (%s): %s" % (time[0:-1], name))
                    p["sub-in"] = int(time[0:-1])
                
            yellow_card = player_info1.find("span", "yellow-card")
            if yellow_card:
                #print("GULT: %s" % name)
                p["yellow"] = True
            red_card = player_info1.find("span", "red-card")
            if red_card:
                #print("RÖTT: %s" % name)
                p["red"] = True
            goals = player_info1.find_all("span", "goal")
            if goals:
                #print("MÅL (%s): %s" % (len(goals), name))
                p["goals"] = len(goals)



            squad.append(p)
            
            sys.stderr.write("%s\n" % (p))
            i+=2
            
        #sys.exit()


        
    else:
        print("Missing %s" % match_file)



def print_formations():
     for match_info in match_info_list:
         if match_info["home/away"] == "H":
             print("Hammarby - %s" % match_info["opponent"])
         else:
             print("%s - Hammarby" % match_info["opponent"])
         
         formation = match_info["formation"].split("-")
         ps = match_info["squad"][:11] 
         print(match_info["formation"])
         #print(len(ps))
         keeper = ps[0]
         print("%s %s" % (keeper["number"], keeper["name"]))
         print("--")
         nDef = int(formation[0])
         i1 = nDef+1
         defenders = ps[1:i1]
         for defender in defenders:
             print("%s %s" % (defender["number"], defender["name"]))
         print("--")
         
         if len(formation) == 4:
             nMfs1 = int(formation[1])
             i2a = i1+nMfs1
             mfs1 = ps[i1:i2a]
             for mf1 in mfs1:
                 print("%s %s" % (mf1["number"], mf1["name"]))

             print("--")
             nMfs = int(formation[2])
             i2 = i2a+nMfs
             mfs = ps[i2a:i2]
             for mf in mfs:
                 print("%s %s" % (mf["number"], mf["name"]))
         else:
             nMfs = int(formation[1])
             i2 = i1+nMfs
             mfs = ps[i1:i2]
             for mf in mfs:
                 print("%s %s" % (mf["number"], mf["name"]))

         print("--")
         #nFws = int(formation[-1])
         #print(nFws)
         fws = ps[i2:]
         for fw in fws:
             print("%s %s" % (fw["number"], fw["name"]))
 
         print("")
                 


         
             
        
players = {}
def print_game_stats():

    #Print header
    to_print = ["Datum", "Motståndare", "Res", "Publik (bortalag)"]
    print_info(to_print, {}, nonewline=True)

    for match_info in match_info_list:
        for player in match_info["squad"]:            
            players[player["number"]] = player["name"]
    #players_by_number = sorted(match_info_list[0]["squad"], key=lambda k: k['number'])
    for nr in sorted(players):
        print("%s %s\t" % (nr, players[nr]), end='')
    #for player in players_by_number:
    #    print("%s %s\t" % (player["number"], player["name"]), end='')
    print("")

    
    for match_info in match_info_list:

        if "referee" in match_info:
            referee = match_info["referee"]
        else:
            referee = "-"


        played_time = 90
        if "first_half_extra_time" in match_info:
            played_time += match_info["first_half_extra_time"]
        if "second_half_extra_time" in match_info:
            played_time += match_info["second_half_extra_time"]

        #Datum	Motståndare	Res	Publik (bortalag)	1 Johan Wiland	2 Simon Sandberg	3 Dennis Widgren	4 Odilon Kossounou	4 Richard Magyar	5 David Fällman	6 Darijan Bojanic	7 Imad Khalili	8 Jeppe Andersen	9 Sander Svendsen
													
        #18/2	Varbergs BOIS	3-0	11 140 (-)	-	S	U	I		S	B	I	S	S1


        to_print = ["date", "opponent", ["hif_score","-","other_score"],["attendance"," (", "attendance_away", ")"]]
        print_info(to_print, match_info, nonewline=True)
        
        players_this_match = {}
        for player in match_info["squad"]:
            players_this_match[player["number"]] = player
                               
        for nr in sorted(players):
            p = "-"
            y = ""
            r = ""
            g = ""
            if nr in players_this_match:
                player = players_this_match[nr]
                if player["starting"]:
                    p = "S"
                else:
                    p = "B"
                if "sub-out" in player:
                    p = "U"
                if "sub-in" in player:
                    p = "I"
                if "yellow" in player:
                    y = "G"
                if "red" in player:
                    r = "R"
                if "goals" in player:
                    g = player["goals"]
            print("%s%s%s%s\t" % (p, y, r, g), end='')
        print("")

        


def print_info(to_print,match_info, nonewline=False):
    print_list = []
    for t in to_print:
        if type(t) == type([]):
            print_list2 = []
            for t2 in t:
                if t2 in match_info:
                    print_list2.append(match_info[t2])
                else:
                    print_list2.append(t2)
            print_list.append("".join(print_list2))
                    
        elif t in match_info:
            print_list.append(match_info[t])
        else:
            print_list.append(t)
    if not nonewline:
        print("\t".join(print_list))
    else:
        print("\t".join(print_list), end='\t')
        


        

def print_player_stats():
     for match_info in match_info_list:
         for player in match_info["squad"]:
             update_info(player, match_info["total_time"])
         #print(players[25])

     print_player_stats_by_number()


def update_info(player, match_time=90):
    nr = player["number"]
    #if nr == 25:
    #    print(player)
    p = players[nr]
    if type(p) == type(""):
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
        
    if player["starting"] or "sub-in" in player:
            p["nMatches"] += 1 
    if "goals" in player:
            p["nGoals"] += int(player["goals"])
    if "yellow" in player:
            p["nYellow"] += 1
    if "red" in player:
            p["nRed"] += 1

    if "sub-in" in player:
        p["timePlayed"] += match_time-player["sub-in"]
    if player["starting"] and "sub-out" in player:
        p["timePlayed"] += match_time-player["sub-out"]
    if player["starting"]:
        p["timePlayed"] += match_time
            
    players[nr] = p

            
def print_player_stats_by_number():
    #print(players[25])
    print("nr                              namn	spel/mål assist	skott speltid gula kort röda kort")
    for nr in sorted(players):
        #1	Johan Wiland	7/0	0	0	568	0	0
        print("%s\t%30s\t%s/%s\t%s\t%s\t%s\t%s\t%s" % (nr, players[nr]["name"], players[nr]["nMatches"], players[nr]["nGoals"], players[nr]["nAssists"], players[nr]["nShots"], players[nr]["timePlayed"], players[nr]["nYellow"], players[nr]["nRed"]))
    

#print_formations()
print_game_stats()
print_player_stats()
