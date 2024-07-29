import json
import pandas as pd
import codecs

def read_json_file(filename):
    data_list = []
    with codecs.open(filename, 'r', 'utf-8') as file:
        for line_num, line in enumerate(file, start=1):
            try:
                data = json.loads(line)
                data_list.append(data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON at line {line_num} in {filename}: {e}")
    return data_list

def merge_data(dismap_data, httpx_data):
    merged_data = []
    for dismap_entry in dismap_data:
        if 'host' not in dismap_entry or 'port' not in dismap_entry:
            print(f"Skipping invalid dismap entry: {dismap_entry}")
            continue
        matched = False
        for httpx_entry in httpx_data:
            if 'host' not in httpx_entry or 'port' not in httpx_entry:
                print(f"Skipping invalid httpx entry: {httpx_entry}")
                continue
            if dismap_entry['host'] == httpx_entry['host'] and int(dismap_entry['port']) == int(httpx_entry['port']):
                merged_entry = {
                    'host': dismap_entry['host'],
                    'port': dismap_entry['port'],
                    'identify_string': dismap_entry.get('identify.string', None),
                    'protocol': dismap_entry.get('protocol', None),
                    'banner_string': dismap_entry.get('banner.string', None),
                    'url': httpx_entry.get('url', None),
                    'title': httpx_entry.get('title', None),
                    'webserver': httpx_entry.get('webserver', None),
                    'tech': httpx_entry.get('tech', None),
                    'status_code': httpx_entry.get('status_code', None),
                    'content_length': httpx_entry.get('content_length', None)
                }
                merged_data.append(merged_entry)
                matched = True
                break
        
        if not matched:
            merged_entry = {
                'host': dismap_entry['host'],
                'port': dismap_entry['port'],
                'identify_string': dismap_entry.get('identify.string', None),
                'protocol': dismap_entry.get('protocol', None),
                'banner_string': dismap_entry.get('banner.string', None),
                'url': None,
                'title': None,
                'webserver': None,
                'tech': None,
                'status_code': None,
                'content_length': None
            }
            merged_data.append(merged_entry)

    for httpx_entry in httpx_data:
        if 'host' not in httpx_entry or 'port' not in httpx_entry:
            print(f"Skipping invalid httpx entry: {httpx_entry}")
            continue
        matched = False
        for dismap_entry in dismap_data:
            if 'host' not in dismap_entry or 'port' not in dismap_entry:
                print(f"Skipping invalid dismap entry: {dismap_entry}")
                continue
            if httpx_entry['host'] == dismap_entry['host'] and int(httpx_entry['port']) == int(dismap_entry['port']):
                matched = True
                break
        if not matched:
            merged_entry = {
                'host': httpx_entry['host'],
                'port': httpx_entry['port'],
                'identify_string': None,
                'protocol': None,
                'banner_string': None,
                'url': httpx_entry.get('url', None),
                'title': httpx_entry.get('title', None),
                'webserver': httpx_entry.get('webserver', None),
                'tech': httpx_entry.get('tech', None),
                'status_code': httpx_entry.get('status_code', None),
                'content_length': httpx_entry.get('content_length', None)
            }
            merged_data.append(merged_entry)
    
    return merged_data


def write_to_excel(data, output_filename):
    df = pd.DataFrame(data)
    df.to_excel(output_filename, index=False)
    print(f"已将数据成功写入 {output_filename} 文件。")

def main():
    dismap_file = input("请输入Dismap的JSON文件名（包括文件扩展名）：")
    httpx_file = input("请输入HTTPX的JSON文件名（包括文件扩展名）：")

    dismap_data = read_json_file(dismap_file)
    httpx_data = read_json_file(httpx_file)

    merged_data = merge_data(dismap_data, httpx_data)
    write_to_excel(merged_data, "merged_data.xlsx")

if __name__ == "__main__":
    main()
