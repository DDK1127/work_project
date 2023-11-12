import dns.resolver

def auto_detect_domain_type(domain):
    query_types = ['A', 'AAAA', 'MX', 'CNAME', 'NS', 'TXT', 'SOA']

    for qtype in query_types:
        try:
            result = dns.resolver.resolve(domain, qtype)
            for rdata in result:
                print(f"{domain} ({qtype}): {rdata}")

            break
        except dns.resolver.NXDOMAIN:
            print(f"{domain} not exist.")
            break
        except dns.resolver.NoAnswer:
            continue
        except Exception as e:
            print(f"Search {domain} error: {e}")

domain = input("input your URL: ")
auto_detect_domain_type(domain)
