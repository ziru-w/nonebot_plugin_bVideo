
import re
import aiohttp
from nonebot.adapters.onebot.v11 import Bot,MessageEvent, GroupMessageEvent,PrivateMessageEvent,MessageSegment
from nonebot import  on_command,logger,get_bot
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot.adapters import Message
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from .utils import sendBVideo,buildMessage,findMid,getUpSendMsg,getExist,register,writeFile
from .config import bVideoPushInfoPath,bVideoSendTime,scheduler,headers,oldMessage,bVideoPushInfo,schedulerInfo,schedulerInfoPath


addBUp = on_command("收录B站UP",aliases={'收录b站up'})
@addBUp.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    text=str(args).replace('https://space.bilibili.com/','').strip()
    # midLenght=text.find('?')
    # if midLenght==-1:
    #     mid=text
    mid=re.findall('(\d.+)?[?]|\d.+',text)
    print(mid)
    if len(mid)==0:
        await addBUp.finish('形如https://space.bilibili.com/688379639')
    mid=mid[0]
    url='https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(mid)
    async with aiohttp.ClientSession() as session:
        async with session.get(url,headers=headers) as res:
            upInfo=await res.json()
    try:
        name=upInfo["data"]["name"]
    except Exception as res:
        await addBUp.send(str(res)[:100]+'\n请输入正确up个人空间链接')
        return
    # 名字不存在且mid存在删掉再赋值，名字存在且mid不存在，证明需要更正，其它二种情况直接赋值
    if bVideoPushInfo["videoUp"].get(name)==None:
        videoMidUp={}
        for up in bVideoPushInfo["videoUp"]:
            videoMidUp[bVideoPushInfo["videoUp"][up]]=up
        if videoMidUp.get(mid)!=None:
            del bVideoPushInfo["videoUp"][videoMidUp[mid]]
    bVideoPushInfo["videoUp"][name]=mid
    if bVideoPushInfo["sendDict"].get(mid)!=None:
        bVideoPushInfo["sendDict"][mid]["videoUp"]=name
        await addBPush.send('推送目录已收录up{}数据，无需再添加，请直接添加推送'.format(name))
    else:
        bVideoPushInfo["sendDict"][mid]={"qq":[],"group":[],"videoUp":name}
        await addBUp.send('收录{}执行成功'.format(name))
    writeFile(bVideoPushInfoPath,bVideoPushInfo)
    

sendB = on_command("推送b站",aliases={'推送B站'})
@sendB.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    print(str(args))
    if args.extract_plain_text()=='':
        op=0
        await sendBVideo(op,bot,event)
    else:
        message=await getUpSendMsg(args.extract_plain_text())
        await bot.send(
            event=event,
            message=message
        )


delSelfBPush = on_command("删除自己全部B站推送",block=True)
@delSelfBPush.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    ''''删除群聊自己的全部或私聊的全部'''
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text().strip()
    comText=getExist("",text,argsText)
    if isinstance(event,PrivateMessageEvent):
        id=event.get_user_id()
        pushType='qq'   
    if isinstance(event,GroupMessageEvent):
        id=str(event.group_id)
        pushType='group'
    uid=event.user_id
    # if '定时' in argsText:
    sendInfo=schedulerInfo[pushType].get(id)
    if sendInfo!=None:
        isPrivate=(pushType=='qq')
        titleList=list(sendInfo.keys())
        for title in titleList:
            if isPrivate or sendInfo[title]['id']==uid:
                scheduler.remove_job(sendInfo[title]['jobId'])
                del sendInfo[title]
        if sendInfo=={}:
            del schedulerInfo[pushType][id]
        writeFile(schedulerInfoPath,schedulerInfo)
    else:
        resMsg='无需删除'
        await delSelfBPush.finish(resMsg)
    if pushType=='qq':
        resMsg='已全部{}成功'.format(comText)
    else:
        resMsg='已全部{}成功'.format(comText)
    # else:#数据结构暂不支持
    #     sendDict=bVideoPushInfo["sendDict"]
    #     for sendMid in sendDict.keys():
    #         sendList=sendDict[sendMid][pushType]
    #         if uid in sendList:
    #             sendList.remove(uid)
    #         else:
    #             continue
    #     writeFile(bVideoPushInfoPath,bVideoPushInfo)
    #     resMsg='已删除{}'.format(uid)
    await delSelfBPush.send(resMsg)

delGroupBPush = on_command("删除群聊全部B站推送",block=True,permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER)
@delGroupBPush.handle()
async def _(bot: Bot, event: GroupMessageEvent,args: Message = CommandArg()):
    '''删除群聊全部或群内指定uid全部定时推送'''
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text().strip()
    comText=getExist("",text,argsText)
    id=event.group_id
    pushType='group'
    if '定时' in argsText:
        id=str(id)
        uid=argsText.replace('定时','').strip()
        sendInfo=schedulerInfo[pushType].get(id)
        if sendInfo!=None:
            isAll=not (uid.isdigit() and len(uid)>5)
            if not isAll:
                uid=int(uid)
            titleList=list(sendInfo.keys())
            for title in titleList:
                if isAll or sendInfo[title]['id']==uid:
                    scheduler.remove_job(sendInfo[title]['jobId'])
                    del sendInfo[title]
            if sendInfo=={}:
                del schedulerInfo[pushType][id]
            writeFile(schedulerInfoPath,schedulerInfo)
            resMsg='已全部{}成功'.format(comText)
        else:
            resMsg='无需删除'
    else:
        sendDict=bVideoPushInfo["sendDict"]
        for sendMid in sendDict.keys():
            sendList=sendDict[sendMid][pushType]
            if id in sendList:
                sendList.remove(id)
            else:
                continue
        writeFile(bVideoPushInfoPath,bVideoPushInfo)
        resMsg='已删除群聊内{}添加的推送'.format(id)
    await delGroupBPush.send(resMsg)


addBPush = on_command("添加B站推送",aliases={'删除B站推送'})
@addBPush.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text().strip()
    comText=getExist("",text,argsText)
    if argsText=='':
        await addBPush.finish('请在命令后面加上up名字')
    argsText=argsText.split()
    if len(argsText)>=2:
        upName,time=argsText
    else:
        upName=argsText[0]
        time=''
    videoUp=bVideoPushInfo["videoUp"]
    mid=findMid(upName,videoUp)
    if mid=='':
        await addBPush.finish('推送目录暂无此up，请先添加，命令/添加B站UP 名字')
    isAdd='添加' in comText
    if time!='' or not isAdd:
        await register(bot,event,upName,time,mid,isAdd)
    else:
        sendDict=bVideoPushInfo["sendDict"]
        if isinstance(event,PrivateMessageEvent):
            id=event.user_id
            sendList=sendDict[mid]['qq']
            # name=sendDict[mid]['videoUp']
        if isinstance(event,GroupMessageEvent):
            id=event.group_id
            sendList=sendDict[mid]['group']
        if id not in sendList and isAdd:
            sendList.append(id)
        elif id in sendList and not isAdd:
            sendList.remove(id)
        else:
            await addBPush.finish('重复操作')

            
        writeFile(bVideoPushInfoPath,bVideoPushInfo)
        await addBPush.send('{}已{}成功，请确认是否正确，不正确请删除并输入完整up名'.format(sendDict[mid]['videoUp'],comText))



    # argsText=argsText.replace('定时','').strip()
    # if '定时' in argsText:
    #     if schedulerInfo.get(argsText)!=None:
    #         id=argsText
    #     if pushType!='group':
    #         schedulerInfo[id]={}
    #     else:
    #         for userSendInfos in schedulerInfo.values():
    #             for userSendInfoTitle in userSendInfos.keys():
    #                 userSendInfo=userSendInfos[userSendInfoTitle]
    #                 if userSendInfo['id']==id:
    #                     userSendInfos.remove(userSendInfoTitle)
    #     writeFile(schedulerInfoPath,schedulerInfo)
    #     resMsg=await parseMsg(comText,'已全部{}成功，如：\n{}'.format(comText,str(schedulerInfo[id])))
    # else:
    #     sendDict=bVideoPushInfo["sendDict"]
    #     for sendMid in sendDict.keys():
    #         sendList=sendDict[sendMid][pushType]
    #         if id in sendList:
    #             sendList.remove(id)
    #         else:
    #             continue
    #     resMsg='已删除{}'.format(id)
    #     writeFile(bVideoPushInfoPath,bVideoPushInfo)
        
    # await addBPush.send(resMsg)