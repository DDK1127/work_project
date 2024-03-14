from difflib import SequenceMatcher
from sklearn.cluster import KMeans

# known urls
known_urls = [
    "https://www.google.com",
    "https://www.facebook.com",
    "https://www.youtube.com",
    "https://www.yahoo.com",
    "https://www.amazon.com",
    "https://www.wikipedia.org",
    "https://www.qq.com",
    "https://www.twitter.com",
]

# suspicious urls or phishing urls
suspicious_urls = [
    "https://www.g00gle.com",
    "https://www.faceb00k.com",
    "https://www.g00gle.com",
    "https://www.faceb000k.com",
    "https://www.gooogle.com",
    "https://www.faceboook.com",
    "https://www.googlc.com",
    "https://www.faccbook.com",
    "https://www.&00&le.com",
    "https://www.faeebook.com",
    "https://www.farebook.com",
    "https://www.faeebook.com",
    "https://www.qwertyhgfds.com",
    "https://www.dshe67%g%yuy%6.com",
    "https://www.googledrive.com",
    "https://erl.ddifjidjjfidjifgoogledrive.com",
    "https://www.gaagle.com.tw",
    "https://www.goggle.com",
    "https://www.youtubee.com",
]

# take domain part of url
def extract_domain_part(url):
    return url.split("www.", 1)[-1]

# regularize url
def normalize_url(url):
    url = url.lower()  # 將 URL 轉換為小寫
    url = url.replace('0', 'o')  # 將 0 視為 o
    url = url.replace('1', 'l')  # 將 1 視為 l(L)
    url = url.replace('g', '&')  # 將 1 視為 l
    # add more regular expression here

    return url

# rm http:// or https:// in urls
def remove_prefix(urls):
    return [extract_domain_part(url) for url in urls]

# remove prefix
known_urls_without_prefix = remove_prefix(known_urls)
suspicious_urls_without_prefix = remove_prefix(suspicious_urls)

# calculate similarity matrix
def calculate_similarity_matrix(suspicious_urls, known_urls):
    similarities = []
    for suspicious_url in suspicious_urls:
        sim = []
        normalized_suspicious_url = normalize_url(suspicious_url)
        for known_url in known_urls:
            normalized_known_url = normalize_url(known_url)
            matcher = SequenceMatcher(None, normalized_suspicious_url, normalized_known_url)
            similarity = matcher.ratio()
            sim.append(similarity)
        similarities.append(sim)
    return similarities

# calculate similarity matrix
similarities_matrix = calculate_similarity_matrix(suspicious_urls_without_prefix, known_urls_without_prefix)

# define threshold
threshold = 0.5

# use k-means to group urls
num_clusters = len(known_urls_without_prefix)  #set number of clusters
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(similarities_matrix)
clusters = kmeans.labels_

# group urls
url_clusters = {'unknown_urls': []}
for i, suspicious_url in enumerate(suspicious_urls):
    similarity = max(similarities_matrix[i])  # use max similarity as similarity of url
    if similarity < threshold:
        url_clusters['unknown_urls'].append(suspicious_url)
    else:
        cluster_label = clusters[i]
        if cluster_label not in url_clusters:
            url_clusters[cluster_label] = [suspicious_url]
        else:
            url_clusters[cluster_label].append(suspicious_url)

# show result
for cluster_label, cluster_urls in url_clusters.items():
    print(f"Cluster {cluster_label}: {cluster_urls}")
