from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def find_similar_urls(input_url, file_path='phishtank_blacklist.txt', threshold=0.75):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.readlines()

    similar_urls = []

    for url in data:
        similarity = similar(input_url, url.strip())
        if similarity > threshold:
            similar_urls.append((url.strip(), similarity))

    return similar_urls

if __name__ == "__main__":
    input_url = input("請輸入URL: ")
    similar_urls = find_similar_urls(input_url)

    if similar_urls:
        print(f"相似度超過80%的URL：")
        for url, similarity_score in similar_urls:
            print(f"URL: {url}, 相似度分數: {similarity_score}")
    else:
        print("沒有找到相似度超過80%的URL。")
