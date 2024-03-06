import csv

def split_csv(input_file, good_output_file, bad_output_file):
    with open(input_file, 'r', newline='') as csvfile, \
         open(good_output_file, 'w', newline='') as good_csv, \
         open(bad_output_file, 'w', newline='') as bad_csv:
        
        reader = csv.reader(csvfile)
        good_writer = csv.writer(good_csv)
        bad_writer = csv.writer(bad_csv)
        
        for row in reader:
            if row and (row[-1] == 'good' or row[-1] == 'bad'):
                status = row[-1]
                row = row[:-1]  # 移除最後一個元素
                if status == 'good':
                    good_writer.writerow(row)
                else:
                    bad_writer.writerow(row)

# 使用範例
input_file = 'phishing_site_urls.csv'
good_output_file = 'good_output.csv'
bad_output_file = 'bad_output.csv'

split_csv(input_file, good_output_file, bad_output_file)
