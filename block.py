from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
   
    blacklist = [
        "facebook.com", "fbcdn.net", "zalo.me", "chat.zalo.me", "tiktok.com",
        "tiktokcdn.com", "tiktokv.com", "instagram.com", "telegram.org", "t.me",
        "api.telegram.org", "messenger.com", "google.com", "youtube.com",
        "googlevideo.com", "chrome.google.com", "coccoc.com", "lemurproject.org"
    ]

    host = flow.request.pretty_host.lower()
    ua = flow.request.headers.get("User-Agent", "").lower()
    sni = flow.server_conn.sni or ""


    if any(item in host for item in blacklist) or any(item in sni for item in blacklist) or any(item in ua for item in blacklist):
        flow.response = http.Response.make(
            403,
            b"<h1>\xf0\x9f\x9a\xab Truy cập bị chặn do có nguy cơ xâm nhập (Hành vi Hack)</h1>",
            {"Content-Type": "text/html"}
        )
