

corrections = {
    2018:{
        3791294:[
            (["players","09","sub_in"],69), 
            (["players","09","sub_out"],0)
            ]
        }
    }



def correct(year, matchid, match):
    if year in corrections and matchid in corrections[year]:
        corrs = corrections[year][matchid]
        info = match.info
        for (keylist, newvalue) in corrs:
            info = updateDict(info, keylist, newvalue)
        match.info = info
        #print(match.info["players"]["04"])
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
