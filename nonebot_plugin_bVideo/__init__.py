import requests
import json
from os.path import dirname,exists
from os import mkdir
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import nonebot_plugin_apscheduler
from nonebot.adapters.onebot.v11 import Bot,MessageEvent, GroupMessageEvent,PrivateMessageEvent
from nonebot import  on_command,logger,get_bot


bVideo_dir = dirname(__file__) + "/bVideoConfig"

scheduler = nonebot_plugin_apscheduler.scheduler  # type:AsyncIOScheduler
headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "referer":"https://www.bilibili.com/"
}
if not exists(bVideo_dir):
   mkdir(bVideo_dir)
if not exists(bVideo_dir+'/bVideoPushInfo.json'):
    bVideoPushInfo={
        "maxCount":6,
        "bVideoSendTime":[{"hour":8,"minute":2}],
        "videoUp": {},
        "sendDict": {}
    }
    with open(bVideo_dir+'/bVideoPushInfo.json','w',encoding='utf-8') as fp:
       json.dump(bVideoPushInfo,fp,ensure_ascii=False)
oldMessage={}
with open(bVideo_dir+'/bVideoPushInfo.json','r',encoding='utf-8') as fp:
    bVideoPushInfo=json.loads(fp.read())
# with open(bVideo_dir +'/oldMessage.json','r',encoding='utf-8') as fp:
#     oldMessage=json.loads(fp.read())
bVideoSendTime=bVideoPushInfo["bVideoSendTime"]
logger.info('载入bVideoSendTime：{}'.format(bVideoSendTime))


async def send_bVideo_everyday():
    await sendBVideo(op=1)


# 根据配置的参数，注册定时任务,每天发送
for time in bVideoSendTime:
    logger.info("time:{}".format(time))
    scheduler.add_job(send_bVideo_everyday, "cron", hour=time['hour'], minute=time['minute'])

addBUp = on_command("收录B站UP",aliases={'收录b站up'})
@addBUp.handle()
async def _(bot: Bot, event: MessageEvent):
    with open(bVideo_dir +'/bVideoPushInfo.json','r',encoding='utf-8') as fp:
        bVideoPushInfo=json.loads(fp.read())
    text=event.get_plaintext()
    mid=text[7:].strip().replace('https://space.bilibili.com/','')
    if not mid.isdigit():
        await addBPush.finish('请不要在链接后面加东西或啥也没，形如https://space.bilibili.com/688379639,不需要?以后的东西')
    upInfo=requests.get('https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(mid),headers=headers).json()
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
        await addBPush.send('推送目录已收录up数据，无需再添加，请直接添加推送')
    else:
        bVideoPushInfo["sendDict"][mid]={"qq":[],"group":[],"videoUp":name}
        await addBUp.send('执行成功')
    with open(bVideo_dir +'/bVideoPushInfo.json','w',encoding='utf-8') as fp:
        json.dump(bVideoPushInfo,fp,ensure_ascii=False)
    


sendB = on_command("推送b站",aliases={'推送B站'})
@sendB.handle()
async def _(bot: Bot, event: MessageEvent):
    op=0
    await sendBVideo(op,bot,event)

addBPush = on_command("添加B站推送",aliases={'删除B站推送'})
@addBPush.handle()
async def _(bot: Bot, event: MessageEvent):
    with open(bVideo_dir +'/bVideoPushInfo.json','r',encoding='utf-8') as fp:
        bVideoPushInfo=json.loads(fp.read())
    text=event.get_plaintext()
    op=text[1:3]
    text=text[7:].strip()
    if text=='':
        await addBPush.finish('请在命令后面加上up名字')
    videoUp=bVideoPushInfo["videoUp"]
    mid=''
    for up in videoUp:
        if text in up:
            mid=videoUp[up]
    if mid=='':
        await addBPush.finish('推送目录暂无此up，请先添加，命令/添加B站UP 名字')
    sendDict=bVideoPushInfo["sendDict"]
    if isinstance(event,PrivateMessageEvent):
        if event.user_id not in sendDict[mid]['qq']:
            if op=='添加':
                sendDict[mid]['qq'].append(event.user_id)
        else:
            if op=='删除':
                sendDict[mid]['qq'].remove(event.user_id)
        # name=sendDict[mid]['videoUp']
    if isinstance(event,GroupMessageEvent):
        if event.user_id not in sendDict[mid]['qq']:
            if op=='添加':
                sendDict[mid]['group'].append(event.group_id)
        else:
            if op=='删除':
                sendDict[mid]['group'].remove(event.user_id)
        
    with open(bVideo_dir +'/bVideoPushInfo.json','w',encoding='utf-8') as fp:
        json.dump(bVideoPushInfo,fp,ensure_ascii=False)
    await addBPush.send('{}已{}成功'.format(sendDict[mid]['videoUp'],op))
        
async def sendBVideo(op=0,bot: Bot='', event: MessageEvent=''):
    with open(bVideo_dir +'/bVideoPushInfo.json','r',encoding='utf-8') as fp:
        bVideoPushInfo=json.loads(fp.read())
    baseUrl='https://api.bilibili.com/x/space/arc/search?mid='  
    i=0
    maxCount=bVideoPushInfo["maxCount"]
    for mid in bVideoPushInfo["sendDict"].keys():
        if i>=maxCount:
            break
        message=requests.get(baseUrl+mid,headers=headers).json()
        message=message["data"]["list"][ "vlist"][0]
        message='标题:{}\n链接:\nhttps://www.bilibili.com/video/{}'.format(message["title"],message["bvid"])
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
                sendDict=bVideoPushInfo["sendDict"][mid]
                for qq in sendDict['qq']:    
                    await get_bot().send_private_msg(user_id=qq, message=message)
                for group in sendDict['group']:    
                    await get_bot().send_group_msg(group_id=group, message=message)
        i+=1
                
    if op!=0:
        with open(bVideo_dir +'/oldMessage.json','w',encoding='utf-8') as fp:
            json.dump(oldMessage,fp,ensure_ascii=False)

