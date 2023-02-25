import concurrent.futures
import requests
from tqdm import tqdm

def is_proxy_alive(proxy, url):
    try:
        response = requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def is_proxy_not_blacklisted(proxy, url):
    try:
        response = requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=2)
        if response.status_code == 200 and 'Our systems have detected unusual traffic' not in response.text:
            return True
    except:
        pass
    return False

def check_proxies_from_file(input_file, output_file, url, max_workers=200):
    with open(input_file, 'r', encoding='ISO-8859-1') as f:
        proxies = f.read().splitlines()
    with open(output_file, 'a') as f:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(is_proxy_alive, f'http://{proxy}', url) for proxy in proxies]
            for i, future in enumerate(tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc='Checking proxies')):
                proxy = proxies[i]
                is_alive = future.result()
                if is_alive and is_proxy_not_blacklisted(f'http://{proxy}', url):
                    f.write(proxy + '\n')

input_file = "proxies.txt"
output_file = "../proxy.txt"
urls = ['https://httpbin.org/ip', 'https://www.google.com/search?q=test', 'https://cryptocloud9.io', '']
max_workers = 500

# Check all proxies against the first URL
check_proxies_from_file(input_file, output_file, urls[0])

# Check subsets of proxies against other URLs in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    for i in range(max_workers):
        start = i * len(input_file) // max_workers
        end = (i + 1) * len(input_file) // max_workers
        subset = input_file[start:end]
        url = urls[i % len(urls)]
        executor.submit(check_proxies_from_file, subset, output_file, url)