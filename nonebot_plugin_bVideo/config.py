



import json
import nonebot_plugin_apscheduler
from nonebot import  on_command,logger,get_bot
from os.path import dirname,exists
from os import mkdir
from apscheduler.schedulers.asyncio import AsyncIOScheduler
bVideoDir = dirname(__file__) + "/bVideoConfig"
bVideoPushInfoPath=bVideoDir+'/bVideoPushInfo.json'
oldMessagePath=bVideoDir +'/oldMessage.json'
scheduler = nonebot_plugin_apscheduler.scheduler  # type:AsyncIOScheduler
headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "referer":"https://www.bilibili.com/"
}
if not exists(bVideoDir):
   mkdir(bVideoDir)
if not exists(bVideoPushInfoPath):
    bVideoPushInfo={
        "maxCount":6,
        "bVideoSendTime":[{"hour":8,"minute":2}],
        "videoUp": {},
        "sendDict": {}
    }
    with open(bVideoPushInfoPath,'w',encoding='utf-8') as fp:
       json.dump(bVideoPushInfo,fp,ensure_ascii=False)
oldMessage={}
with open(bVideoPushInfoPath,'r',encoding='utf-8') as fp:
    bVideoPushInfo=json.loads(fp.read())
# with open(bVideoDir +'/oldMessage.json','r',encoding='utf-8') as fp:
#     oldMessage=json.loads(fp.read())
bVideoSendTime=bVideoPushInfo["bVideoSendTime"]
logger.info('载入bVideoSendTime：{}'.format(bVideoSendTime))
def writeFile(path,content):
    with open(path,'w',encoding='utf-8') as fp:
        json.dump(content,fp,ensure_ascii=False)

def readFile(path,content={}):
    if not exists(path):
        with open(path,'w',encoding='utf-8') as fp:
            json.dump(content,fp,ensure_ascii=False)
    with open(path,'r',encoding='utf-8') as fp:
        replyTextJson = json.loads(fp.read())
    return replyTextJson
content={"qq":{},"group":{}}
schedulerInfoPath=bVideoDir+'/schedulerInfo.json'
schedulerInfo=readFile(schedulerInfoPath,content)

