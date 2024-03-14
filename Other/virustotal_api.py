import requests

def scan_url(api_key, url):
    url_scan_endpoint = 'https://www.virustotal.com/vtapi/v2/url/scan'
    params = {'apikey': api_key, 'url': url}

    # Send post require 
    response = requests.post(url_scan_endpoint, params=params)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return {'error': f"Failed to submit URL for scanning. Status code: {response.status_code}"}

def get_url_report(api_key, resource):
    url_report_endpoint = 'https://www.virustotal.com/vtapi/v2/url/report'
    params = {'apikey': api_key, 'resource': resource}

    # Send get require
    response = requests.get(url_report_endpoint, params=params)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return {'error': f"Failed to get URL report. Status code: {response.status_code}"}

# import execution
if __name__ == '__main__':
    # VirusTotal API KEY
    api_key = 'd90803045347585458f84cc5d28338496251d41b058a5a4516342e716439e3c4'

    # Input URL
    url_to_scan = str(input("Please input your URL:"))

    scan_result = scan_url(api_key, url_to_scan)
    print(f"Scan Result: {scan_result}\n\n")

    # json report
    if 'scan_id' in scan_result:
        report_result = get_url_report(api_key, scan_result['scan_id'])
        print(f"URL Report: {report_result}")
    else:
        print("Error in scan result, cannot retrieve URL report.")
