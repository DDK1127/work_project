import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.mixture import GaussianMixture
import numpy as np

# 1. 数据准备
# 从 CSV 文件中读取 URL 数据
df = pd.read_csv('../testdata/newone.csv', header=None)

# 提取 URL 列
urls = df[0].tolist()

# 2. 特征提取
# 使用 TF-IDF 将 URL 转换为向量表示
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(urls).toarray()  # 将稀疏矩阵转换为密集的数据

# 3. GMM 模型拟合
# 使用 BIC 来自动选择最优的群集数量
n_samples, n_features = X.shape
n_components = min(n_samples - 1, 2)  # 设置群集数量为数据样本数量减去 1
gmm = GaussianMixture(n_components=n_components)
gmm.fit(X)

# 4. 分群
cluster_labels = gmm.predict(X)

# 5. 群集分析
# 显示每个群集中的 URL
clusters = {}
for url, label in zip(urls, cluster_labels):
    if label not in clusters:
        clusters[label] = []
    clusters[label].append(url)

for cluster, urls in clusters.items():
    print(f"Cluster {cluster}:")
    for url in urls:
        print(url)
    print()
