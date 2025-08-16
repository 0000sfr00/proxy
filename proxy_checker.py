import requests
import threading
import socket
from colorama import init, Fore
import time

init(autoreset=True)

THREAD_COUNT = 150
TIMEOUT = 3

proxy_list = set()
proxy_queue = []
hit_count = 0
bad_count = 0
lock = threading.Lock()

proxy_api_urls = [
    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=1000&country=all',
    'https://www.proxy-list.download/api/v1/get?type=http',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
    'https://www.proxy-list.download/api/v1/get?type=https',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
    'https://api.proxyscrape.com/?request=displayproxies&proxytype=http',
    'https://www.proxyscan.io/download?type=http',
    'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt',
    'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
    'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt',
    'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/proxies/https.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/proxies/socks4.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/proxies/socks5.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt',
    'https://proxy.spys.one/proxy.txt',
    'https://www.proxy-list.download/api/v1/get?type=socks4',
    'https://www.proxy-list.download/api/v1/get?type=socks5',
    'https://www.proxyscan.io/download?type=socks4',
    'https://www.proxyscan.io/download?type=socks5',
]

def fetch_proxies():
    global proxy_list
    print("[*] Proxy API'lerinden proxyler çekiliyor...")
    for url in proxy_api_urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                proxies = res.text.strip().split('\n')
                for proxy in proxies:
                    proxy = proxy.strip()
                    if proxy and proxy not in proxy_list:
                        proxy_list.add(proxy)
                print(f"  [+] {len(proxies)} proxy çekildi | Toplam: {len(proxy_list)} (Kaynak: {url})")
            else:
                print(f"  [-] API hatası {url} - Kod: {res.status_code}")
        except Exception as e:
            print(f"  [-] API erişim hatası {url} - {e}")

def is_port_open(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((ip, port))
        sock.close()
        return True
    except:
        return False

def is_proxy_usable(proxy):
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=TIMEOUT)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def save_proxy_to_file(proxy):
    try:
        with open("proxyscloud571.txt", "a", encoding="utf-8") as f:
            f.write(proxy + "\n")
    except Exception as e:
        print(Fore.YELLOW + f"[!] Dosyaya yazma hatası: {e}")

def proxy_worker():
    global hit_count, bad_count
    while True:
        try:
            proxy = proxy_queue.pop()
        except IndexError:
            break

        ip, port = proxy.split(":")
        port = int(port)

        if is_port_open(ip, port):
            if is_proxy_usable(proxy):
                with lock:
                    hit_count += 1
                    print(Fore.GREEN + f"[✔️ HIT {hit_count}] {proxy} ✓✓✓")
                    save_proxy_to_file(proxy)
            else:
                with lock:
                    bad_count += 1
                    print(Fore.RED + f"[✖ BAD {bad_count}] {proxy} - IP değişmedi")
        else:
            with lock:
                bad_count += 1
                print(Fore.RED + f"[✖ BAD {bad_count}] {proxy} - Port kapalı")

def main():
    fetch_proxies()
    global proxy_queue
    proxy_queue = list(proxy_list)
    print(f"[*] Toplam {len(proxy_queue)} proxy test kuyruğunda.")

    threads = []
    for _ in range(min(THREAD_COUNT, len(proxy_queue))):
        t = threading.Thread(target=proxy_worker)
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(Fore.CYAN + f"\n[✔️] Tarama tamamlandı! Hit: {hit_count}, Bad: {bad_count}")

if __name__ == "__main__":
    main()
