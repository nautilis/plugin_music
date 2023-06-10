##  音乐插件
这个项目是[chatgpt-on-wechat](https://github.com/zhayujie/chatgpt-on-wechat) 的音乐插件, 基于[网易云音乐API](https://github.com/Binaryify/NeteaseCloudMusicApi)（需要自己搭一个本地服务）,实现以下功能：
- [x] 使用chatgpt 推荐音乐并发送播放链
- [x] 点歌

### 使用方式
#### 部署网易云API 
见：https://github.com/Binaryify/NeteaseCloudMusicApi
#### 插件集成
1. 把项目解压到chatgpt-on-wechat/plugins/music/ 目录下
2. 配置 chatgpt-on-wechat/plugins/plugins.json
```json
{
  "Music": {
    "enabled": true,
    "priority": 0
  }
}
```
3. 重新启动chatgpt-on-wechat
#### 触发
<关键字><空格><指令>:<内容>
- 点歌: `music 点歌:可惜我是水瓶座-杨千嬅`
- 推荐: `music 推荐一手粤语歌曲`

#### 效果



