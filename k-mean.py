from difflib import SequenceMatcher
from sklearn.cluster import KMeans

# 已知的 URL
known_urls = [
    "https://www.google.com",
    "https://www.facebook.com",
    # 更多已知 URL ...
]

# 疑似 URL
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
    "https://www.faeebook.com",
    "https://www.qwertyhgfds.com",
    "https://www.dshe67%g%yuy%6.com",
    "https://www.googledrive.com",
    "https://erl.ddifjidjjfidjifgoogledrive.com",
]

# 提取域名后的部分
def extract_domain_part(url):
    return url.split("www.", 1)[-1]

# 正規化函數，將一些相似的字視為相同
def normalize_url(url):
    url = url.lower()  # 將 URL 轉換為小寫
    url = url.replace('0', 'o')  # 將 0 視為 o
    url = url.replace('1', 'l')  # 將 1 視為 l(L)
    url = url.replace('g', '&')  # 將 1 視為 l
    # 可以添加更多的正規化規則

    return url

# 移除 URL 的 https://www. 部分
def remove_prefix(urls):
    return [extract_domain_part(url) for url in urls]

# 移除前綴部分
known_urls_without_prefix = remove_prefix(known_urls)
suspicious_urls_without_prefix = remove_prefix(suspicious_urls)

# 計算相似度矩陣
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

# 計算相似度矩陣
similarities_matrix = calculate_similarity_matrix(suspicious_urls_without_prefix, known_urls_without_prefix)

# 定義相似度閾值
threshold = 0.5

# 使用 K-means 聚類
num_clusters = len(known_urls_without_prefix)  # 假設與已知網站數量相同的群數
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(similarities_matrix)
clusters = kmeans.labels_

# 將 URL 分群
url_clusters = {'unknown_urls': []}
for i, suspicious_url in enumerate(suspicious_urls):
    similarity = max(similarities_matrix[i])  # 使用最大相似度作為該 URL 的相似度
    if similarity < threshold:
        url_clusters['unknown_urls'].append(suspicious_url)
    else:
        cluster_label = clusters[i]
        if cluster_label not in url_clusters:
            url_clusters[cluster_label] = [suspicious_url]
        else:
            url_clusters[cluster_label].append(suspicious_url)

# 顯示分群結果
for cluster_label, cluster_urls in url_clusters.items():
    print(f"Cluster {cluster_label}: {cluster_urls}")
