import re
import json

def classify_urls(input_string, txt_file_path):
    regex_pattern = re.compile(input_string)

    matching_urls = []

    with open(txt_file_path, 'r') as file:
        content = file.read()

        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)

        for url in urls:
            if regex_pattern.search(url):
                matching_urls.append(url)

    return matching_urls

def save_results(matching_urls, output_file_path, input_string):
    results = {
        input_string: matching_urls
    }

    with open(output_file_path, 'a') as output_file:
        json.dump(results, output_file, indent=2)  # indent


input_string = input("請輸入分群的字串：")
txt_file_path = "phishtank_blacklist.txt"
output_file_path = "results.json"

matching_urls = classify_urls(input_string, txt_file_path)
save_results(matching_urls, output_file_path, input_string)

print("已被分入的Url", matching_urls)
print(f"結果已保存至 {output_file_path}")
