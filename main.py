from urllib.parse import urlparse, parse_qs
import geoip2.database
import pandas as pd
import dns.resolver
import re
import requests
import time
import socket
import requests
import ssl
import socket
import tldextract
import whois
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
        # 發送 HTTPS 請求，驗證 TLS/SSL 證書
        response = requests.get(domain)
        # 檢查是否成功建立連線
        if response.status_code == 200:
            # 檢查證書相關資訊是否存在
            if response.history:
                # 歷史記錄中可能包含重定向的證書資訊
                cert = response.history[0].connection.sock.getpeercert()
            else:
                # 否則，從當前回應中獲取證書資訊
                cert = response.connection.sock.getpeercert()
            # 返回證書主體名稱 (subject)
            return 1
        else:
            # 如果連線失敗，返回 None
            return 0
    except:
        # 如果出現任何錯誤，返回 None
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
        response = requests.get("http://" + domain)
        end_time = time.time()
        # 返回響應時間（秒）
        return end_time - start_time
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
        w = whois.whois(domain)
        
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
        w = whois.whois(domain)
        
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

def number_group_to(domain):

    return 

def split_class(domain):

    return 
    
# 讀取CSV檔案，並省略掉標題行
df = pd.read_csv("fff.csv", header=None, skiprows=1, names=["URL", "Lable"])

data = []
for index, row in df.iterrows():
    url = row["URL"]
    phishing_label = row["Lable"]
    
    # 處理Fishing_Lable
    if phishing_label == "good":
        phishing = 0
    elif phishing_label == "bad":
        phishing = 1
    else:
        phishing = None
    
    # 獲取URL相關資訊
    domain = get_domain(url)
    print(domain)
    response_time = get_response_time(domain)
    is_ip = 1 if is_ip_address(domain) else 0
    contains_server_client_flag = contains_server_client(domain)
    email_present = email_in_url(url)
    resolved_ips = count_resolved_ips(domain)
    tls_ssl_certificate = check_tls_ssl_certificate(domain)
    redirects = count_redirects(url)
    url_shortened = is_url_shortened(url)
    
    # 調用函數檢查URL是否被Google索引
    url_google_index = is_url_indexed_on_google(url)
    
    domain_spf = has_spf_record(domain)
    
    tld_present_params = tld_present_url(domain)
    
    ttl_value = ttl_hostname(domain)
    
    asn_ip = asn_url(domain)
    
    qty_tld_url = tld_length(domain)
    
    time_domain_activation = Time_domain_activation(domain)
    time_domain_expiration = Time_domain_expiration(domain)
    
    qty_mx_servers = mx_servers(domain)
    
    qty_hashtag_url = count_hash_symbols(url)

    qty_underline_domain = count_underline(domain)
    
    number_group = number_group_to(domain)

    tld_class = split_class(domain)

    # 將資料添加到data列表中
    data.append([url] + [is_ip, contains_server_client_flag] + [email_present, response_time, resolved_ips, tls_ssl_certificate, redirects, url_shortened, url_google_index, domain_spf, tld_present_params, ttl_value, asn_ip, qty_tld_url, time_domain_activation, time_domain_expiration, qty_mx_servers, qty_hashtag_url, qty_underline_domain, number_group, tld_class, phishing])

columns = ["URL", "is_ip", "server_client_domain", "email_in_url", "response_time", "qty_ip_resolved", "tls_ssl_certificate", "qty_redirects", "url_shortened", "url_google_index", "domain_spf", "tld_presencet_params", "ttl_value", "asn_ip", "qty_tld_url", "time_domain_activation", "time_domain_expiration", "qty_mx_servers", "qty_hashtag_url", "qty_underline_domain", "number_group", "tld_class", "phishing"]

# 將 DataFrame 存為 CSV 檔案
df = pd.DataFrame(data, columns=columns)
df.to_csv("output.csv", index=False)