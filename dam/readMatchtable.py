import sys, re

matchtablefile = "matchtabell-elitettan-se.txt"

lines = open(matchtablefile).readlines()

teams = []
matches = {}



i = 0
while i < len(lines)-1:    
    line1 = lines[i]
    line2 = lines[i+1]
    i += 1
    if line1.startswith("#"):
        continue
    if re.match("^\s*$", line1):
        continue
    i += 1
    

    #print(line1)
    
    m = re.match("^\s*([0-9]+)\s+([0-9]+)\s+(\S+)\s+([0-9:]+)\s(.+)\s+([0-9]+)\s*-\s*([0-9]+)\s*$", line1)

    if m:
        round = m.group(1)
        day = m.group(2)
        month = m.group(3)
        time = m.group(4)
        hometeam = m.group(5)
        ht_goals = m.group(6)
        at_goals = m.group(7)

    else:
        m = re.match("^\s*([0-9]+)\s+([0-9]+)\s+(\S+)\s+([0-9:]+)\s(.+)\s+-\s*$", line1)
        round = m.group(1)
        day = m.group(2)
        month = m.group(3)
        time = m.group(4)
        hometeam = m.group(5)
        ht_goals = None
        at_goals = None
        

    awayteam = line2.strip()


    if not hometeam in teams:
        teams.append(hometeam)
    if not awayteam in teams:
        teams.append(awayteam)

    matches[(hometeam,awayteam)] = (round, day, month, time, ht_goals, at_goals)
        

    
#for (hometeam, awayteam) in matches:
#    ht_goals = matches[(hometeam,awayteam)][4]
#    at_goals = matches[(hometeam,awayteam)][5]

#    if ht_goals != None:
#        print("%s-%s: %s-%s" % (hometeam, awayteam, ht_goals, at_goals))


teams.sort()
print("\t%s" % "\t".join(teams))

for hometeam in teams:
    htline = []
    for awayteam in teams:
        if hometeam == awayteam:
            htline.append("X")
        else:
            ht_goals = matches[(hometeam,awayteam)][4]
            at_goals = matches[(hometeam,awayteam)][5]
            if ht_goals != None:
                htline.append("%s-%s" % (ht_goals, at_goals))
            else:
                htline.append("-")
                
    print("%s\t%s" % (hometeam,"\t".join(htline)))

    

