#下載bad_url.txt = bad_output.csv和aka_url.txt即可執行
import re
import tldextract

def tear_down(url):
    # 要移除的常見子域名
    common_subdomains = ["www", "mail", "blog", "shop", "forum", "news", "app", "api", "cdn", "img", "dev"]

    # 使用 tldextract 提取域名的各個部分
    extracted = tldextract.extract(url)

    # 移除通用頂級域名（gTLD）和國家代碼頂級域名（ccTLD）
    url = url.replace(f'.{extracted.suffix}', '')

    # 移除 http:// 或 https://
    url = re.sub(r'https?://', '', url)

    # 移除常見子域名
    for subdomain in common_subdomains:
        url = re.sub(fr'\b{subdomain}\.', '', url)

    # 使用 "." 和 "/" 分割 URL
    url_parts = re.split(r'[./-]', url)

    # 移除空字串
    url_parts = [part for part in url_parts if part]

    # 正規化
    url_parts = [word.lower().replace('0', 'o').replace('1', 'l').replace('&', 'g') for word in url_parts]
    return url_parts

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]

        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)

            current_row.append(min(insertions, deletions, substitutions))

        previous_row = current_row

    return previous_row[-1]

def find_most_similar_word(input_url, target_word):
    min_distance = float('inf')
    most_similar_word = ""

    for i in range(len(input_url) - len(target_word) + 1):
        substring = input_url[i:i+len(target_word)]
        distance = levenshtein_distance(substring, target_word)

        if distance < min_distance:
            min_distance = distance
            most_similar_word = substring

    return most_similar_word, min_distance




#----------------------------input-------------------------------#

with open('bad_url.txt', 'r') as file:
    input_url = [line.strip() for line in file]

with open('aka_url.txt', 'r') as file:
    target_word = [line.split('.')[0].strip() for line in file]

#----------------------------input-------------------------------#
    
# 清空distance.txt
with open("Grouped.txt", "w") as file:
    file.write("")

with open("Grouped.txt", "a") as file:
    for origin_url in input_url:
        most_similase_url = 'nothing'
        most_similase_unm = 1.0
        for j in target_word:
            teared = tear_down(origin_url)
            min_levenshtein = 100
            levenshtein_similase = 1.0
            similar = "null"
            for i in teared:
                most_similar_word, levenshtein_dist = find_most_similar_word(i, j)#找出與target_word最相似的most_similar_word
                if most_similar_word == j:
                    min_levenshtein = 0
                    levenshtein_similase = 0.0
                    similar = j
                    break
                if levenshtein_dist < min_levenshtein:
                    min_levenshtein = levenshtein_dist
                    similar = most_similar_word

            if levenshtein_similase == 1.0:
                levenshtein_similase = min_levenshtein/len(j)
            # print(f"Origin: '{j}' Similar: '{similar}' levenshtein_similase: '{levenshtein_similase:.5f}'")#記錄這三個

            is_imitate_value = 0.5

            if len(j) <= 4:
                is_imitate_value = 0.0
            elif j[0].lower() != similar[0].lower():#首字母
                is_imitate_value = 0.25
            elif len(j) <= 6:
                is_imitate_value = 0.4
            
            if levenshtein_similase <= is_imitate_value and levenshtein_similase < most_similase_unm:
                most_similase_unm = levenshtein_similase
                most_similase_url = j
        print(origin_url+' '+most_similase_url)




