import traceback
import sys
import time
import random
import json
import getpass
sys.path.append('..\\PTTCrawlerLibrary')
import PTT

# If you want to automatically login define Account.txt
# {"ID":"YourID", "Password":"YourPW"}
try:
    with open('Account.txt', encoding = 'utf8') as AccountFile:
        Account = json.load(AccountFile)
        ID = Account['ID']
        Password = Account['Password']
except FileNotFoundError:
    print('Welcome to 5FloorBot v 1.0.17.0618')
    ID = input('Input ID: ')
    Password = getpass.getpass('Input password: ')

try:
    with open('5FloorBotOption.txt', encoding = 'utf8') as PushListFile:
        PushList = json.load(PushListFile)
except FileNotFoundError:
    print('5FloorBotOption.txt is not found')
    sys.exit()

Board = PushList['Board']
Retry = True

Startup = True

while Retry:
    PTTCrawler = PTT.Crawler(ID, Password, False)
    if not PTTCrawler.isLoginSuccess():
        PTTCrawler.Log('Login fail')
    else:
        #PTTCrawler.setLogLevel(PTT.LogLevel_DEBUG)
        LastIndex = 0
        LastIndexList = [0]
        
        NoFastPushWait = False

        PTTCrawler.Log('Start detect new post in ' + Board)
        while Retry:
            try:
                    
                if not len(LastIndexList) == 0:
                    LastIndex = LastIndexList.pop()
                ErrorCode, LastIndexList = PTTCrawler.getNewPostIndexList(Board, LastIndex)
                if ErrorCode != PTT.Success:
                    PTTCrawler.Log('Get newest list error: ' + str(ErrorCode))
                    time.sleep(1)
                    continue
                
                if not len(LastIndexList) == 0:
                    PTTCrawler.Log('Detected ' + str(len(LastIndexList)) + ' new post')
                    
                    if Startup:
                        PTTCrawler.Log('Pass the post alread exist')
                        Startup = False
                        continue
                    for NewPostIndex in LastIndexList:
                
                        PTTCrawler.Log('Detected ' + str(NewPostIndex))
                        
                        ErrorCode, Post = PTTCrawler.getPostInfoByIndex(Board, NewPostIndex)
                        if ErrorCode == PTT.PostDeleted:
                            PTTCrawler.Log('Post has been deleted')
                            continue
                        if ErrorCode == PTT.WebFormatError:
                            PTTCrawler.Log('Web structure error')
                            continue
                        if ErrorCode != PTT.Success:
                            PTTCrawler.Log('Get post by index fail')
                            continue
                        if Post == None:
                            PTTCrawler.Log('Post is empty')
                            continue
                        #PTTCrawler.Log(Post.getPostContent())
                        if ID in Post.getPostContent():
                            PTTCrawler.Log('User is not allow push')
                            continue
                        
                        if '五樓' in Post.getOriginalData() or '5樓' in Post.getOriginalData() or '5 樓' in Post.getOriginalData():
                            PTTCrawler.Log('Detect 5 floor trap')
                            continue
                            
                        for i in range(len(Post.getPushList()), 5):
                            PushContent = PushList[str(i + 1)]
                            #PTTCrawler.Log('Push: ' + PushContent)
                            ErrorCode = PTTCrawler.pushByIndex(Board, PTTCrawler.PushType_Push, PushContent, NewPostIndex)
                            
                            if ErrorCode == PTT.Success:
                                #PTTCrawler.Log('Push success')
                                pass
                            else:
                                PTTCrawler.Log('Push fail')
                                break
                        PTTCrawler.Log('Index ' + str(NewPostIndex) + ' complete')
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
                Retry = True
                break
            except ConnectionAbortedError:
                Retry = True
                break
            except Exception:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                Retry = True
                break