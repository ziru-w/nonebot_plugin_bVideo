


import json
import re
from time import sleep,time as ctime
import aiohttp
from nonebot import  on_command,logger,get_bot
from nonebot.adapters.onebot.v11 import Bot,MessageEvent, GroupMessageEvent,PrivateMessageEvent,MessageSegment
from .config import bVideoPushInfoPath,bVideoSendTime,scheduler,headers,oldMessage,bVideoPushInfo,writeFile,schedulerInfoPath,schedulerInfo,oldMessagePath




async def send_bVideo_everyday():
    await sendBVideo(op=1)
async def sendBVideo(op=0,bot: Bot='', event: MessageEvent=''):
    writeFile(bVideoPushInfoPath,bVideoPushInfo)
    i=0
    maxCount=bVideoPushInfo["maxCount"]
    for mid in bVideoPushInfo["sendDict"].keys():
        print(mid)
        if i>=maxCount:
            break
        sendDict=bVideoPushInfo["sendDict"][mid]
        message=await buildMessage(sendDict,mid)        
        print(message)
        if op==0:
            await bot.send(
                event=event,
                message=message
            )
        else: 
            if oldMessage.get(mid)==None:
                oldMessage[mid]=''
            print(oldMessage[mid], message!=oldMessage[mid])
            if message!=oldMessage[mid]:
                oldMessage[mid]=message
                for qq in sendDict['qq']:    
                    await get_bot().send_private_msg(user_id=qq, message=message)
                for group in sendDict['group']:    
                    await get_bot().send_group_msg(group_id=group, message=message)
        i+=1
                
    if op!=0:
        writeFile(oldMessagePath,oldMessage)



async def buildMessage(sendDict:dict,mid,op=0):
    url='https://api.bilibili.com/x/space/arc/search?mid={}'.format(mid)
    async with aiohttp.ClientSession() as session:
        async with session.get(url,headers=headers) as res:
            message=await res.json()
    message=message["data"]["list"][ "vlist"][0]   
    # await easyCommand.send(MessageSegment.share(message["bvid"],sendDict['videoUp']+':'+message["title"],message['description'],message['pic']))
    message='UP主:{}\n标题:{}\n链接:\nhttps://www.bilibili.com/video/{}'.format(sendDict['videoUp'],message["title"],message["bvid"])
    if op==1:
        message=MessageSegment.share(message["bvid"],sendDict['videoUp']+':'+message["title"],message['description'],message['pic'])
    return message

def findMid(name,videoUp:dict):
    mid=''
    if videoUp.get(name):
        return videoUp[name]
    for up in videoUp:
        if name in up:
            mid=videoUp[up]
    return mid

async def getUpSendMsg(args,bVideoPushInfo={}):
    if bVideoPushInfo=={}:
        writeFile(bVideoPushInfoPath,bVideoPushInfo)
    mid=findMid(args,bVideoPushInfo["videoUp"])
    message=await buildMessage(bVideoPushInfo['sendDict'][mid],mid) 
    return message

async def sendSingle(mid,id,sendTpe):
    message=await buildMessage(bVideoPushInfo['sendDict'][mid],mid) 
    if sendTpe=='qq':    
        await get_bot().send_private_msg(user_id=id, message=message)
    else:    
        await get_bot().send_group_msg(group_id=id, message=message)

def getExist(plainCommandtext:str,wholeMessageText:str,argsText:str):
    commandText=wholeMessageText.replace(argsText,'').strip()
    if plainCommandtext=='':
        return commandText
    else:
        return plainCommandtext in commandText





def parseTimeArea(inputTime,timeType):
    if timeType=='h':
        if inputTime>24 or inputTime<0:
            return False
    else:
        if inputTime>59 or inputTime<0:
            return False
    return True

def parseNum(inputTime:str,timeType:str,cornType):
    '1,*/2,0-59,*'
    if timeType==0:
        timeType='h'
    else:
        timeType='noH'
    if cornType==0:
        inputTime=int(inputTime)
        if not parseTimeArea(inputTime,timeType):
            return False
        return str(inputTime)
    elif cornType==1:
        inputTime=int(inputTime[2:])
        if inputTime<1:
            return False
        return '*/{}'.format(inputTime)
    elif cornType==2:
        inputTime=inputTime.split('-')
        temp=''
        for index,tempi in enumerate(inputTime):
            if not parseTimeArea(inputTime[index],timeType):
                return False
            temp=temp+inputTime[index]+'-'
        return temp[:-1]
    return inputTime


def parseTimeData(time:list,isSuper:False):
    # pattern=["^[0-9]{1,2}$", "^[*][/][0-9]{1,2}$","^[0-9]{1,2}-[0-9]{1,2}$","^[*]$"]
    pattern=["^[0-9]{1,2}$"]
    print(time)
    errorData=-1
    for i,inputTime in enumerate(time):
        for cornType,patterni in enumerate(pattern):
            select=re.match(patterni,inputTime)
            if select:
                isCorrect=parseNum(inputTime,i,cornType)
                if not isCorrect:
                    errorData=i
                    return errorData #收束数据超限
                time[i]=isCorrect
                break # 真，结束循环
            if (cornType==0 and not isSuper) or cornType+1==len(pattern): # 成功即break,故至此者非第一个匹配非超管F或最后一轮仍未break，判错
                errorData=i
                return errorData #收束未匹配
    return errorData # 全成功





def getTime():
    sleep(0.001)
    content=ctime()
    content=str(content)
    return content
async def register(bot: Bot, event: MessageEvent,title,time,content,isRegister,isSuper=True):
    if isinstance(event,GroupMessageEvent):
        msgType='group'
        id=str(event.group_id)
    else:
        msgType='qq'
        id=event.get_user_id()
    uid=event.user_id
    schedulerTypedInfo=schedulerInfo[msgType]
    if isRegister:
        if schedulerTypedInfo.get(id)==None:
            schedulerTypedInfo[id]={}
        tempInfo=schedulerTypedInfo[id].get(title)
        if tempInfo!=None:
            await bot.send(event=event,message='请先删除定时任务{}:{}'.format(title,tempInfo))
            return
        time=time.split('.')
        errorData=parseTimeData(time,isSuper)
        if errorData!=-1:
            await bot.send(event=event,message='{}中，第{}个数据{}非法，或过于危险，注册失败'.format(time,errorData,time[errorData]))
            return
        timeNum=len(time)
        if timeNum<3:
            time=time+['0','0','0'][:3-timeNum]
        print(time)
        tempInfo={'time':time,'content':content,'type':msgType,'id':uid,'jobId':getTime()}
        schedulerTypedInfo[id][title]=tempInfo
        scheduler.add_job(sendSingle, "cron", hour=time[0], minute=time[1],args=[tempInfo['content'],id,tempInfo['type']],id=tempInfo['jobId'])
        writeFile(schedulerInfoPath,schedulerInfo)
        await bot.send(event=event,message='已注册\n{}:\n{},请确认up名{}否正确，不正确请删除并输入完整up名'.format(title,tempInfo,bVideoPushInfo['sendDict'][content]["videoUp"]))
    else:
        if schedulerTypedInfo.get(id)==None or schedulerTypedInfo[id].get(title)==None:
            await bot.send(event=event,message='{}不存在哦'.format(title))
            return
        tempInfo=schedulerTypedInfo[id][title]
        scheduler.remove_job(tempInfo['jobId'])
        del schedulerTypedInfo[id][title]
        if schedulerTypedInfo[id]=={}:
            del schedulerTypedInfo[id]
        writeFile(schedulerInfoPath,schedulerInfo)
        await bot.send(event=event,message='已删除:\n{}'.format(tempInfo))

for schedulerTypedInfo in schedulerInfo.values():
    for sendId in schedulerTypedInfo.keys():
        userSendInfos=schedulerTypedInfo[sendId]
        for userSendInfoTitle in userSendInfos.keys():
            userSendInfo=userSendInfos[userSendInfoTitle]
            time=userSendInfo['time']
            scheduler.add_job(sendSingle, "cron", hour=time[0], minute=time[1],second=time[2],args=[userSendInfo['content'],sendId,userSendInfo['type']],id=userSendInfo['jobId'])

# 根据配置的参数，注册定时任务,每天发送
for time in bVideoSendTime:
    logger.info("time:{}".format(time))
    scheduler.add_job(send_bVideo_everyday, "cron", hour=time['hour'], minute=time['minute'])




# for sendId in schedulerInfo.keys():
#     userSendInfos=schedulerInfo[sendId]
#     for userSendInfoTitle in userSendInfos.keys():
#         userSendInfo=userSendInfos[userSendInfoTitle]
#         time=userSendInfo['time']
#         scheduler.add_job(sendSingle, "cron", hour=time[0], minute=time[1],second=time[2],args=[userSendInfo['content'],userSendInfo['id'],userSendInfo['type']],id=userSendInfo['jobId'])


