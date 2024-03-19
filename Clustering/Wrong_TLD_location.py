# 从 string.txt 中逐行读取字符串
with open("large_badurl.txt", "r") as file:
    strings = file.readlines()

# 从 substring.txt 中逐行读取子字符串
with open("TLD.txt", "r") as file:
    substrings = file.readlines()

# 遍历每个字符串和子字符串
for string in strings:
    string = string.strip()  # 去除行尾的换行符和空格
    origin_string = string
    parts = string.split('/')
    string = '/'.join(parts[3:])
    if string.strip():
        for substring in substrings:
            substring = substring.strip()  # 去除行尾的换行符和空格

            start_index = 0
            while True:
                index = string.find(substring, start_index)
                if index == -1:
                    break

                if index > 0:
                    before = string[index - 1]
                else:
                    before = None

                if index + len(substring) < len(string):
                    after = string[index + len(substring)]
                else:
                    after = None
                if str(before).isalpha() != 1 and str(after).isalpha() != 1:
                    if len(substring) >= 3:
                        print(origin_string+' '+substring+' '+str(before)+' '+str(after))
                    elif before.isdigit() != 1 and after.isdigit() != 1:
                        print(origin_string+' '+substring+' '+str(before)+' '+str(after))
                start_index = index + 1

            
                # print("字符串:", string)
                # print("子字符串:", substring)
                # print("前面的字符:", before)
                # print("后面的字符:", after)
        
