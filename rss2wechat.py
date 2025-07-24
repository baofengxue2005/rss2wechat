#!/usr/bin/env python3
import os, sys, datetime, hashlib, feedparser, requests, json

APPID  = os.getenv("WX_APPID")
SECRET = os.getenv("WX_SECRET")
RSS    = "https://pubmed.ncbi.nlm.nih.gov/rss/search/1TAHVG_L--C4I5n3ZKx7cFD9yaT84W6V2uThXemmmPdUmQzkqM/?limit=15&utm_campaign=pubmed-2&fc=20250723221811"  # 改成你的 RSS 地址
FEED_HISTORY_FILE = "history.json"

# ---------- 工具函数 ----------
def load_history():
    try:
        with open(FEED_HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_history(s):
    with open(FEED_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(s), f, ensure_ascii=False)

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}"
    return requests.get(url, timeout=10).json()["access_token"]

def upload_image_from_url(img_url):
    """下载并上传封面图，返回 media_id"""
    img = requests.get(img_url, timeout=15).content
    files = {"media": ("cover.jpg", img, "image/jpeg")}
    url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={get_access_token()}&type=image"
    return requests.post(url, files=files, timeout=15).json()["media_id"]

def create_draft(entries):
    articles = []
    for e in entries[:8]:
        cover = upload_image_from_url(e.get("media_thumbnail") or "https://via.placeholder.com/300")
        articles.append({
            "title": e.title,
            "author": "RSS机器人",
            "digest": e.summary[:60] + "...",
            "content": f'<p>{e.summary}</p><p><a href="{e.link}">阅读原文</a></p>',
            "thumb_media_id": cover
        })
    data = {"articles": articles}
    url = f"https://api.weixin.qq.com/cgi-bin/draft/addDraft?access_token={get_access_token()}"
    return requests.post(url, json=data, timeout=15).json()

# ---------- 主逻辑 ----------
def main():
    history = load_history()
    feed = feedparser.parse(RSS)
    new = []
    for e in feed.entries:
        gid = hashlib.md5(e.link.encode()).hexdigest()
        if gid not in history:
            history.add(gid)
            new.append(e)
    if not new:
        print("无更新")
        return
    print(f"发现 {len(new)} 篇新文章")
    create_draft(new)
    save_history(history)

if __name__ == "__main__":
    main()
