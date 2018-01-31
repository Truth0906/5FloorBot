import traceback
import sys
import time
import random
import json
import getpass
from PTTLibrary import PTT

# If you want to automatically login define Account.txt
# {"ID":"YourID", "Password":"YourPW"}
try:
    with open('Account.txt', encoding = 'utf8') as AccountFile:
        Account = json.load(AccountFile)
        ID = Account['ID']
        Password = Account['Password']
except FileNotFoundError:
    print('Welcome to IDTracker v 1.0.18.0131')
    ID = input('Input ID: ')
    Password = getpass.getpass('Input password: ')

try:
    with open('IDTrackerOption.txt', encoding = 'utf8') as OptionFile:
        IDTrackerOption = json.load(OptionFile)
except FileNotFoundError:
    print('IDTrackerOption.txt is not found')
    sys.exit()

IDState_Unknow =                    0


IDList = IDTrackerOption['IDList']

PTTCrawler = PTT.Library(ID, Password, False)
if not PTTCrawler.isLoginSuccess():
    PTTCrawler.Log('Login fail')
else:
    #PTTCrawler.setLogLevel(PTT.LogLevel_DEBUG)
    PTTCrawler.Log('Detect ID List:')
    
    IDStatus = {}
    
    for ID in IDList:
        PTTCrawler.Log(ID)
        IDStatus[ID] = IDState_Unknow
        
    PTTCrawler.Log('--------------------')
    
    while True:
        try:
            for ID in IDList:
                PTTCrawler.Log(ID)
                ErrorCode, UserInfo = PTTCrawler.getUserInfo(ID)
                if ErrorCode == PTTCrawler.NoUser:
                    PTTCrawler.Log('No such user')
                    continue
                if ErrorCode != PTTCrawler.Success:
                    PTTCrawler.Log('getUserInfo fail error code: ' + str(ErrorCode))
                    continue
                
                PTTCrawler.Log
                
        except KeyboardInterrupt:
            '''
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            '''
            PTTCrawler.Log('Interrupted by user')
            PTTCrawler.logout()
            sys.exit()
        except EOFError:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
        except ConnectionAbortedError:
            pass
