import sys, re


#02	               Filippa Graneld	+	mittföltare	SWE	2001		IFK Lidingö	2019	Djurgårdens IF	2022	25	2

#HB vad är tredje fältet? prev? används inte..

lines = sys.stdin.readlines()
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
    
