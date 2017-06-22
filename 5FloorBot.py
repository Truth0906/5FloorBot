import traceback
import sys
import time
import random
import json
import getpass
sys.path.append('..\\PTTCrawlerLibrary')
import PTT
print('Welcome to 5FloorBot v 1.0.17.0622')

# If you want to automatically login define Account.txt
# {"ID":"YourID", "Password":"YourPW"}
try:
    with open('Account.txt', encoding = 'utf8') as AccountFile:
        Account = json.load(AccountFile)
        ID = Account['ID']
        Password = Account['Password']
        print('Auto ID password mode')
except FileNotFoundError:
    ID = input('Input ID: ')
    Password = getpass.getpass('Input password: ')

try:
    with open('5FloorBotOption.txt', encoding = 'utf8') as PushListFile:
        PushList = json.load(PushListFile)
except FileNotFoundError:
    print('5FloorBotOption.txt is not found')
    sys.exit()

def isIDinPost(PostContent):
    
    LetterList = 'abcdefghijklmnopqrstuvwxyz'
    BigUpperLetterList = 'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
    BigLowerLetterList = 'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
    
    for i in range(len(BigUpperLetterList)):
        PostContent = PostContent.replace(list(BigUpperLetterList)[i], list(LetterList)[i])
        PostContent = PostContent.replace(list(BigLowerLetterList)[i], list(LetterList)[i])
        
    for i in list(ID):
        if not i.lower() in PostContent.lower():
            return False
    return True
'''
TestString = 'QQ Ｃｏｄｉｎｇｍａｎ'
print(TestString)
print(isIDinPost(TestString))
print(TestString)
sys.exit()
'''
Board = PushList['Board']
Retry = True

Startup = True

PTTCrawler = PTT.Crawler(ID, Password, False)
if not PTTCrawler.isLoginSuccess():
    PTTCrawler.Log('Login fail')
else:
    PTTCrawler.setLogLevel(PTTCrawler.LogLevel_DEBUG)
    LastIndex = 0
    LastIndexList = [0]
    
    NoFastPushWait = False

    PTTCrawler.Log('Start detect new post in ' + Board)
    while Retry:
        try:
                
            if not len(LastIndexList) == 0:
                LastIndex = LastIndexList.pop()
            ErrorCode, LastIndexList = PTTCrawler.getNewPostIndexList(Board, LastIndex)
            if ErrorCode != PTTCrawler.Success:
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
                    if ErrorCode == PTTCrawler.PostDeleted:
                        PTTCrawler.Log('Post has been deleted')
                        continue
                    if ErrorCode == PTTCrawler.WebFormatError:
                        PTTCrawler.Log('Web structure error')
                        continue
                    if ErrorCode != PTTCrawler.Success:
                        PTTCrawler.Log('Get post by index fail')
                        continue
                    if Post == None:
                        PTTCrawler.Log('Post is empty')
                        continue
                    #PTTCrawler.Log(Post.getPostContent())
                    if isIDinPost(Post.getPostContent()) or isIDinPost(Post.getTitle()):
                        PTTCrawler.Log('User is not allow push')
                        continue
                    
                    if '五樓' in Post.getOriginalData() or '5樓' in Post.getOriginalData() or '5 樓' in Post.getOriginalData():
                        PTTCrawler.Log('Detect 5 floor trap')
                        continue
                        
                    for i in range(len(Post.getPushList()), 5):
                        PushContent = PushList[str(i + 1)]
                        #PTTCrawler.Log('Push: ' + PushContent)
                        ErrorCode = PTTCrawler.pushByIndex(Board, PTTCrawler.PushType_Push, PushContent, NewPostIndex)
                        
                        if ErrorCode == PTTCrawler.Success:
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
    