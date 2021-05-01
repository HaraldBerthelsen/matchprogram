import sys, re
import csv


#02	               Filippa Graneld	+	mittföltare	SWE	2001		IFK Lidingö	2019	Djurgårdens IF	2022	25	2

#HB vad är tredje fältet? prev? används inte..


def yearbookstyle(lines):
    for line in lines:

        #print("#".join(re.split("\t+", line.strip())))

        try:
            (nr, name, prev, field, nationality, birthyear, motherclub, profession, tohammarby, fromclub, contract, matches, goals) = re.split("\t+", line.strip())
        except:
            print(re.sub("\t", "TAB", line))
            sys.exit()

        if tohammarby == "-":            
            toprint = """
            %s. %s
            %s
            %s %s
            Moderklubb: %s
            Kom: Egen produkt
            Kontrakt till %s
            Matcher: %s. Mål: %s
            """ % (int(nr), name.strip(), field, nationality, birthyear, motherclub, contract, int(matches), int(goals))

        else:

            toprint = """
            %s. %s
            %s
            %s %s
            Moderklubb: %s
            Kom: %s (%s)
            Kontrakt till %s
            Matcher: %s. Mål: %s
            """ % (int(nr), name.strip(), field, nationality, birthyear, motherclub, int(tohammarby), fromclub, contract, int(matches), int(goals))

        print(toprint)




from datetime import date,datetime

def calculate_age(birthdate):
    born = datetime.strptime(birthdate, "%Y-%m-%d")
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def magazinestyle_old(lines):
    for line in lines:

        #print("#".join(re.split("\t+", line.strip())))

        try:
            info = re.split("\t", line.strip())
            #print(len(info))
            (nr, name, a, field, nationality, birthyear, birthdate, height, motherclub, clubs, tohammarby, fromclub, contract, national, matches, goals) = info
        except:
            print(re.sub("\t", "TAB", line))
            sys.exit()

        if a != "+":
            continue


        if height == "?":
            height = ""
        else:
            height = "Längd: %s cm." % height
            

        toprint = """
%s. %s %s
%s %s (%s år). %s
• Moderklubb: %s.
• Klubbar: %s, %s– Hammarby IF.
• Kontrakt till: %s. • Landskamper: %s
• Matcher: %s. Mål: %s.
            """ % (int(nr), name.strip(), field, nationality, birthdate, calculate_age(birthdate), height, motherclub, clubs, tohammarby, contract, national, matches, goals)

        print(toprint)

def magazinestyle(lines):
    for row in lines:
        if row["a-trupp"] != "+":
            continue

        if row["längd"] == "?":
            height = ""
        else:
            height = "Längd: %s cm." % row["längd"]

        if row["landskamper"] != "":
            national = "• Landskamper: %s" % row["landskamper"]
        else:
            national = ""

            
        nr = row["nr"]
        name = row["namn"]
        field = row["position"]
        nationality = row["land"]
        birthdate = row["född datum"]
        motherclub = row["moderklubb"]
        clubs = row["klubbar"]
        tohammarby = row["till bajen"]
        contract = row["kontrakt till"]
        leaguematches = int(row["liga 2021 matcher"])+int(row["liga tidigare matcher"])
        leaguegoals = int(row["liga 2021 mål"])+int(row["liga tidigare mål"])
        cupmatches = int(row["cup 2021 matcher"])+int(row["cup tidigare matcher"])
        cupgoals = int(row["cup 2021 mål"])+int(row["cup tidigare mål"])

        goals = leaguegoals+cupgoals
        
        toprint = """
%s. %s %s
%s %s. %s
• Moderklubb: %s.
• Klubbar: %s, %s– Hammarby IF.
• Kontrakt till: %s. %s
• Matcher: Seriespel: %s. Cupspel: %s Mål: %s.
            """ % (int(nr), name.strip(), field, nationality, birthdate, height, motherclub, clubs, tohammarby, contract, national, leaguematches, cupmatches, goals)

        print(toprint)

        


csvfile = "spelarinfo.csv"
with open(csvfile) as fh:
     lines = csv.DictReader(fh, delimiter='\t')
     magazinestyle(lines)

#lines = sys.stdin.readlines()[1:]
#yearbookstyle(lines)

