# -*- coding: utf-8 -*-
import sys, re, json
import util

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

#KOLLA blir fel med cupmatcherna eftersom numrena inte stämmer, Hamad, Borges, Degerlund, Bengtsson, Krusnell


def main():
    year = 2018
    season = Season(year)
    season.loadJson("season_%d_info.json" % year)
    #Uppdatera från SF och spara til fil
    season.loadMatchesFromSF()
    season.loadMatchesFromJson()
    #Skriv ut statistik för senast spelade
    #season.printLastPlayedMatchStatistics()
    #Eller skriv ut för alla spelade
    season.printMatchStatistics()
    season.printPlayerStatistics()


class Season(object):

    def __init__(self, year):
        self.info = {}
        self.matches = []
        
    def loadMatchesFromSF(self):
        nr = 1
        for matchid in self.info["matchIds"]:
            match = Match(nr, matchid)
            match.loadFromSF(self)
            match.saveJson("matchid_%d.json" % matchid)
            nr += 1

    def loadMatchesFromJson(self):
        nr = 1
        for matchid in self.info["matchIds"]:
            match = Match(nr, matchid)
            match.loadJson("matchid_%d.json" % matchid)
            self.matches.append(match)
            nr += 1

    def saveJson(self, filename):
        fh = open(filename, "w", encoding="utf-8")
        fh.write(json.dumps(self.info, default=jdefault, indent=4))
        fh.close()


    def loadJson(self, filename):
        fh = open(filename, encoding="utf-8")
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
        ps = PlayerStats(nr)        
        for match in self.matches:
            ps_match = match.getPlayerStats(nr)
            self.sumPlayerStats(ps, ps_match)
            if ps_match.get("start") or ps_match.get("sub_in"):
                ps.set("matches", ps.get("matches") + 1)
        return ps

    def sumPlayerStats(self, s1, s2):        
        for key in s2:
            if key in s1.stats:
                s1.stats[key] += s2[key]
            else:
                s1.stats[key] = s2[key]
        return s1
            
    

    def printMatchStatistics(self):
        self.printMatchStatisticsHeader()
        for match in self.matches:
            match.printMatchStatistics(self)

    def printMatchStatisticsHeader(self):
        header_to_print = "datum\tmotståndare\tres\tåskådare" 
        for player in sorted(self.info["squad"]):
            initials = self.getPrintInitials(player)
            header_to_print += "\t%s %s" % (player,initials)

        print("\nMatch- & spelarstatistik\n")
        print(header_to_print)

            
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

        print("\nSpelarstatistik\n")    
        print("%s\t%s\t%s (%s)\t%s\t%s\t%s\t%s\t%s" % ("nr","spelare","matcher","mål","skott","skott på mål","orsakat frispark","gula kort","röda kort"))

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
            print("%s\t%s\t%d (%d)\t%d\t%d\t%d\t%d\t%d" % (nr,shortname,matches,goals,shots,shotsongoal,causedfreekicks,yellow_cards,red_cards))

    
        
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

    def loadFromSF(self,season):
        self.info = util.loadFromSF(self.matchid,season)
        

    def saveJson(self, filename):
        fh = open(filename, "w", encoding="utf-8")
        fh.write(json.dumps(self.info, default=jdefault, indent=4))
        fh.close()


    def loadJson(self, filename):
        fh = open(filename, encoding="utf-8")
        self.info = json.loads(fh.read())
        fh.close()

    def getPlayerStats(self, nr):
        if nr in self.info["players"]:
            return self.info["players"][nr]
        else:
            return {}

        
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



        m = re.match("^[0-9]{4}-0?([1-9]+)-0?([1-9]+)", date)
        if m:
            month = m.group(1)
            day = m.group(2)
        date_to_print = "%s/%s" % (day, month)


        match_stats_to_print = "%s\t%s\t%s-%s\t%s (%s)" % (date_to_print, opponent, bajen_score, opponent_score, spectators, spectators_away)

        #season = Season(2018)

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
                if player_match_info["yellow_card"]:
                    info_to_print = "%s%s" % (info_to_print, "G")
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
    main()

