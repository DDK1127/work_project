import pandas as pd

# 读取CSV文件
df = pd.read_csv('domain_dataset_1000.csv', header=None)

# 定义包含特定字段的列表
specific_domains_1 = ['.com.tw', '.com.hk', '.eu', '.gov', '.edu', '.org.tw', '.org.hk', 
                      '.mil', '.ac', '.int', '.gov', '.edu', '.museum', '.aero', '.coop', 
                      '.pro', '.cat', '.gov.uk', '.edu.au', '.sch.uk', '.police.uk']

specific_domains_2 = ['.de', '.it', '.jp', '.fr', '.kr', '.sg', '.au', '.ca', '.nz', '.ie',
                      '.ae', '.br', '.sa', '.mx', '.nl', '.ch', '.uk', '.be', '.at', '.pl',
                      '.se', '.dk', '.cz', '.no', '.ie', '.gr', '.pt']

# 遍历DataFrame中的每一行
for index, row in df.iterrows():
    # 初始化标志
    flag = 0
    # 检查每个元素是否包含特定的字段
    for element in row:
        if any(domain in element for domain in specific_domains_1):
            # 如果找到特定字段，则将标志设置为1并跳出循环
            flag = 1
            break
        elif any(domain in element for domain in specific_domains_2):
            # 如果找到第二组特定字段，则将标志设置为2并跳出循环
            flag = 2
            break
    # 在C列中写入相应的标志
    df.at[index, 2] = flag

# 保存修改后的DataFrame到新的CSV文件
df.to_csv('modified_domain_dataset.csv', index=False, header=False)
