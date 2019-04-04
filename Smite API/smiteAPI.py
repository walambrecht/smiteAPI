import requests
import time
import datetime
import hashlib
import json

from cachetools import cached, TTLCache
cache = TTLCache(maxsize=30, ttl=300)

# Neccesary information for authentication with the Smite API
# For legal reasons, auth_key and dev_id left blank for
# user to fill in.
url = 'http://api.smitegame.com/smiteapi.svc/'
dev_id = #Please fill in
auth_key = #Please fill in

# Creating a new session to call requests
s = requests.session()

# signature: String -> String
# Creates a md5 encrypted Hash from the dev_id, an input string, the auth key,
# the UTC time in yyMMDDHHmmSS, all encoded with utf-8. Outputs as a hexdigest
def signature(methd):
    h = hashlib.new('md5')
    s = (dev_id + methd + auth_key + str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S'))).encode('utf-8')
    h.update(s)
    return h.hexdigest()

# apiRequest: String String -> Dictionary
# Creates a request for the Smite API using the given url, the type of request,
# the dev_id, a created signature, and the time in UTC.
def sessionRequest(req, session):
    return (session.get(url + req + 'Json/' + dev_id + '/' + signature(req) +
    '/' + str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S'))))

# apiRequest: String String -> Dictionary
# Creates a request for the Smite API using the given url, the type of request,
# the dev_id, a created signature, and the time in UTC.
def apiRequest(req, sessionID, session, playerName):
    return (session.get(url + req + 'Json/' + dev_id + '/' + signature(req) + '/' + sessionID +
     '/' + str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')) + '/' + playerName))

# cachePlayerInfo: String -> {Dictionary-of Key: String}
# Creates a dictionary with the username as the key and the resulting player information as the value.
def cachePlayerInfo(cachedPlyrInfo, playerName, playerInfo):
    if playerName in cachedPlyrInfo:
        cachedPlyrInfo[playerName] = playerInfo
    else: cachedPlyrInfo.update({playerName:playerInfo})


# createPlayerInf: SessionID Session String -> String
# Provides the player information retreived from the API in a formated
# string, with a new line between each new piece of information. This information is then cached for 5 minutes
# to reduce the number of API calls required.
@cached(cache)
def createPlayerInf(sID, s, playerName):
    plyrInfJson = apiRequest('getplayer', sID, s, playerName)
    plyrInfList = json.loads(plyrInfJson.text)
    if len(plyrInfList) > 0:
        plyrInfDict = plyrInfList[0]
        return ('Player as of: ' + str(datetime.datetime.now().strftime("%c")) +
                        '\nPlayer: ' + plyrInfDict['Name'] +
                        '\nLevel: ' + str(plyrInfDict['Level']) +
                        '\nClan: ' + plyrInfDict['Team_Name'] +
                        '\nStatus: ' + plyrInfDict['Personal_Status_Message'] +
                        '\nWins: ' + str(plyrInfDict['Wins']) +
                        '\nLosses: ' + str(plyrInfDict['Losses']) +
                        '\nAchievements: ' + str(plyrInfDict['Total_Achievements']) +
                        '\nMastery Level: ' + str(plyrInfDict['MasteryLevel']) +
                        '\nHours Played: ' + str(plyrInfDict['HoursPlayed']))
    else:
        return ("No player with the name: " + playerName + ", was found.")


# main: Session -> String
# The main function that runs the entire program.
# Creates a new session with the Smite API, Creates a sessionID from this session,
# then loops to allow a user to input any valid player name to retrieve their player
# information. This will loop until the user enters 'N' when prompted if they would
# like to search for another player name. It will also stop if the user enters anything
# other than 'Y' at this point.
def main(s):
    newSession = sessionRequest('createsession', s)
    sessionDict = json.loads(newSession.text)
    sessionID = sessionDict['session_id']
    done = "Y"
    while done == "Y":
        playerName = input('\nPlayer Name: ').lower()
        playerInfo = createPlayerInf(sessionID, s, playerName)
        print(playerInfo)
        done = input('Would you like to search for another player? Y/N: ')


# Running the main function with the created session.
#main(s)
main(s)
