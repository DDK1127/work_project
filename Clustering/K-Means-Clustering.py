from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from kneed import KneeLocator
from collections import defaultdict
import matplotlib.pyplot as plt


def read_url_list_from_txt(file_path):
    with open(file_path, 'r') as file:
        urls = file.readlines()
    # Remove trailing newline characters
    urls = [url.strip() for url in urls]
    return urls

def find_optimal_clusters(data, max_k=10):
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(data)

    # Normalize the TF-IDF matrix
    tfidf_matrix_normalized = normalize(tfidf_matrix)

    # Calculate cosine similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix_normalized)

    # Calculate distortions for different cluster numbers
    distortions = []
    for i in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(similarity_matrix)
        distortions.append(kmeans.inertia_)

    # Find the "elbow" point using KneeLocator
    knee_locator = KneeLocator(range(1, max_k + 1), distortions, curve='convex', direction='decreasing')
    optimal_clusters = knee_locator.elbow

    # Plot the elbow
    knee_locator.plot_knee()
    plt.show()

    return optimal_clusters

def kmeans_cluster(data, num_clusters):
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(data)

    # Normalize the TF-IDF matrix
    tfidf_matrix_normalized = normalize(tfidf_matrix)

    # Calculate cosine similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix_normalized)

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    clusters = kmeans.fit_predict(similarity_matrix)

    return clusters

def main():
    file_path = '../testdata/Grouped.txt'  # replace with your file path
    urls = read_url_list_from_txt(file_path)

    # You can choose the maximum number of clusters to consider
    max_clusters = 1000

    # Find optimal number of clusters using KneeLocator
    optimal_clusters = find_optimal_clusters(urls, max_k=max_clusters)

    # Apply KMeans clustering with the optimal number of clusters
    clusters = kmeans_cluster(urls, optimal_clusters)

    grouped_urls = defaultdict(list)
    for url, cluster in zip(urls, clusters):
        grouped_urls[cluster].append(url)

    for cluster, urls_in_cluster in grouped_urls.items():
        print(f'Cluster {cluster + 1}:')
        for url in urls_in_cluster:
            print(f'  - {url}')
        print('\n')

if __name__ == "__main__":
    main()
