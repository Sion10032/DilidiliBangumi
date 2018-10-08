# DilidiliBangumi

DilidiliBangumi是一个命令行界面的D站是视频解析程序。\
主要功能为获取D站的新番时间表，并尝试解析出其视频链接。

## 用法

**sw [weekday]**\
(SelectWeekday)\
用于选择星期几， weekday的范围为1-7，在不输入参数的情况下将会跳转到目前的日期。\
同时，使用sw命令后会自动调用la命令。

**sa [animeNum = 0]**\
(SelectAnime)\
用于选择番剧。\
使用后会自动调用ls命令。

**la**\
(ListAnimes)\
用于显示当前选择星期的番剧。

**ls**\
(ListSections)\
用于显示当前选择番剧的目录。

**play [secNum]**\
(Play)\
用于播放番剧，不传参数的情况下默认播放最新一集。\
注意：使用前一定要使用cfg命令设置播放器路径.

**pd [url]**\
(PlayDirected)\
用于直接从视频页面链接解析出地址并播放，\
参数是视频页面的url。

**cfg [set key value]**\
(config)\
用于显示或设置当前设置项。\
例如：cfg set PlayerPath C:\Program Files\PotPlayer\PotPlayerMini64.exe\
注意：设置路径时最后的路径可以带空格，不需要使用引号包住路径。