<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/picmcstat/picmcstat.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# NoneBot-Plugin-PicMCStat

_✨ Minecraft 服务器 MOTD 查询 图片版 ✨_

<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
<a href="https://pdm.fming.dev">
  <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>
<a href="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/5bc0f141-d1ec-430a-8d21-0e312188fdae">
  <img src="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/5bc0f141-d1ec-430a-8d21-0e312188fdae.svg" alt="wakatime">
</a>

<br />

<a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/pyd-v1-or-v2.json" alt="Pydantic Version 1 Or 2" >
</a>
<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/lgc-NB2Dev/nonebot-plugin-picmcstat.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-picmcstat">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-picmcstat.svg" alt="pypi">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-picmcstat">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-picmcstat" alt="pypi download">
</a>

<br />

<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-picmcstat:nonebot_plugin_picmcstat">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin%2Fnonebot-plugin-picmcstat" alt="NoneBot Registry">
</a>
<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-picmcstat:nonebot_plugin_picmcstat">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin-adapters%2Fnonebot-plugin-picmcstat" alt="Supported Adapters">
</a>

</div>

## 📖 介绍

插件实际上是可以展示 **玩家列表**、**Mod 端信息 以及 Mod 列表（还未测试）** 的，这里没有找到合适的例子所以没在效果图里展示出来，如果遇到问题可以发 issue

插件包体内并没有自带图片内 Unifont 字体，需要的话请参考 [这里](#字体) 安装字体

<details open>
<summary>效果图</summary>

![example](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/picmcstat/example.png)  
![example](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/picmcstat/example_je.png)

</details>

## 💿 安装

### 插件

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-picmcstat
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-picmcstat
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-picmcstat
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-picmcstat
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-picmcstat
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_picmcstat"
]
```

</details>

### 字体

字体文件请自行去自行去 [这里](http://ftp.gnu.org/gnu/unifont/unifont-15.0.01/unifont-15.0.01.ttf) 下载
如需将英文部分变为游戏内字体，请另外下载安装 [这个](https://resources.download.minecraft.net/3d/3d009535ec7860c29603cd66cdb4db5c8b4aefd2) 字体（请自行修改文件扩展名为 `.ttf`）

将字体文件直接安装在系统中即可  
如果不行，请尝试右键字体文件点击 `为所有用户安装`  
如果还是不行，请尝试修改插件字体配置

## ⚙️ 配置

### `MCSTAT_FONT` - 使用的字体名称 / 路径

默认：`["Minecraft Seven", "unifont"]`

请按需自行更改

### `MCSTAT_SHOW_ADDR` - 是否在生成的图片中显示服务器地址

默认：`False`

### `MCSTAT_SHOW_DELAY` - 是否显示测试延迟

默认：`True`

### `MCSTAT_SHOW_MODS` - 是否在生成的图片中显示 Mod 列表

默认：`False`

由于某些整合包服务器的 Mod 数量过多，导致图片生成时间过长，且容易炸内存，所以默认不显示

### `MCSTAT_REPLY_TARGET` - 是否回复指令发送者

默认：`True`

### `MCSTAT_SHORTCUTS` - 快捷指令列表

这个配置项能够帮助你简化一些查询指令

此配置项的类型是一个列表，里面的元素需要为一个特定结构的字典：

- `regex` - 用于匹配指令的正则，例如 `^查服$`  
  （注意，nb2 以 JSON 格式解析配置项，所以当你要在正则表达式里表示`\`时，你需要将其转义为`\\`）
- `host` - 要查询的服务器地址，格式为 `<IP>[:端口]`，  
  例如 `hypixel.net` 或 `example.com:1919`
- `type` - 要查询服务器的类型，`je` 表示 Java 版服，`be` 表示基岩版服
- `whitelist` - （仅支持 OneBot V11 适配器）群聊白名单，只有里面列出的群号可以查询，可以不填来对所有群开放查询

最终的配置项看起来是这样子的，当你发送 `查服` 时，机器人会把 EaseCation 服务器的状态发送出来

```env
MCSTAT_SHORTCUTS='
[
  {"regex": "^查服$", "host": "asia.easecation.net", "type": "be"}
]
'
```

### `MCSTAT_RESOLVE_DNS` - 是否由插件解析 DNS 记录

默认：`True`

是否由插件解析一遍 DNS 记录后再进行查询，  
如果你的服务器在运行 Clash 等拦截了 DNS 解析的软件，且查询部分地址时遇到了问题，请尝试关闭此配置项  
此配置项不影响 Java 服务器的 SRV 记录解析

### `MCSTAT_QUERY_TWICE` - 是否查询两遍服务器状态

默认：`True`

由于第一次测得的延迟一般不准，所以做了这个配置，  
开启后每次查询时，会丢掉第一次的结果再查询一次，且使用第二次查询到的结果

### `MCSTAT_JAVA_PROTOCOL_VERSION` - Motd Java 服务器时向服务器发送的客户端协议版本

默认：`767`

## 🎉 使用

发送 `motd` 指令 查看使用指南

![usage](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/picmcstat/usage.png)

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[1105946125](https://jq.qq.com/?_wv=1027&k=Z3n1MpEp)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [pil-utils](https://github.com/MeetWq/pil-utils)

超好用的 Pillow 辅助库，wq 佬是叠！快去用 awa

## 💰 赞助

**[赞助我](https://blog.lgc2333.top/donate)**

感谢大家的赞助！你们的赞助将是我继续创作的动力！

## 📝 更新日志

### 0.7.1

- 修复文字下对齐的 Bug

### 0.7.0

- 适配 pil-utils 0.2
- 更改配置项 `MCSTAT_FONT` 类型为 `List[str]`（`str` 仍然受支持）

### 0.6.3

- fix [#22](https://github.com/lgc-NB2Dev/nonebot-plugin-picmcstat/issues/22)

### 0.6.2

- 允许自定义向 Java 服务器发送的客户端协议版本，且提高默认协议版本以解决部分服务器 Motd 渐变显示异常的问题

### 0.6.1

- fix [#21](https://github.com/lgc-NB2Dev/nonebot-plugin-picmcstat/issues/21)

### 0.6.0

- 适配 Pydantic V1 & V2

### 0.5.1

- 修复 玩家 / Mod 列表 中出现的一些 Bug ~~果然又出 Bug 了~~
- 添加配置项 `MCSTAT_SHOW_DELAY`、`MCSTAT_QUERY_TWICE`

### 0.5.0

- 换用 Alconna 支持多平台
- 快捷指令支持多平台（`whitelist` 依然仅支持 OneBot V11）
- 添加配置项 `MCSTAT_RESOLVE_DNS`
- 部分代码重构 ~~Bug 海与屎山代码又增加了~~

### 0.4.0

- 修复修复无法解析中文域名 IP 的错误（[#13](https://github.com/lgc-NB2Dev/nonebot-plugin-picmcstat/issues/13)）
- 使用 SAA 支持多适配器（shortcut 依然仅支持 OB V11）
- 添加配置项 `MCSTAT_REPLY_TARGET`

### 0.3.5

- 修复上个版本的小 Bug

### 0.3.4

- 修复无法正常绘制 Mod 列表的情况
- 增加显示 Mod 列表的配置项 (`MCSTAT_SHOW_MODS`)

### 0.3.3

- 修复特殊情况下玩家列表排版错误的问题（虽然现在使用其他字体的情况下还是有点问题）
- 添加显示服务器地址的配置项 (`MCSTAT_SHOW_ADDR`)

### 0.3.2

- 🎉 NoneBot 2.0 🚀

### 0.3.1

- 修复文本内含有 `§k` 时报错的问题

### 0.3.0

- 弃用 `nonebot-plugin-imageutils`，换用 `pil-utils`
- 支持了更多字体样式
- 支持自定义字体

### 0.2.7

- 修复 `shortcut` 的 `whitelist` 的奇怪表现

### 0.2.6

- 修复 `shortcut` 中没有 `whitelist` 项会报错的问题

### 0.2.5

- `shortcut` 加入 `whitelist` 项配置触发群白名单

### 0.2.4

- 修复玩家列表底下的多余空行

### 0.2.3

- 修复 JE 服务器 Motd 中粗体意外显示为蓝色的 bug

### 0.2.2

- 修复 motd 前后留的空去不干净的问题
- 优化玩家列表显示效果

### 0.2.1

- 修复当最大人数为 0 时出错的问题

### 0.2.0

- 加入快捷指令，详见配置项
- 修复某些 JE 服无法正确显示 Motd 的问题
-

### 0.1.1

- 将查 JE 服时的 `游戏延迟` 字样 改为 `测试延迟`
