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


def is_url_shortened(url):
    shortening_services = ['goo.gl', 'bit.ly', 'tinyurl.com', 'ow.ly', 't.co', 'is.gd', 'rebrand.ly', 'tiny.cc', 'shorte.st', 'b24.io', 'moourl.com', 'yourls.org', 'hyperlink.to', 'mcaf.ee', 'clkim.com', 'soo.gd', 'firelink.io', 'viralurl.com', 'prettylinkpro.com','reurl.cc', 'picsee.io', 'ssur.cc', 'ifreesite', 'myppt.cc', 'lihi2.com']  # famous shortened

    domain = url.split('//')[-1].split('/')[0] 
    # or domain = = urlparse(url).netloc

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
        response = requests.get("https://" + domain)
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
    parsed_url = urlparse(url)
    return parsed_url.netloc

# 定義函數來獲取目錄
def get_directory_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    # 移除末尾的文件名（如果有）
    directory = '/'.join(path.split('/')[:-1])
    return directory

# 定義函數來獲取檔案名稱
def get_file_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    if path:
        # 將路徑按照"/"分割，取最後一個元素即為檔案名稱
        file_name = path.split('/')[-1]
        return file_name
    
# 定義函數來獲取 URL 中的參數
def get_parameters_from_url(url):
    # 解析URL
    parsed_url = urlparse(url)
    # 獲取查詢參數部分並解析為字典形式
    parameters = parse_qs(parsed_url.query)
    return parameters


# 定義函數來判斷是否為 IP 地址格式
def is_ip_address(domain):
    parts = domain.split('.')
    if len(parts) == 4:
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False
        return True
    return False

# 定義函數來判斷 domain 中是否包含關鍵字 "server" 或 "client"
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
    
def has_spf_record(url):
    domain = url.split('//')[-1].split('/')[0]  # split domain form url
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
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
    return 0

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
        # 設置API端點
        api_endpoint = f"https://ipinfo.io/{domain}/json"
        
        # 發送GET請求
        response = requests.get(api_endpoint)
        
        # 解析JSON響應
        data = response.json()
        
        # 獲取ASN數字
        asn = data.get('asn')
        if asn:
            return int(asn.split()[0])  # 返回ASN的第一部分（通常是數字）
        else:
            return -1
    except Exception as e:
        return -1

# 定義函數來計算每個 URL 中的各種字元數量和長度
def count_chars(url):
    qty_dot_url = url.count('.')
    qty_hyphen_url = url.count('-')
    qty_underline_url = url.count('_')
    qty_slash_url = url.count('/')
    qty_questionmark_url = url.count('?')
    qty_equal_url = url.count('=')
    qty_at_url = url.count('@')
    qty_and_url = url.count('&')
    qty_exclamation_url = url.count('!')
    qty_space_url = url.count(' ')
    qty_tilde_url = url.count('~')
    qty_comma_url = url.count(',')
    qty_plus_url = url.count('+')
    qty_asterisk_url = url.count('*')
    qty_hashtag_url = url.count('#')
    qty_dollar_url = url.count('$')
    qty_percent_url = url.count('%')
    qty_tld_url = url.count('.') - 1  # 總域名標記（TLD）數量
    length_url = len(url)
    return qty_dot_url, qty_hyphen_url, qty_underline_url, qty_slash_url, qty_questionmark_url, qty_equal_url, qty_at_url, qty_and_url, qty_exclamation_url, qty_space_url, qty_tilde_url, qty_comma_url, qty_plus_url, qty_asterisk_url, qty_hashtag_url, qty_dollar_url, qty_percent_url, qty_tld_url, length_url

# 定義函數來計算 domain 中的各種字元數量和長度
def count_domain_chars(domain):
    qty_dot_domain = domain.count('.')
    qty_hyphen_domain = domain.count('-')
    qty_underline_domain = domain.count('_')
    qty_slash_domain = domain.count('/')
    qty_questionmark_domain = domain.count('?')
    qty_equal_domain = domain.count('=')
    qty_at_domain = domain.count('@')
    qty_and_domain = domain.count('&')
    qty_exclamation_domain = domain.count('!')
    qty_space_domain = domain.count(' ')
    qty_tilde_domain = domain.count('~')
    qty_comma_domain = domain.count(',')
    qty_plus_domain = domain.count('+')
    qty_asterisk_domain = domain.count('*')
    qty_hashtag_domain = domain.count('#')
    qty_dollar_domain = domain.count('$')
    qty_percent_domain = domain.count('%')
    qty_vowels_domain = sum(1 for char in domain if char in 'aeiouAEIOU')
    domain_length = len(domain)
    return qty_dot_domain, qty_hyphen_domain, qty_underline_domain, qty_slash_domain, qty_questionmark_domain, qty_equal_domain, qty_at_domain, qty_and_domain, qty_exclamation_domain, qty_space_domain, qty_tilde_domain, qty_comma_domain, qty_plus_domain, qty_asterisk_domain, qty_hashtag_domain, qty_dollar_domain, qty_percent_domain, qty_vowels_domain, domain_length

# 定義函數來計算目錄中的各種字元數量和長度
def count_directory_chars(directory):
    qty_dot_directory = directory.count('.')
    qty_hyphen_directory = directory.count('-')
    qty_underline_directory = directory.count('_')
    qty_slash_directory = directory.count('/')
    qty_questionmark_directory = directory.count('?')
    qty_equal_directory = directory.count('=')
    qty_at_directory = directory.count('@')
    qty_and_directory = directory.count('&')
    qty_exclamation_directory = directory.count('!')
    qty_space_directory = directory.count(' ')
    qty_tilde_directory = directory.count('~')
    qty_comma_directory = directory.count(',')
    qty_plus_directory = directory.count('+')
    qty_asterisk_directory = directory.count('*')
    qty_hashtag_directory = directory.count('#')
    qty_dollar_directory = directory.count('$')
    qty_percent_directory = directory.count('%')
    directory_length = len(directory)
    return qty_dot_directory, qty_hyphen_directory, qty_underline_directory, qty_slash_directory, qty_questionmark_directory, qty_equal_directory, qty_at_directory, qty_and_directory, qty_exclamation_directory, qty_space_directory, qty_tilde_directory, qty_comma_directory, qty_plus_directory, qty_asterisk_directory, qty_hashtag_directory, qty_dollar_directory, qty_percent_directory, directory_length

# 定義函數來計算檔案名稱中的各種字元數量和長度
def count_file_chars(file_name):
    if file_name:
        qty_dot_file = file_name.count('.')
        qty_hyphen_file = file_name.count('-')
        qty_underline_file = file_name.count('_')
        qty_slash_file = file_name.count('/')
        qty_questionmark_file = file_name.count('?')
        qty_equal_file = file_name.count('=')
        qty_at_file = file_name.count('@')
        qty_and_file = file_name.count('&')
        qty_exclamation_file = file_name.count('!')
        qty_space_file = file_name.count(' ')
        qty_tilde_file = file_name.count('~')
        qty_comma_file = file_name.count(',')
        qty_plus_file = file_name.count('+')
        qty_asterisk_file = file_name.count('*')
        qty_hashtag_file = file_name.count('#')
        qty_dollar_file = file_name.count('$')
        qty_percent_file = file_name.count('%')
        file_length = len(file_name)
        return qty_dot_file, qty_hyphen_file, qty_underline_file, qty_slash_file, qty_questionmark_file, qty_equal_file, qty_at_file, qty_and_file, qty_exclamation_file, qty_space_file, qty_tilde_file, qty_comma_file, qty_plus_file, qty_asterisk_file, qty_hashtag_file, qty_dollar_file, qty_percent_file, file_length
    else:
        # 如果沒有檔案名稱，則返回 0
        return (0,) * 18


# 定義函數來計算參數中的各種字元數量和長度
# 修改 count_params_chars 函數來計算參數長度
def count_params_chars(parameters):
    qty_dot_params = sum(param.count('.') for param in parameters.values())
    qty_hyphen_params = sum(param.count('-') for param in parameters.values())
    qty_underline_params = sum(param.count('_') for param in parameters.values())
    qty_slash_params = sum(param.count('/') for param in parameters.values())
    qty_questionmark_params = sum(param.count('?') for param in parameters.values())
    qty_equal_params = sum(param.count('=') for param in parameters.values())
    qty_at_params = sum(param.count('@') for param in parameters.values())
    qty_and_params = sum(param.count('&') for param in parameters.values())
    qty_exclamation_params = sum(param.count('!') for param in parameters.values())
    qty_space_params = sum(param.count(' ') for param in parameters.values())
    qty_tilde_params = sum(param.count('~') for param in parameters.values())
    qty_comma_params = sum(param.count(',') for param in parameters.values())
    qty_plus_params = sum(param.count('+') for param in parameters.values())
    qty_asterisk_params = sum(param.count('*') for param in parameters.values())
    qty_hashtag_params = sum(param.count('#') for param in parameters.values())
    qty_dollar_params = sum(param.count('$') for param in parameters.values())
    qty_percent_params = sum(param.count('%') for param in parameters.values())
    params_length = sum(len(param) for param in parameters.values())
    return qty_dot_params, qty_hyphen_params, qty_underline_params, qty_slash_params, qty_questionmark_params, qty_equal_params, qty_at_params, qty_and_params, qty_exclamation_params, qty_space_params, qty_tilde_params, qty_comma_params, qty_plus_params, qty_asterisk_params, qty_hashtag_params, qty_dollar_params, qty_percent_params

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
    response_time = get_response_time(domain)
    directory = get_directory_from_url(url)
    file_name = get_file_from_url(url)
    is_ip = 1 if is_ip_address(domain) else 0
    contains_server_client_flag = contains_server_client(domain)
    counts_url = count_chars(url)
    counts_domain = count_domain_chars(domain)
    counts_directory = count_directory_chars(directory)
    counts_file = count_file_chars(file_name) if file_name else (0,) * 18
    parameters = get_parameters_from_url(url)
    counts_params = count_params_chars(parameters)
    email_present = email_in_url(url)
    resolved_ips = count_resolved_ips(domain)
    tls_ssl_certificate = check_tls_ssl_certificate(domain)
    redirects = count_redirects(url)
    url_shortened = is_url_shortened(url)
    
    # 調用函數檢查URL是否被Google索引
    url_google_index = is_url_indexed_on_google(url)
    
    # 調用函數檢查域名是否被Google索引
    domain_google_index = is_domain_indexed_on_google(domain)
    
    domain_spf = has_spf_record(domain)
    
    tld_present_params = tld_present_url(url)
    
    ttl_value = ttl_hostname(domain)
    asn_ip = asn_url(domain)
    
    # 將資料添加到data列表中
    data.append([url] + list(counts_url) + list(counts_domain) + [is_ip, contains_server_client_flag] + list(counts_directory) + list(counts_file) + list(counts_params) + [len(parameters), email_present, response_time, resolved_ips, tls_ssl_certificate, redirects, url_shortened, url_google_index, domain_google_index, domain_spf, tld_present_params, ttl_value, asn_ip, phishing])

columns = ["URL", "qty_dot_url", "qty_hyphen_url", "qty_underline_url", "qty_slash_url", "qty_questionmark_url", "qty_equal_url", "qty_at_url", "qty_and_url", "qty_exclamation_url", "qty_space_url", "qty_tilde_url", "qty_comma_url", "qty_plus_url", "qty_asterisk_url", "qty_hashtag_url", "qty_dollar_url", "qty_percent_url", "qty_tld_url", "length_url",
           "qty_dot_domain", "qty_hyphen_domain", "qty_underline_domain", "qty_slash_domain", "qty_questionmark_domain", "qty_equal_domain", "qty_at_domain", "qty_and_domain", "qty_exclamation_domain", "qty_space_domain", "qty_tilde_domain", "qty_comma_domain", "qty_plus_domain", "qty_asterisk_domain", "qty_hashtag_domain", "qty_dollar_domain", "qty_percent_domain", "qty_vowels_domain", "domain_length",
           "domain_in_ip", "server_client_domain", "qty_dot_directory", "qty_hyphen_directory", "qty_underline_directory", "qty_slash_directory", "qty_questionmark_directory", "qty_equal_directory", "qty_at_directory", "qty_and_directory", "qty_exclamation_directory", "qty_space_directory", "qty_tilde_directory", "qty_comma_directory", "qty_plus_directory", "qty_asterisk_directory", "qty_hashtag_directory", "qty_dollar_directory", "qty_percent_directory", "directory_length",
           "qty_dot_file", "qty_hyphen_file", "qty_underline_file", "qty_slash_file", "qty_questionmark_file", "qty_equal_file", "qty_at_file", "qty_and_file", "qty_exclamation_file", "qty_space_file", "qty_tilde_file", "qty_comma_file", "qty_plus_file", "qty_asterisk_file", "qty_hashtag_file", "qty_dollar_file", "qty_percent_file", "file_length",
           "qty_dot_params", "qty_hyphen_params", "qty_underline_params", "qty_slash_params", "qty_questionmark_params", "qty_equal_params", "qty_at_params", "qty_and_params", "qty_exclamation_params", "qty_space_params", "qty_tilde_params", "qty_comma_params", "qty_plus_params", "qty_asterisk_params", "qty_hashtag_params", "qty_dollar_params", "qty_percent_params", "qty_params", "email_in_url", "response_time", "qty_ip_resolved", "tls_ssl_certificate", "qty_redirects", "url_shortened", "url_google_index", "domain_google_index", "domain_spf", "tld_presencet_params", "ttl_value", "asn_ip", "phishing"]

# 將 DataFrame 存為 CSV 檔案
df = pd.DataFrame(data, columns=columns)
df.to_csv("output.csv", index=False)