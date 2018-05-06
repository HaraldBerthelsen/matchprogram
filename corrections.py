

corrections = {}
corrections[2018] = {}

#Degerlund hade nr 15 och spelade hela matchen de tre cupmatcherna
#Det är inte det som är felet, måste fixa i cup_mappningen TODO
#corrections[2018][3791294] = [(["players","15","start"],1)]
#corrections[2018][3791292] = [(["players","15","start"],1)]
#corrections[2018][3791290] = [(["players","15","start"],1)]

corrections[2018][3791294] = [
    (["players","09","sub_in"],69), 
    (["players","09","sub_out"],0)
]
    
corrections[2018][3795764] = [
    #Jeppe Andersen, inte Hamad, ska ha målpass (gbg-hif)
    (["players","06","pas"],0), 
    (["players","08","pas"],1)
]

corrections[2018][3795956] = [
    #Bajen - bp
    #Hamads pass fram till Khalilis andra mål
    (["players", "06", "pas"], 1),
    #Paulsen till Hamad 3-0
    (["players", "04", "pas"], 1)
]



def correct(year, matchid, match):
    if year in corrections and matchid in corrections[year]:
        corrs = corrections[year][matchid]
        info = match.info
        for (keylist, newvalue) in corrs:
            info = updateDict(info, keylist, newvalue)
        match.info = info
    return match

def updateDict(info, keylist, newvalue):
    if type(info) == type({}):
        key = keylist[0]
        #print(key)
        #print(info[key])
        info[key] = updateDict(info[key], keylist[1:], newvalue)
        #print(key)
        #print(info[key])
    else:
        info = newvalue
    return info
