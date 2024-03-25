import subprocess
import re
from urllib.parse import urlparse

def extract_domain(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        return parsed_url.netloc
    else:
        return parsed_url.path.split('/')[0]

def get_website_info(domain, whois_path):
    # 使用 subprocess 調用 whois 命令
    whois_result = subprocess.check_output([f"{whois_path}/whois", domain]).decode('utf-8')
    return whois_result

def get_part(result, part):
    pattern = re.compile(f"{part} (.+?)\n")
    match = pattern.search(result)
    if match:
        return match.group(1)
    else:
        return None

whois_path = 'E:/NetworkTool/WhoIs'
file_path = 'Grouped.txt'

# 讀取文件內容
with open(file_path, 'r') as file:
    lines = file.read().split(".\n")

for line in lines:
    try:
        domain = extract_domain(line)
        result = get_website_info(domain, whois_path)

        date = get_part(result, "Updated Date:")
        date2 = get_part(result, "Creation Date:")
        country = get_part(result, "Registrant Country:")

        if date is None and date2 is None and country is None:
            iana_result = subprocess.check_output([f"{whois_path}/whois", domain]).decode('utf-8')
            whois_server = get_part(iana_result, "whois:")
            result = subprocess.check_output([f"{whois_path}/whois", "-h", whois_server, domain]).decode('utf-8')

            date = get_part(result, "Updated Date:")
            date2 = get_part(result, "Creation Date:")
            country = get_part(result, "Registrant Country:")

            if date is None and date2 is None and country is None:
                date2 = get_part(result, "Record created on")
                address_lines = iana_result.split('\n')
                for address_line in address_lines:
                    match = re.match(r'\s*address:\s*(.+)$', address_line)
                    if match:
                        country = match.group(1).strip()

        if country is None:
            iana_result = subprocess.check_output([f"{whois_path}/whois", domain]).decode('utf-8')
            address_lines = iana_result.split('\n')
            for address_line in address_lines:
                match = re.match(r'\s*address:\s*(.+)$', address_line)
                if match:
                    country = match.group(1).strip()

        print(f"Doman_name: {domain} \nlast_update_date: {date} DNS_registration_time: {date2} country: {country}")
    except Exception as e:
        print(f"執行查詢時發生錯誤: {e}")
        break
