# -*- coding: utf-8 -*-
import sys, re, json
import util, corrections

#KOLLA
#Spelartruppen finns på svf men utan nummer. Nummer kan ju ändras också.. Gör en egen lista med nummer och det namn som vi vill ha i programmet, en del namn är olika på svf.
#Alt använd svf spelarid? Bättre för att kunna använda gammal statistik? I s f behövs en koppling till tröjnummer och till namn som vi vill använda.
#borta-åskådare ? Var finns den informationen?
#spelarstatistiken på svf tveksam? ex efter sirius står ingen offside för någon spelare, men det var flera avvinkningar?


#TODO
#Läs in matchinfo från sf och spara till fil
#Läs in säsong från fil, uppdatera med ny match, skriv till fil
#Läs in säsong från fil, skriv ut för smp

#TODO
#testar med två matcher 2017
#matches = [3491041, 3491183]
#season = Season(2017, matches)
#sen med 2018
#matches = [3795745]




def main(mode=None):
    year = 2018
    #TEST TODO rätt trupp!
    #year = 2017
    season = Season(year)
    season.loadJson("season_%d_info.json" % year)
    #Uppdatera från SF och spara til fil
    #season.loadMatchesFromSF()
    #season.loadLatestMatchFromSF()

    season.loadMatchesFromJson()


    if mode == "yearbook":
        #skriv ut i format för årskrönikan
        season.printYearbookFormat()

    elif mode == "last":
        #Skriv ut statistik för senast spelade
        season.printLastPlayedMatchStatistics()

    else:
        #Eller skriv ut för alla spelade
        season.printMatchStatistics()
        season.printPlayerStatistics()

class Season(object):

    def __init__(self, year):
        self.year = year
        self.info = {}
        self.matches = []
        
    def loadLatestMatchFromSF(self):
        nr = 1
        matchid = self.info["matchIds"][-1]
        match = Match(nr, matchid)
        match.loadFromSF(self)
        match.saveJson("%s/matchid_%d.json" % (self.year, matchid))


    def loadMatchesFromSF(self):
        nr = 1
        for matchid in self.info["matchIds"]:
            match = Match(nr, matchid)
            match.loadFromSF(self)
            match.saveJson("%s/matchid_%d.json" % (self.year, matchid))
            nr += 1

            
    def loadMatchesFromJson(self):
        nr = 1
        for matchid in self.info["matchIds"]:
            match = Match(nr, matchid)
            match.loadJson("%s/matchid_%d.json" % (self.year,matchid))
            match = corrections.correct(self.year, matchid, match)
            self.matches.append(match)
            nr += 1
            #print(matchid)

    def saveJson(self, filename):
        try:
            fh = open(filename, "w", encoding="utf-8")
        except:
            import io
            fh = io.open(filename, "w", encoding="utf-8")
            
        fh.write(json.dumps(self.info, default=jdefault, indent=4))
        fh.close()


    def loadJson(self, filename):
        try:
            fh = open(filename, encoding="utf-8")
        except:
            import io
            fh = io.open(filename, encoding="utf-8")


        self.info = json.loads(fh.read())
        fh.close()

    def getPrintInitials(self, nr):
        names = self.info["squad"][str(nr)].split()
        initials = []
        for name in names:
            initials.append(name[0])
        return "".join(initials)

    def getPrintName(self, nr):
        return self.info["squad"][str(nr)]
    

    def getShortname(self, nr):
        if str(nr) in self.info["shortnames"]:
            return self.info["shortnames"][str(nr)]
        else:
            names = self.info["squad"][str(nr)].split()
            return names[-1]

        
    def getPlayerStatistics(self, nr):
        ignoreCupGames = True
        ps = PlayerStats(nr)
        cupmatches = self.info["sc"]
        cupmatches.extend(self.info["sc2"])
        for match in self.matches:
            if ignoreCupGames and match.matchid in cupmatches:
                continue
            ps_match = match.getPlayerStats(nr)
            self.sumPlayerStats(ps, ps_match)
            if ps_match.get("start") or ps_match.get("sub_in"):
                ps.set("matches", ps.get("matches") + 1)
            if ps_match.get("start"):
                minutes_played = 90
                if ps_match.get("sub_out"):
                    #TODO exact time
                    time_event = ps_match.get("sub_out")
                    minutes_played = minutes_played-(90-time_event)
                ps.set("minutes_played", ps.get("minutes_played")+minutes_played)
            if ps_match.get("sub_in"):
                #TODO exect time
                time_event = ps_match.get("sub_in")
                minutes_played = 90-time_event
                ps.set("minutes_played", ps.get("minutes_played")+minutes_played)
                
        return ps

    def sumPlayerStats(self, s1, s2):        
        for key in s2:
            if key in s1.stats:
                s1.stats[key] += s2[key]
            else:
                s1.stats[key] = s2[key]
        return s1
            
    

    def printLastPlayedMatchStatistics(self):
        self.printMatchStatisticsHeader()
        match = self.matches[-1]
        match.printMatchStatistics(self)

    def printMatchStatistics(self):
        self.printMatchStatisticsHeader()
        for match in self.matches:
            match.printMatchStatistics(self)

    def printMatchStatisticsHeader(self):
        header_to_print = u"datum\tmotståndare        \tres\tåskådare" 
        for player in sorted(self.info["squad"]):
            initials = self.getPrintInitials(player)

            #special för att få det rätt med Barny/Dibba
            if player == "1314":
                player = "14"
            #special för att få det rätt med Rodic/Smarra
            if player == "1011":
                player = "11"


            try:
                header_to_print += "\t%s %s" % (player,initials)
            except:
                header_to_print += u"\t%s %s" % (player,initials)

        print("\nMatch- & spelarstatistik\n")
        print(header_to_print)

            
    def printPlayerStatisticsOLD(self):
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

        print("\nSpelarstatistik\n")    
        print("%s\t%-9s\t%s (%s)\t%s\t%s\t%s\t%s\t%s" % ("nr","spelare","matcher","mål","skott","skott på mål","orsakat frispark","gula kort","röda kort"))

        for nr in sorted(self.info["squad"]):
            shortname = self.getShortname(nr)
            stats = self.getPlayerStatistics(nr)

            matches = stats.get("matches")
            goals = stats.get("goals")
            shots = stats.get("sko")
            shotsongoal = stats.get("spm")
            causedfreekicks = stats.get("orf")
            yellow_cards = stats.get("yellow_card")
            red_cards = stats.get("red_card")



            print("%s\t%-9s\t%d (%d)\t%d\t%d\t%d\t%d\t%d" % (nr,shortname,matches,goals,shots,shotsongoal,causedfreekicks,yellow_cards,red_cards))

    def printPlayerStatistics(self):
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

        #Läs skottstatistik från msn-fil
        #msn_file = "2018/msn_gbg_hif.txt"
        #msn_file = "2018/msn_hif_bp.txt"
        #msn_file = "2018/msn_hacken_bajen.txt"
        #msn_file = "2018/msn_dif_bajen.txt"
        #msn_file = "2018/msn_bajen_sundsvall.txt"
        #msn_file = "2018/msn_bajen_mff.txt"
        #msn_file = "2018/msn_bajen_aik.txt"
        #msn_file = "2018/msn_kalmar_bajen.txt"
        #msn_file = "2018/msn_elfsborg_bajen.txt"
        #msn_file = "2018/msn_norrkoping_bajen.txt"
        #msn_file = "2018/msn_dalkurd_bajen.txt"
        #msn_file = "2018/msn_aik_bajen.txt"
        #msn_file = "2018/msn_bajen_elfsborg.txt"
        #msn_file = "2018/msn_malmo_bajen.txt",
        #msn_file = "2018/msn_bajen_kalmar.txt"
        msn_file = "2018/msn_sundsvall_bajen.txt"
        msn_shots = {}
        msn_ass = {}
        with open(msn_file) as f:
            lines = f.readlines()
            for line in lines:
                #print(line)
                info = line.split("\t")
                nr = info[0]
                shots = int(info[-2])
                msn_shots[nr] = shots
                ass = int(info[-3])
                msn_ass[nr] = ass
        #print(msn_shots)
        
        print("\nSpelarstatistik\n")    
        #print("%s\t%-9s\t%s (%s)\t%s\t%s\t%s\t%s\t%s" % ("nr","spelare","matcher","mål","skott","skott på mål","orsakat frispark","gula kort","röda kort"))
        print("%s\t%-9s\t%s/%s\t%s\t%s\t%s\t%s\t%s" % ("nr", "spelare", "matcher", "mål", "assist", "skott", "min", "gula","röda kort"))

        for nr in sorted(self.info["squad"]):
            shortname = self.getShortname(nr)
            stats = self.getPlayerStatistics(nr)

            matches = stats.get("matches")
            goals = stats.get("goals")

            #shotsongoal = stats.get("spm")
            #causedfreekicks = stats.get("orf")
            minutes_played = stats.get("minutes_played")
            yellow_cards = stats.get("yellow_card")
            red_cards = stats.get("red_card")


            
            #använd msn för skott+assist istf svenskfotboll
            #shots = stats.get("sko") + stats.get("spm")
            #assists = stats.get("pas")
            if nr in msn_shots:
                shots = msn_shots[nr]
            else:
                shots = 0
            if nr in msn_ass:
                assists = msn_ass[nr]
            else:
                assists = 0

            #special för att få det rätt med Barny/Dibba
            if nr == "1314":
                nr = "14"
            #special för att få det rätt med Rodic/Smarra
            if nr == "1011":
                nr = "11"
                

    
            #print("%s\t%-9s\t%d (%d)\t%d\t%d\t%d\t%d\t%d" % (nr,shortname,matches,goals,shots,shotsongoal,causedfreekicks,yellow_cards,red_cards))
            print("%s\t%-9s\t%3d / %-3d\t%d\t%d\t%d\t%d\t%d" % (nr,shortname,matches,goals,assists,shots,minutes_played,yellow_cards,red_cards))

    def printYearbookFormat(self):

        for match in self.matches:
            #Om matchfilen har kompletterats
            if "positions" in match.info:
                match.printYearbookFormat(self)
                print("\n\n")

                
class Match(object):
    def __init__(self, nr, matchid):
        self.nr = nr
        self.matchid = matchid
        self.info = {}
        #home_team
        #away_team 
        #date
        #arena
        #referee
        #linesmen?
        #assistant referee?
        #attendance
        #attendance_away
        #home_lineup
        #home_subs
        #away_lineup
        #away_subs

    def get(self, key):
        return self.info[key]

    def set(self, key, value):
        self.info[key] = value

        
    def loadFromSF(self,season):
        self.info = util.loadFromSF(self.matchid,season)
        

    def saveJson(self, filename):
        try:
            fh = open(filename, "w", encoding="utf-8")
        except:
            import io
            fh = io.open(filename, "w", encoding="utf-8")
        fh.write(json.dumps(self.info, default=jdefault, indent=4))
        fh.close()


    def loadJson(self, filename):
        try:
            fh = open(filename, encoding="utf-8")
        except:
            import io
            fh = io.open(filename, encoding="utf-8")
        self.info = json.loads(fh.read())
        fh.close()

    def getPlayerStats(self, nr):
        if nr in self.info["players"]:
            return self.info["players"][nr]
        else:
            return {}


    def printYearbookFormat(self, season):
        date = self.info["date"]
        spectators = self.info["spectators"]
        spectators_away = self.info["spectators_away"]
        home_team = self.info["home_team"]
        away_team = self.info["away_team"]
        home_score = self.info["home_score"]
        away_score = self.info["away_score"]
        halftime_score = self.info["halftime_score"]
        players = self.info["players"]
        scores = self.info["scores"]

        if home_team in season.info["teams"]:
            home_team = season.info["teams"][home_team]
        if away_team in season.info["teams"]:
            away_team = season.info["teams"][away_team]
        
        lines = []
        #Line: Teams, score, halftime score
        lines.append("%s-%s %s-%s (%s)" % (home_team, away_team, home_score, away_score, halftime_score))

        #Lines: Goal scored, player, time (2 per line)
        nr = 0
        score_prints = []
        for score in scores:
            nr += 1
            score_prints.append("%s %s (%s)" % (score[1], score[0], score[2]))
            if nr == 2:
                lines.append(", ".join(score_prints))
                nr = 0
                score_prints = []
        if len(score_prints) > 0:
            lines.append(", ".join(score_prints))

        #Line: Publik
        lines.append("Publik: %s" % spectators)

        #Line: Squad, substitutes
        squad = []

        subs_in = self.findSubsIn(season)

        #According to list of positions
        for playernr in self.info["positions"]:
            if playernr in players:
                player = players[playernr] 
                if player["start"]:
                    name = season.info["squad"][playernr]
                    #player["name"]
                    if player["sub_out"]:
                        (sub_in, subs_in) = self.getSubIn(subs_in, player["sub_out"], playernr, season)
                        squad.append("%s (%s, %s)" % (name, sub_in, player["sub_out"]))
                    else:
                        squad.append("%s" % (name))


        #"halftime_score":"2-0",
        #"scores": [["Jiloan Hamad","1-0","45"],["Jiloan Hamad","2-0","50"],["Sam Lundholm","2-1","74"],["Jiloan Hamad","3-1","90+1"]],
        #"positions": ["01", "02","05","04","03", "19","08","06", "07","22","14"],


                    
        lines.append("Laget: %s" % ", ".join(squad))
        print("\n".join(lines))

    def findSubsIn(self, season):
        subs = []
        for playernr in self.info["players"]:
            player = self.info["players"][playernr]
            if player["sub_in"]:
                name = season.info["squad"][playernr]
                subs.append((player["sub_in"], playernr, name))
        return subs

    def getSubIn(self, subs_in, time, number, season):
        for (sub_in_time, sub_in_number, sub_in_name) in subs_in:
            if sub_in_time == time and self.onlySubAtTime(time, subs_in):
                #print("only sub at time %s" % time)
                subs_in.remove((sub_in_time, sub_in_number, sub_in_name))
                return (sub_in_name, subs_in)
            elif sub_in_time == time and self.samePosition(number, sub_in_number, season):
                #print("same position %s %s" % (number, sub_in_number))
                subs_in.remove((sub_in_time, sub_in_number, sub_in_name))
                return (sub_in_name, subs_in)
        print("%s %s\t%s" % (time, number, subs_in))
        raise Exception("PROBLEM WITH SUBS")

    def onlySubAtTime(self, time, subs_in):
        #print("onlySubAtTime; %s %s" % (time, subs_in))
        count = 0
        for (sub_in_time, sub_in_number, sub_in_name) in subs_in:
            if time == sub_in_time:
                #print("%s == %s %s" % (time, sub_in_time, count))
                if count > 0:
                    return False
                else:
                    count += 1
        return True
    
    def samePosition(self, nr1, nr2, season):
        for pos in season.info["positions"]:
            if nr1 in season.info["positions"][pos] and nr2 in season.info["positions"][pos]:
                return True
        return False

    
    def printMatchStatistics(self, season):
        date = self.info["date"]
        spectators = self.info["spectators"]
        spectators_away = self.info["spectators_away"]
        home_team = self.info["home_team"]
        away_team = self.info["away_team"]
        home_score = self.info["home_score"]
        away_score = self.info["away_score"]
        players = self.info["players"]
        self.printMatchStatistics2(date, spectators, spectators_away, home_team, away_team, home_score, away_score, players, season)

    def printMatchStatistics2(self, date, spectators, spectators_away, home_team, away_team, home_score, away_score, players, season):
        #Utskrift:

        #1: Matchstatistik
        #datum d/m
        #motståndare, fetstil om hemma
        #resultat (bajen först? KOLLA) x-x
        #publik (bortasupportrar inom parentes - finns den infon?)
        #för varje spelare i nummerordning:
        #S grön prick, startelvan
        #I gul prick, inbytt
        #U ? prick, utbytt (inte med i smp)
        #Siffra efter för antal mål
        #R rött kort (inte med i smp)
        #G gult kort (inte med i smp)

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



        m = re.match("^[0-9]{4}-([0-9]+)-([0-9]+)", date)
        if m:
            month = int(m.group(1))
            day = int(m.group(2))
        try:
            date_to_print = "%d/%d" % (day, month)
        except:
            print("Something wrong with date '%s'" % date)
            date_to_print = date

        match_stats_to_print = "%s\t%-20s\t%s-%s\t%-6s (%s)" % (date_to_print, opponent, bajen_score, opponent_score, spectators, spectators_away)


        player_stats_to_print = []
    #    for player in sorted(players):
        for player in sorted(season.info["squad"]):
            info_to_print = ""
            if player in players:
                player_match_info = players[player]
                #print("%s %s" % (player, player_match_info))
                info_to_print = "-"
                if player_match_info["start"]:
                    info_to_print = "S"
                if player_match_info["sub_in"]:
                    info_to_print = "I"
                if player_match_info["sub_out"]:
                    info_to_print = "U"
                if player_match_info["goals"] > 0:
                    info_to_print = "%s%d" % (info_to_print, player_match_info["goals"])
                #Skippar G för gula kort 180410
                #if player_match_info["yellow_card"]:
                #    info_to_print = "%s%s" % (info_to_print, "G")
                if player_match_info["red_card"]:
                    info_to_print = "%s%s" % (info_to_print, "R")
            else:
                #player not in match squad
                info_to_print = "."

            player_stats_to_print.append(info_to_print)

        print("%s\t%s" % (match_stats_to_print, "\t".join(player_stats_to_print)))



    
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

    def get(self, stat):
        if stat in self.stats:
            return self.stats[stat]
        else:
            return 0

    def set(self, stat, value):
        self.stats[stat] = value

    def loadJson(self, filename):
        pass

    def saveJson(self, filename):
        pass
    
    def printForSMP(self):
        pass




    
def jdefault(o):
    return o.__dict__






if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = None

    main(mode)

