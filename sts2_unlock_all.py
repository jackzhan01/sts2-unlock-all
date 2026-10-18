#!/usr/bin/env python3
"""Slay the Spire 2 unlock-all — edits the save JSON only, never the game itself.
杀戮尖塔 2 全解锁 —— 只改存档 JSON，不改游戏本体。

See README.md / README.en.md. Standard library only (Python 3.8+);
`--dll` (re-extracting IDs) additionally needs `pip install dnfile`.
"""
import argparse
import json
import locale
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

APP_ID = "2868840"
STEAMID64_BASE = 76561197960265728
HERE = Path(__file__).resolve().parent
DEFAULT_IDS = HERE / "sts2_ids.json"
SAVE_PATTERN = re.compile(r"^(modded/)?profile\d+/saves/progress\.save$")
LANG = "en"


def T(zh, en):
    return zh if LANG == "zh" else en


def detect_lang():
    loc = (locale.getlocale()[0] or "") + os.environ.get("LANG", "") + os.environ.get("LC_ALL", "")
    return "zh" if re.search(r"zh|chinese", loc, re.I) else "en"


# ---------- paths / 路径 ----------

def default_save_root():
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library/Application Support/SlayTheSpire2"
    if system == "Windows":
        return Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming")) / "SlayTheSpire2"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "SlayTheSpire2"


def default_steam_roots():
    system = platform.system()
    if system == "Darwin":
        return [Path.home() / "Library/Application Support/Steam"]
    if system == "Windows":
        roots = []
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                roots.append(Path(winreg.QueryValueEx(k, "SteamPath")[0]))
        except OSError:
            pass
        roots += [Path(r"C:\Program Files (x86)\Steam"), Path(r"C:\Program Files\Steam")]
        return roots
    return [Path.home() / ".steam/steam", Path.home() / ".local/share/Steam",
            Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam"]


def find_profiles(save_root, steam_roots):
    """[(steamid64, relative path, local file, Steam cloud cache file or None)]"""
    found = []
    base = save_root / "steam"
    if not base.is_dir():
        return found
    for id_dir in sorted(base.iterdir()):
        if not (id_dir.is_dir() and id_dir.name.isdigit()):
            continue
        account_id = int(id_dir.name) - STEAMID64_BASE
        for f in sorted(id_dir.rglob("progress.save")):
            rel = f.relative_to(id_dir).as_posix()
            if not SAVE_PATTERN.match(rel):
                continue
            cloud = None
            for root in steam_roots:
                c = root / "userdata" / str(account_id) / APP_ID / "remote" / rel
                if c.is_file():
                    cloud = c
                    break
            found.append((id_dir.name, rel, f, cloud))
    return found


# ---------- running-process check / 进程检查 ----------

def running_blockers():
    """Names of running Steam / game processes."""
    try:
        if platform.system() == "Windows":
            out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True).stdout
            names = [line.split('","')[0].strip('"') for line in out.splitlines() if line]
        else:
            out = subprocess.run(["ps", "-A", "-o", "comm="], capture_output=True, text=True).stdout
            names = [os.path.basename(line.strip()) for line in out.splitlines() if line.strip()]
    except OSError:
        return []
    hits = set()
    for n in names:
        low = n.lower()
        if low in ("steam", "steam_osx", "steam.exe") or "slay the spire 2" in low or "slaythespire2" in low:
            hits.add(n)
    return sorted(hits)


# ---------- unlock / 解锁 ----------

def summarize(save, ids):
    revealed = sum(e.get("state") == "revealed" for e in save.get("epochs", []))
    return T("卡牌 {}/{}，遗物 {}/{}，Epoch {}/{}", "cards {}/{}, relics {}/{}, epochs {}/{}").format(
        len(save.get("discovered_cards", [])), len(ids["cards"]),
        len(save.get("discovered_relics", [])), len(ids["relics"]),
        revealed, len(ids["epochs"]))


def unlock(save, ids):
    now = int(time.time())
    for field, key in (("discovered_cards", "cards"), ("discovered_relics", "relics"),
                       ("discovered_potions", "potions"), ("discovered_events", "events"),
                       ("discovered_acts", "acts")):
        have = save.setdefault(field, [])
        seen = set(have)
        have += [x for x in ids[key] if x not in seen]

    epochs = save.setdefault("epochs", [])
    by_id = {e["id"]: e for e in epochs}
    for eid in ids["epochs"]:
        e = by_id.get(eid)
        if e is None:
            epochs.append({"id": eid, "obtain_date": now, "state": "revealed"})
        elif e.get("state") != "revealed":
            e["state"] = "revealed"
            e["obtain_date"] = e.get("obtain_date") or now

    max_asc = ids.get("max_ascension", 10)
    template = {"badges": [], "best_win_streak": 0, "current_streak": 0, "fastest_win_time": -1,
                "max_ascension": 0, "playtime": 0, "preferred_ascension": 0, "total_losses": 0, "total_wins": 0}
    chars = save.setdefault("character_stats", [])
    have_chars = {c["id"] for c in chars}
    chars += [dict(template, id=cid) for cid in ids["characters"] if cid not in have_chars]
    for c in chars:
        c["max_ascension"] = max(c.get("max_ascension", 0), max_asc)
    save["max_multiplayer_ascension"] = max(save.get("max_multiplayer_ascension", 0), max_asc)
    return save


# ---------- backup / restore 备份 / 还原 ----------

def backup(targets, backup_dir):
    manifest = []
    for i, path in enumerate(targets):
        dst = backup_dir / f"{i:02d}_{path.parent.parent.name}_{path.name}"
        shutil.copy2(path, dst)
        manifest.append({"backup": dst.name, "original": str(path)})
    (backup_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def restore(backup_dir):
    manifest = json.loads((backup_dir / "manifest.json").read_text(encoding="utf-8"))
    for m in manifest:
        shutil.copy2(backup_dir / m["backup"], m["original"])
        print(T("  已还原 ", "  restored ") + m["original"])


# ---------- re-extract IDs (optional) / 重新提取 ID（可选） ----------

def extract_ids(dll_path, out_path):
    try:
        import dnfile
    except ImportError:
        sys.exit(T("需要先安装 dnfile：pip install dnfile", "Please install dnfile first: pip install dnfile"))
    snake = lambda n: re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", n).upper()
    skip = ("DEPRECATED", "RANDOM_CHARACTER", "DEPRIVED", "VAKUU_CARD_SELECTOR")
    cats = {"Cards": ("cards", "CARD."), "Relics": ("relics", "RELIC."), "Potions": ("potions", "POTION."),
            "Events": ("events", "EVENT."), "Acts": ("acts", "ACT."), "Characters": ("characters", "CHARACTER.")}
    out = {k: [] for k, _ in cats.values()}
    out["epochs"] = []
    for t in dnfile.dnPE(str(dll_path)).net.mdtables.TypeDef:
        ns, name = str(t.TypeNamespace), str(t.TypeName)
        if t.Flags.tdAbstract or "<" in name:
            continue
        if ns == "MegaCrit.Sts2.Core.Timeline.Epochs":
            out["epochs"].append(snake(name))
        elif ns.startswith("MegaCrit.Sts2.Core.Models.") and ns.rsplit(".", 1)[1] in cats:
            key, prefix = cats[ns.rsplit(".", 1)[1]]
            out[key].append(prefix + snake(name))
    for k in out:
        out[k] = sorted(x for x in out[k] if not any(s in x for s in skip))
    out.update(game_version="extracted from " + Path(dll_path).name, source="sts2.dll type names", max_ascension=10)
    Path(out_path).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(T("已写入", "written:"), out_path, {k: len(v) for k, v in out.items() if isinstance(v, list)})


# ---------- main / 主流程 ----------

def choose(profiles, ids, select_all):
    print(T("\n找到这些存档：", "\nFound these saves:"))
    for i, (sid, rel, local, cloud) in enumerate(profiles, 1):
        kind = T("开 mod 用的存档", "modded save") if rel.startswith("modded/") else T("原版存档", "vanilla save")
        save = json.loads((cloud or local).read_text(encoding="utf-8"))
        warn = "" if cloud else T("  ⚠ 没找到 Steam 云缓存", "  ⚠ Steam cloud cache not found")
        print(f"  [{i}] {kind}  {rel}  (Steam {sid})  {summarize(save, ids)}{warn}")
    if select_all:
        return profiles
    ans = input(T("\n要解锁哪几个？输入编号（逗号分隔），直接回车 = 全部：",
                  "\nWhich ones to unlock? Enter numbers (comma-separated), or press Enter for all: ")).strip()
    if not ans:
        return profiles
    picks = {int(x) for x in re.split(r"[,\s，]+", ans) if x.isdigit()}
    return [p for i, p in enumerate(profiles, 1) if i in picks]


def main():
    global LANG
    ap = argparse.ArgumentParser(description="Slay the Spire 2 unlock-all (save edit only) / 杀戮尖塔 2 全解锁（只改存档）")
    ap.add_argument("--yes", action="store_true", help="unlock every save found, no prompt / 不询问，解锁全部存档")
    ap.add_argument("--dry-run", action="store_true", help="show changes without writing / 只显示会改什么，不写文件")
    ap.add_argument("--force", action="store_true", help="skip the Steam/game running check (not recommended) / 跳过进程检查（不推荐）")
    ap.add_argument("--ids", default=str(DEFAULT_IDS), help="ID list file (default: sts2_ids.json) / ID 列表文件")
    ap.add_argument("--save-root", help="game save root (auto-detected by default) / 游戏存档根目录")
    ap.add_argument("--steam-root", action="append", help="Steam install dir (auto-detected, repeatable) / Steam 安装目录")
    ap.add_argument("--restore", metavar="BACKUP_DIR", help="restore a backup / 还原某次备份")
    ap.add_argument("--dll", metavar="sts2.dll", help="re-extract the ID list from the game's sts2.dll / 从 sts2.dll 重新提取 ID")
    ap.add_argument("--lang", choices=["zh", "en"], help="output language (default: system language) / 输出语言")
    args = ap.parse_args()
    LANG = args.lang or detect_lang()

    if args.dll:
        extract_ids(args.dll, args.ids)
        return

    if not args.force and not args.dry_run:
        blockers = running_blockers()
        if blockers:
            sys.exit(T("请先完全退出 Steam 和游戏（检测到：{}），再重新运行。",
                       "Please fully quit Steam and the game first (found: {}), then run again.").format(", ".join(blockers)))

    if args.restore:
        restore(Path(args.restore))
        print(T("还原完成。现在可以打开 Steam 了。", "Restore complete. You can start Steam now."))
        return

    ids = json.loads(Path(args.ids).read_text(encoding="utf-8"))
    save_root = Path(args.save_root) if args.save_root else default_save_root()
    steam_roots = [Path(p) for p in args.steam_root] if args.steam_root else default_steam_roots()
    profiles = find_profiles(save_root, steam_roots)
    if not profiles:
        sys.exit(T("在 {} 下没找到 progress.save。至少先进一次游戏；路径不对可以用 --save-root 指定。",
                   "No progress.save found under {}. Launch the game at least once, or pass --save-root.").format(save_root))

    selected = choose(profiles, ids, args.yes)
    if not selected:
        sys.exit(T("没有选择任何存档。", "No save selected."))

    backup_dir = HERE / "backups" / time.strftime("%Y%m%d-%H%M%S")
    if not args.dry_run:
        backup_dir.mkdir(parents=True)
        backup([p for _, _, local, cloud in selected for p in (local, cloud) if p], backup_dir)
        print(T("\n已备份到：", "\nBacked up to: ") + str(backup_dir))

    for sid, rel, local, cloud in selected:
        # The game overwrites local with the cloud copy at launch, so the cloud cache is the source of truth.
        src = cloud or local
        save = json.loads(src.read_text(encoding="utf-8"))
        before = summarize(save, ids)
        unlock(save, ids)
        print(f"\n{rel}\n  {T('之前', 'before')}: {before}\n  {T('之后', 'after')}:  {summarize(save, ids)}, "
              + T("进阶 {}，每日/自定义模式已解锁", "ascension {}, Daily/Custom modes unlocked").format(ids.get("max_ascension", 10)))
        if args.dry_run:
            continue
        data = json.dumps(save, ensure_ascii=False, indent=2)
        for target in (local, cloud):
            if target:
                target.write_text(data, encoding="utf-8")

    if args.dry_run:
        print(T("\n（--dry-run：没有写任何文件）", "\n(--dry-run: nothing was written)"))
    else:
        print(T("\n完成！现在打开 Steam，等十几秒让它上传，再启动游戏。"
                "\n如果 Steam 弹出“云存档冲突”，选“本地 / 此计算机上的文件”。"
                "\n想撤销：python3 {} --restore \"{}\"",
                "\nDone! Start Steam, wait ~15 seconds for it to upload, then launch the game."
                "\nIf Steam shows a cloud conflict, choose the LOCAL files."
                "\nTo undo: python3 {} --restore \"{}\"").format(Path(__file__).name, backup_dir))


if __name__ == "__main__":
    main()
