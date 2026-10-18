# 杀戮尖塔 2 全解锁脚本

**中文** | [English](README.en.md)

![解锁后的游戏统计页](docs/screenshot.png)

一键把《杀戮尖塔 2》（Slay the Spire 2）的百科全书、时间线、游戏模式、进阶全部解锁。

**它只改你电脑上的存档文件，不改游戏本体，也不需要装 mod。**

> ⚠️ 这是玩家自制的非官方工具，与 Mega Crit 无关。《Slay the Spire》及相关名称、截图中的游戏画面版权归 Mega Crit 所有。改存档风险自负，运行前脚本会自动备份。

适用版本：游戏 **v0.107.1**（其他版本见下面的“游戏更新了怎么办”）。

---

## 能解锁什么

| 内容 | 解锁后 |
|---|---|
| 卡牌 | 全部 577 张 |
| 遗物 | 全部 296 个 |
| 药水 | 全部 63 种 |
| 事件 | 全部 |
| 时间线（历史节点） | 全部 57 个 |
| 角色 | 全部 5 个（含故障机器人） |
| 单人模式 | **每日挑战**、**自定义 / 种子模式** |
| 进阶 | 每个角色都能选到 10 级，联机进阶也是 10 级 |

**不会改的**：Steam 成就、胜负场数、历史对局、怪物图鉴。

> 解锁后游戏里显示卡牌 577/578、遗物 296/297 是正常的。差的那一个是游戏代码里留着的“已废弃”占位内容，正常游戏里也拿不到。

---

## 准备

需要 **Python 3.8 或更新的版本**。

- **Mac**：打开“终端”，输入 `python3 --version`。如果弹窗让你安装“命令行开发者工具”，点安装，装完再输入一次。
- **Windows**：去 <https://www.python.org/downloads/> 下载安装。安装第一页**一定要勾选 “Add python.exe to PATH”**。装好后打开“命令提示符”，输入 `py --version` 检查。

点本页右上角绿色的 **Code → Download ZIP** 下载，解压后保持 `sts2_unlock_all.py` 和 `sts2_ids.json` 在同一个文件夹里，不要拆开。

---

## 使用步骤

### 1. 至少玩过一次游戏

脚本改的是已有的存档。新装的游戏要先进去一次，让它生成存档。

- 平时**开 mod 玩**的，就开 mod 进一次。
- 平时**不开 mod**的，就正常进一次。

开 mod 和不开 mod 用的是**两份不同的存档**，你平时玩哪个就解锁哪个，两个都解锁也可以。

### 2. 完全退出游戏和 Steam ⚠️

这一步最重要。

- **Mac**：菜单栏 Steam → 退出 Steam（或者 ⌘Q）。只关窗口不算退出。
- **Windows**：右下角托盘里右键 Steam 图标 → 退出。

脚本会检查，如果 Steam 或游戏还开着，它会拒绝运行。

### 3. 在这个文件夹里打开终端

- **Mac**：打开“终端”，输入 `cd `（cd 后面有个空格），把这个文件夹拖进终端窗口，按回车。
- **Windows**：打开这个文件夹，在地址栏里输入 `cmd`，按回车。

### 4. 运行脚本

**Mac：**

```bash
python3 sts2_unlock_all.py
```

**Windows：**

```bat
py sts2_unlock_all.py
```

它会列出找到的存档，比如：

```
找到这些存档：
  [1] 开 mod 用的存档  modded/profile1/saves/progress.save  (Steam 7656...)  卡牌 232/577，遗物 105/296，Epoch 14/57
  [2] 原版存档  profile1/saves/progress.save  (Steam 7656...)  卡牌 200/577，遗物 87/296，Epoch 13/57

要解锁哪几个？输入编号（逗号分隔），直接回车 = 全部：
```

输入编号（比如 `1`）后按回车，或者直接按回车解锁全部。

脚本会**自动先备份**，再修改。备份放在本文件夹的 `backups/` 里。

> 想先看看会改什么、但不真的改？在命令后面加 `--dry-run`。

### 5. 打开 Steam，等十几秒

让 Steam 把新存档上传到云端。

如果 Steam 弹出“**云存档冲突**”，选 **“本地 / 此计算机上的文件”（Local）**，不要选云端。

### 6. 启动游戏检查

进百科全书、单人模式和角色选择界面，看看是不是都解锁了。

---

## 想撤销怎么办

脚本运行完会告诉你备份在哪，比如 `backups/20261017-211204`。先完全退出 Steam 和游戏，然后运行：

**Mac：**

```bash
python3 sts2_unlock_all.py --restore backups/20261017-211204
```

**Windows：**

```bat
py sts2_unlock_all.py --restore backups\20261017-211204
```

---

## 常见问题

**提示“请先完全退出 Steam 和游戏”**

Steam 还在后台运行。按第 2 步彻底退出。实在退不掉可以重启电脑。

**提示“没找到 progress.save”**

- 先进一次游戏再退出。
- 存档不在默认位置的话，可以用 `--save-root` 手动指定。默认位置是：
  - Mac：`~/Library/Application Support/SlayTheSpire2`
  - Windows：`%APPDATA%\SlayTheSpire2`
  - Linux：`~/.local/share/SlayTheSpire2`

**列表里出现“⚠ 没找到 Steam 云缓存”**

脚本找不到 Steam 的云存档缓存。可能是你关了 Steam 云同步，或者 Steam 装在别的位置。

- 关了云同步：不影响，直接用。
- Steam 装在别处：用 `--steam-root "你的Steam安装目录"` 指定。不指定的话，游戏启动时可能会用云端的旧存档把解锁覆盖掉。

**进游戏发现没解锁（又变回原样）**

几乎都是因为改的时候 Steam 没有完全退出，游戏启动时拿云端的旧存档覆盖了本地。完全退出 Steam 后再跑一次就好。

**会不会封号？**

目前没有任何因为改存档被封号的案例。官方也说过不打算做侵入式的反作弊。这个脚本只改你自己电脑上的单机进度，不碰成就，也不碰排行榜数据。不过官方并没有明确写过这方面的规定，**风险自负**。

**游戏更新了怎么办**

新版本可能加了新卡牌、新遗物。没更新 ID 列表的话，脚本照样能跑，只是新内容不会被解锁。想更新列表的话：

```bash
pip install dnfile
python3 sts2_unlock_all.py --dll "游戏目录里的 sts2.dll 路径"
```

`sts2.dll` 在游戏安装目录里：
- Mac：`SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64/sts2.dll`
- Windows：游戏目录下的 `data_sts2_windows_x86_64\sts2.dll`（具体文件夹名以实际为准）

**支持哪些系统**

Mac 上实测过。Windows 和 Linux 的路径是按规律写的，**还没实测**。遇到问题可以用 `--save-root` 和 `--steam-root` 手动指定路径。

---

## 原理（给好奇的人）

1. **存档就是 JSON**：`progress.save` 是普通的 JSON 文本。
   - 百科全书显示什么，看 `discovered_cards` 等列表。
   - 时间线、模式、角色有没有解锁，看 `epochs` 里每一项的 `state` 是不是 `revealed`。
   - 进阶等级看 `character_stats[].max_ascension`。
2. **ID 列表来自游戏程序本身**：`sts2_ids.json` 是从游戏的 `sts2.dll`（.NET 程序集）元数据里读出来的类名。
   - 比如 `MegaCrit.Sts2.Core.Models.Cards.StrikeIronclad` 对应 `CARD.STRIKE_IRONCLAD`。
   - 翻译文件里有过时的条目，所以没有用它。
3. **Steam 云同步的坑**：游戏启动时不管本地新不新，都会拿 Steam 云端的版本覆盖本地。
   - 游戏所谓的“云端”，其实是 Steam 在本地的缓存文件夹 `Steam/userdata/<账号ID>/2868840/remote/`。
   - 所以脚本会在 Steam 退出的状态下，把这个缓存和游戏存档**一起改**。Steam 重开后发现文件变了，就会把新的上传上去。

## 许可证

[MIT](LICENSE)
