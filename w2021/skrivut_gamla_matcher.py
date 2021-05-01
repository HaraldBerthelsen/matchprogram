import csv

cup = dict()
league = dict()
cupgoals = dict()
leaguegoals = dict()


emma = list()

csvfile = "spelarinfo_alla_matcher.csv"
with open(csvfile) as fh:
     lines = csv.DictReader(fh, delimiter='\t')
     for row in lines:

         if "Hammarby" in row["TEAM"]:
             if "Cupen" in row["TOURNAMENT"]:             
                 if row["PLAYER"] in cup:
                     cup[row["PLAYER"]] += int(row["MATCHES"])
                 else:
                     cup[row["PLAYER"]] = int(row["MATCHES"])
                 if row["PLAYER"] in cupgoals:
                     cupgoals[row["PLAYER"]] += int(row["GOALS"])
                 else:
                     cupgoals[row["PLAYER"]] = int(row["GOALS"])
             else:
                 if row["PLAYER"] in league:
                     league[row["PLAYER"]] += int(row["MATCHES"])
                 else:
                     league[row["PLAYER"]] = int(row["MATCHES"])
                 if row["PLAYER"] in leaguegoals:
                     leaguegoals[row["PLAYER"]] += int(row["GOALS"])
                 else:
                     leaguegoals[row["PLAYER"]] = int(row["GOALS"])
                 

             #if row["PLAYER"] == "Emma Jansson":
             #    print("%s\t%s\t%s\t%s" % (row["TEAM"], row["YEAR"], row["TOURNAMENT"], row["MATCHES"]))
             #    emma.append(int(row["MATCHES"]))
             


                     
for player in league:
    if player in cup:
        cupmatches = cup[player]
        cupgls = cupgoals[player]
    else:
        cupmatches = 0
        cupgls = 0
    print("%s\t%s\t%s\t%s\t%s" % (player, league[player], leaguegoals[player], cupmatches, cupgls))

#print(emma)
#print(sum(emma))
