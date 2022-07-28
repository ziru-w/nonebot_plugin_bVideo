# nonebot_plugin_bVideo
一个基于NoneBot2的插件，用于处理推送B站up主最新视频的插件


A NoneBot2-based plugin for processing plugins that push the latest videos of the B station up master


下载方法 pip install nonebot_plugin_bVideo


1./收录B站UP 个人空间链接 用于收录B站UP的mid，形如/收录B站UP https://space.bilibili.com/688379639 其中688379639即为mid

2./推送b站 返回收录的前maxCount个up的视频标题加链接,maxCount默认为6 

3./添加B站推送 up主名字 /删除B站推送 up主名字 群聊发推送到该群，私聊推送到发送者 up名字优先为实际up名，允许为实际up名的部分，但只返回第一个结果，请尽量一样 权限为群聊的所有人，私聊的自己 此处添加的是统一定时推送，时间由配置项"bVideoSendTime"决定

4./添加B站推送 up主名字 时间 /删除B站推送 up主名字 定时  时间以.隔开，形如/添加B站推送 武忠祥 21.23.0 /添加B站推送 武忠祥 定时  此处添加的是随意定时推送

5./删除群聊全部B站推送定时 /删除群聊全部B站推送 /删除自己全部B站推送定时 /删除自己全部B站推送

权限为群聊的自己添加的，私聊的全部 +定时删定时，管理员之类可以删群聊内别人添加的全部，不加定时删群统一定时推送

