import sys, re


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



def magazinestyle(lines):
    for line in lines:

        #print("#".join(re.split("\t+", line.strip())))

        try:
            (nr, name, a, field, nationality, birthyear, birthdate, height, motherclub, clubs, tohammarby, fromclub, contract, national, matches, league, cup, goals) = re.split("\t", line.strip())
        except:
            print(re.sub("\t", "TAB", line))
            sys.exit()

        toprint = """
%s. %s %s
%s %s. Längd: %s cm.
• Moderklubb: %s.
• Klubbar: %s, %s– Hammarby IF.
• Kontrakt till: %s. • Landskamper: %s
• Matcher: Ligaspel: %s. Cupspel: %s. Mål: %s.
            """ % (int(nr), name.strip(), field, nationality, birthdate, height, motherclub, clubs, tohammarby, contract, national, matches, cup, goals)

        if a == "+":
            print(toprint)

        


lines = sys.stdin.readlines()[1:]
#yearbookstyle(lines)
magazinestyle(lines)
