import csv
import re
import requests
from urllib.parse import urlparse
import geoip2.database

import dns.resolver

def Is_shortened(url):
    shortening_services = ['goo.gl', 'bit.ly', 'tinyurl.com', 'ow.ly', 't.co', 'is.gd', 'rebrand.ly', 'tiny.cc', 'shorte.st', 'b24.io', 'moourl.com', 'yourls.org', 'hyperlink.to', 'mcaf.ee', 'clkim.com', 'soo.gd', 'firelink.io', 'viralurl.com', 'prettylinkpro.com','reurl.cc', 'picsee.io', 'ssur.cc', 'ifreesite', 'myppt.cc', 'lihi2.com']  # famous shortened

    domain = url.split('//')[-1].split('/')[0] 
    # or domain = = urlparse(url).netloc

    if domain in shortening_services:
        return 1
    else:
        return 0

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

def process_url(url):
    parsed_url = urlparse(url)

    url_length = len(url)

    country = "Unknown"

    validation_date = "2024-04-15"

    shortened = Is_shortened(url)

    domain_spf = has_spf_record(url)

    return {
        'URL': url,
        'URL Length': url_length,
        'Country': country,
        'Validation Date': validation_date,
        'Is Shortened': shortened,
        'Domain_SPF' : domain_spf
    }

def main():
    input_file = './testdata/newone_fortest.csv'  
    output_file = 'main_output.csv'

    with open(input_file, 'r', newline='', encoding='utf-8') as f_input, \
         open(output_file, 'w', newline='', encoding='utf-8') as f_output:
        csv_reader = csv.reader(f_input)
        csv_writer = csv.DictWriter(f_output, fieldnames=['URL', 'URL Length', 'Country', 'Validation Date', 'Is Shortened', 'Domain_SPF'])
        csv_writer.writeheader()

        for row in csv_reader:
            url = row[0] 
            processed_data = process_url(url)
            csv_writer.writerow(processed_data)

if __name__ == '__main__':
    main()
