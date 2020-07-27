import sys, os, re
from bs4 import BeautifulSoup


with open("matcher.html") as fh:
    html_doc = fh.read()

data = BeautifulSoup(html_doc, 'html.parser')

rounds = data.find_all("div", "matchesRounds")

#print(len(rounds))

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
        print("READING %s" % match_file)
        
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


        #EXTRA TIME
        times = data.find_all("div", "time-after")
        first_half_extra_time = re.search("\+([0-9]+)'", times[0].text.strip()).group(1)
        match_info["first_half_extra_time"] = int(first_half_extra_time)
        
        second_half_extra_time = re.search("\+([0-9]+)'", times[2].text.strip()).group(1)
        match_info["second_half_extra_time"] = int(second_half_extra_time)


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
            if "Ersättare" in player.text:
                starting = False
            if "data-page-url" in player.attrs and "hammarby" in player["data-page-url"]:
                if starting:
                    hif_players.append(player)
                else:
                    hif_subs.append(player)

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
                "number": number,
                "starting": True
                }

            out = player_info1.find("span", "subs")
            if out:
                time = out.text
                if time.endswith("'"):
                    #print("UT (%s): %s" % (time[0:-1], name))
                    p["sub-out"] = time
                
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
            
            print("%s" % (p))
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
                "number": number,
                "starting": False
                }

            sub_in = player_info1.find("span", "subs")
            if sub_in:
                time = sub_in.text
                if time.endswith("'"):
                    #print("IN (%s): %s" % (time[0:-1], name))
                    p["sub-in"] = time
                
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
            
            print("%s" % (p))
            i+=2
            
        #sys.exit()


        
    else:
        print("Missing %s" % match_file)


        

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

        
    
    print("%s\t%s\t%s\t%20s\t%s\t%s\t%20s\t%20s\t%s\t%s\t%s" % (match_info["id"], match_info["round"], match_info["home/away"], match_info["opponent"], match_info["date"], match_info["time"], match_info["arena"], referee, match_info["hif_score"], match_info["other_score"], played_time))
    
