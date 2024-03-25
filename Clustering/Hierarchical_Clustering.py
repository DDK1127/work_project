import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from collections import defaultdict

# 读取文本文件
with open("../testdata/Grouping_to_db_phishtank_blacklist.txt", "r") as file:
    # 逐行读取文件内容
    urls = file.readlines()

# 去除每行末尾的换行符
urls = [url.strip() for url in urls]

# TF-IDF向量化
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(urls)

# 计算TF-IDF向量之间的余弦相似度
cosine_sim = cosine_similarity(X)

# 执行层次聚类
clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=1.5, linkage='average').fit(cosine_sim)

# 将URL分配给聚类
clusters = clustering.labels_

# 创建一个字典，用于将相同聚类的URL放在一起
cluster_dict = defaultdict(list)
for i, url in enumerate(urls):
    cluster_dict[clusters[i]].append(url)

# 输出将相同聚类的URL按照聚类顺序放在一起
for cluster in sorted(cluster_dict.keys()):
    urls_in_cluster = cluster_dict[cluster]
    print(f"Cluster {cluster}:")
    for url in urls_in_cluster:
        print(url)
    print()  # 打印一个空行来区分不同的聚类
