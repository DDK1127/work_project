from urllib.parse import urlparse, parse_qs
import geoip2.database
import pandas as pd
import dns.resolver
import re
import os
import requests
import time
import socket
import requests
import ssl
import socket
import tldextract
import whois
import concurrent.futures
from multiprocessing import Pool
from datetime import datetime


def is_url_shortened(domain):
    shortening_services = ['goo.gl', 'bit.ly', 'tinyurl.com', 'ow.ly', 't.co', 'is.gd', 'rebrand.ly', 'tiny.cc', 'shorte.st', 'b24.io', 'moourl.com', 'yourls.org', 'hyperlink.to', 'mcaf.ee', 'clkim.com', 'soo.gd', 'firelink.io', 'viralurl.com', 'prettylinkpro.com','reurl.cc', 'picsee.io', 'ssur.cc', 'ifreesite', 'myppt.cc', 'lihi2.com']  # famous shortened

    if domain in shortening_services:
        return 1
    else:
        return 0


# 定義函數來計算重定向數量
def count_redirects(url):
    try:
        response = requests.get(url, allow_redirects=True)
        return len(response.history)
    except:
        return 0

# 定義函數來檢查 TLS/SSL 證書的有效性
def check_tls_ssl_certificate(domain):
    try:
        # 尝试发送 HTTPS 请求
        response = requests.get(f"https://{domain}")
        if response.status_code == 404:
            return 0
        else:
            # 如果连接成功建立，返回1
            return 1
    except:
        # 如果出现任何错误，也返回0
        return 0 

# 定義函數來計算解析出的 IP 數量
def count_resolved_ips(domain):
    try:
        # 透過 socket 解析域名的所有 IP 地址
        ip_addresses = socket.getaddrinfo(domain, None)
        # 回傳 IP 地址的數量
        return len(ip_addresses)
    except socket.gaierror:
        # 如果解析失敗，返回 0
        return 0

# 定義函數來獲取 domain
def get_domain(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if domain.startswith('www.'):
        domain = domain[4:]

    return domain


# 定義函數來判斷是否為 IP 地址格式
def is_ip_address(domain):
    parts = domain.split('.')
    if len(parts) == 4:
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False
        return True
    return False

# 定義函數來判斷 domain 中是否包含關鍵字 ka
def contains_server_client(domain):
    return 1 if "server" in domain or "client" in domain else 0

# 定義函數來檢查 URL 中是否存在電子郵件地址
def email_in_url(url):
    # 使用正則表達式進行電子郵件地址的匹配
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.search(pattern, url):
        return 1
    else:
        return 0
    
# 定義函數來獲取 domain 的響應時間
def get_response_time(domain):
    try:
        start_time = time.time()
        # 嘗試向該 domain 發送一個 GET 請求
        response = requests.get("http://" + domain,timeout=2)
        end_time = time.time()
        # 返回響應時間（秒）
        return end_time - start_time
    except requests.exceptions.Timeout:
        return 3
    except:
        # 如果出現任何錯誤（例如無法連接），返回 None
        return -1
    
def has_spf_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'TXT', lifetime=2)
        for rdata in answers:
            txt_record = rdata.strings[0].decode('utf-8')
            if txt_record.startswith('v=spf1'):
                return 1
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.NXDOMAIN:
        pass
    except dns.resolver.NoNameservers:
        pass
    except dns.resolver.LifetimeTimeout:
        return -1
    return -1

def tld_present_url(url):
    extracted = tldextract.extract(url)
    if extracted.suffix:
        return 1
    else:
        return 0
    
def ttl_hostname(domain):
    try:
        # 執行DNS查詢以獲取主機名的TTL值
        answer = dns.resolver.resolve(domain, 'A')
        # 返回第一個IP地址的TTL值
        return answer.rrset.ttl
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        # 如果出現任何錯誤或者沒有找到A記錄，則返回0
        return 0

def asn_url(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        # 設置API端點
        api_endpoint = f"https://ipinfo.io/{ip_address}/json"
        
        # 發送GET請求
        response = requests.get(api_endpoint)

        # 解析JSON響應
        data = response.json()
        
        #print(data)
        # 獲取ASN數字
        asn = data.get('org')
        if asn:
            return 1  # 返回ASN的第一部分（通常是數字）
        else:
            return -1
    except:
        return -1


# 定義函數來檢查URL是否被Google索引
def is_url_indexed_on_google(url):
    try:
        google_search_url = f"https://www.google.com/search?q=site%3A{url}"
        response = requests.get(google_search_url)
        if response.status_code == 200:
            return 1 if "Did not match any documents." not in response.text else 0
        else:
            return 0
    except Exception as e:
        print("is_url_indexed_on_google function => error:", e)
        return 0

# 定義函數來檢查域名是否被 Google 索引
def is_domain_indexed_on_google(domain):
    try:
        google_search_url = f"https://www.google.com/search?q=site%3A{domain}"
        response = requests.get(google_search_url)
        if response.status_code == 200:
            return 1 if "Did not match any documents." not in response.text else 0
        else:
            return 0
    except Exception as e:
        print("is_domain_indexed_on_google function => error:", e)
        return 0
    
def tld_length(domain):
    try:
        # 從域名中獲取頂級域名
        tld = domain.split('.')[-1]
        # 返回頂級域名的長度
        return len(tld)
    except Exception as e:
        return -1

def Time_domain_activation(domain):
    try:
        # 查詢域名的 Whois 記錄
        w = whois.whois(domain, timeout=3)
        
        # 獲取註冊日期
        creation_date = w.creation_date
        
        # 如果 creation_date 是一個列表，我們只取第一個日期
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        # 計算註冊日期與現在日期之間的差距（以天為單位）
        if creation_date:
            today = datetime.today()
            activation_days = (today - creation_date).days
            return activation_days
        else:
            return -1
    except:
        return -1

def Time_domain_expiration(domain):
    try:
        # 查詢域名的 Whois 記錄
        w = whois.whois(domain, timeout=3)
        
        # 獲取到期日期
        expiration_date = w.expiration_date
        
        # 如果 expiration_date 是一個列表，我們只取第一個日期
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        
        # 計算到期日期與現在日期之間的差距（以天為單位）
        if expiration_date:
            today = datetime.today()
            expiration_days = (expiration_date - today).days
            return expiration_days
        else:
            return -1
    except:
        return -1
    
def mx_servers(domain):
    try:
        # 查詢域名的MX記錄
        mx_records = dns.resolver.resolve(domain, 'MX')
        # 返回MX記錄的數量
        return len(mx_records)
    except:
        return -1
    
def count_hash_symbols(url):
    return url.count('#')

def count_underline(domain):
    return domain.count('_') 

def tear_down(url):#number_group_to used
    # 要移除的常見子域名
    common_subdomains = ["www", "mail", "blog", "shop", "forum", "news", "app", "api", "cdn", "img", "dev"]

    # 使用 tldextract 提取域名的各個部分
    extracted = tldextract.extract(url)

    # 移除通用頂級域名（gTLD）和國家代碼頂級域名（ccTLD）
    url = url.replace(f'.{extracted.suffix}', '')

    # 移除 http:// 或 https://
    url = re.sub(r'https?://', '', url)

    # 移除常見子域名
    for subdomain in common_subdomains:
        url = re.sub(fr'\b{subdomain}\.', '', url)

    # 使用 "." 和 "/" 分割 URL
    url_parts = re.split(r'[./-]', url)

    # 移除空字串
    url_parts = [part for part in url_parts if part]

    # 正規化
    url_parts = [word.lower().replace('0', 'o').replace('1', 'l').replace('&', 'g') for word in url_parts]
    return url_parts

def levenshtein_distance(s1, s2):#number_group_to used
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]

        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)

            current_row.append(min(insertions, deletions, substitutions))

        previous_row = current_row

    return previous_row[-1]

def find_most_similar_word(input_url, target_word):#number_group_to used
    min_distance = float('inf')
    most_similar_word = ""

    for i in range(len(input_url) - len(target_word) + 1):
        substring = input_url[i:i+len(target_word)]
        distance = levenshtein_distance(substring, target_word)

        if distance < min_distance:
            min_distance = distance
            most_similar_word = substring

    return most_similar_word, min_distance

def number_group_to(url):
    target_word = ['google', 'youtube', 'facebook', 'instagram', 'twitter', 'baidu', 'wikipedia', 'yahoo', 'yandex', 'whatsapp', 'xvideos', 'amazon', 'pornhub', 'tiktok', 'xnxx', 'reddit', 'yahoo', 'docomo', 'live', 'netflix', 'linkedin', 'openai', 'dzen', 'xhamster', 'office', 'bing', 'bilibili', 'vk', 'naver', 'mail', 'max', 'pinterest', 'samsung', 'discord', 'twitch', 'microsoftonline', 'turbopages', 'microsoft', 'weather', 'tme', 'xhamster', 'qq', 'duckduckgo', 'quora', 'roblox', 'stripchat', 'ebay', 'fandom', 'globo', 'msn', 'paypal', 'pichincha', 'index']
    most_similase_url = 'nothing'
    most_similase_unm = 1.0
    for j in target_word:
        teared = tear_down(url)
        min_levenshtein = 100
        levenshtein_similase = 1.0
        similar = "null"
        for i in teared:
            most_similar_word, levenshtein_dist = find_most_similar_word(i, j)#找出與target_word最相似的most_similar_word
            if most_similar_word == j:
                min_levenshtein = 0
                levenshtein_similase = 0.0
                similar = j
                break
            if levenshtein_dist < min_levenshtein:
                min_levenshtein = levenshtein_dist
                similar = most_similar_word

        if levenshtein_similase == 1.0:
            levenshtein_similase = min_levenshtein/len(j)
        # print(f"Origin: '{j}' Similar: '{similar}' levenshtein_similase: '{levenshtein_similase:.5f}'")#記錄這三個

        is_imitate_value = 0.5

        if len(j) <= 4:
            is_imitate_value = 0.0
        elif j[0].lower() != similar[0].lower():#首字母
            is_imitate_value = 0.25
        elif len(j) <= 6:
            is_imitate_value = 0.4
        
        if levenshtein_similase <= is_imitate_value and levenshtein_similase < most_similase_unm:
            most_similase_unm = levenshtein_similase
            most_similase_url = j
    return(str(round(most_similase_unm, 1)))#str

def split_class(domain):
    specific_domains_1 = ['.com.tw', '.com.hk', '.eu', '.gov.tw', '.edu.tw', '.org.tw', '.org.hk', 
                          '.mil', '.ac', '.int', '.gov', '.edu', '.museum', '.aero', '.coop', 
                          '.pro', '.cat', '.gov.uk', '.edu.au', '.sch.uk', '.police.uk','.net.tw']

    specific_domains_2 = ['.de', '.it', '.jp', '.fr', '.kr', '.sg', '.au', '.ca', '.nz', '.ie',
                          '.ae', '.br', '.sa', '.mx', '.nl', '.ch', '.uk', '.be', '.at', '.pl',
                         '.se', '.dk', '.cz', '.no', '.ie', '.gr', '.pt','.org', '.police']

    if any(domain.endswith(specific) for specific in specific_domains_1):
        return 1
    elif any(domain.endswith(specific) for specific in specific_domains_2):
        return 2
    else:
        return 0 
    
# 定義函數來計算URL中特定字符的出現次數
def count_char_in_url(url, char):
    return url.count(char)

# 定義函數來計算URL長度
def calculate_url_length(url):
    return len(url)

    
def process_url(url):
    # 獲取URL相關資訊
    domain = get_domain(url)
    response_time = get_response_time(domain)
    contains_server_client_flag = contains_server_client(domain)
    email_present = email_in_url(url)
    resolved_ips = count_resolved_ips(domain)
    tls_ssl_certificate = check_tls_ssl_certificate(domain)
    url_google_index = is_url_indexed_on_google(url)
    domain_spf = has_spf_record(domain)
    ttl_value = ttl_hostname(domain)
    asn_ip = asn_url(domain)
    qty_tld_url = tld_length(domain)
    qty_mx_servers = mx_servers(domain)
    qty_hashtag_url = count_hash_symbols(url)
    qty_underline_domain = count_underline(domain)
    number_group = number_group_to(url)
    tld_class = split_class(domain)
    qty_dot_url = count_char_in_url(url, '.')
    qty_hyphen_url = count_char_in_url(url, '-')
    qty_underline_url = count_char_in_url(url, '_')
    qty_slash_url = count_char_in_url(url, '/')
    qty_questionmark_url = count_char_in_url(url, '?')
    qty_at_url = count_char_in_url(url, '@')
    qty_exclamation_url = count_char_in_url(url, '!')
    qty_space_url = count_char_in_url(url, ' ')
    qty_tilde_url = count_char_in_url(url, '~')
    qty_plus_url = count_char_in_url(url, '+')
    qty_asterisk_url = count_char_in_url(url, '*')
    qty_dollar_url = count_char_in_url(url, '$')
    qty_percent_url = count_char_in_url(url, '%')
    length_url = calculate_url_length(url)
    return [url, contains_server_client_flag, email_present, response_time, resolved_ips, tls_ssl_certificate, url_google_index, domain_spf, ttl_value, asn_ip, qty_tld_url, qty_mx_servers, qty_hashtag_url, qty_underline_domain, number_group, tld_class, qty_dot_url, qty_hyphen_url, qty_underline_url, qty_slash_url, qty_questionmark_url, qty_at_url, qty_exclamation_url, qty_space_url, qty_tilde_url, qty_plus_url, qty_asterisk_url, qty_dollar_url, qty_percent_url, length_url]
    
def process_batch(batch_urls):
    # 使用多進程處理多個URL
    pool = Pool()
    results = pool.map(process_url, batch_urls)
    pool.close()
    pool.join()
    # 將處理結果轉換為DataFrame
    columns = ["URL", "server_client_domain", "email_in_url", "response_time", "qty_ip_resolved", "tls_ssl_certificate", "url_google_index", "domain_spf", "ttl_value", "asn_ip", "qty_tld_url", "qty_mx_servers", "qty_hashtag_url", "qty_underline_domain", "unsimiler", "tld_class", "qty_dot_url", "qty_hyphen_url", "qty_underline_url", "qty_slash_url", "qty_questionmark_url", "qty_at_url", "qty_exclamation_url", "qty_space_url", "qty_tilde_url", "qty_plus_url", "qty_asterisk_url", "qty_dollar_url", "qty_percent_url", "length_url"]
    result_df = pd.DataFrame(results, columns=columns)
    result_df.to_csv("output.csv", mode='a', index=False, header=not os.path.exists("output.csv"))


def main():
    # 讀取CSV檔案，並省略掉標題行
    df = pd.read_csv("./test.csv", header=None, names=["URL"])

    # 提取URL列表
    urls = df["URL"].tolist()

    # 将urls切分为多个列表，每个列表包含50个URL
    split_urls = [urls[i:i+1] for i in range(0, len(urls), 1)]

    # 逐个处理URL组
    ccc = 1
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for batch_urls in split_urls:
            future = executor.submit(process_batch, batch_urls)
            try:
                future.result(timeout=80)  # 设置超时时间为80秒
            except concurrent.futures.TimeoutError:
                print(ccc)
                ccc += 1
                print("big time out")
                continue
            finally:
                print(ccc)
                ccc += 1

        

if __name__ == "__main__":
    main()