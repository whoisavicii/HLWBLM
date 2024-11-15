import json
import pandas as pd
import codecs
import os
from pathlib import Path
from datetime import datetime

def read_json_file(filename):
    try:
        data_list = []
        with codecs.open(filename, 'r', 'utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line)
                    data_list.append(data)
                except json.JSONDecodeError as e:
                    print(f"解析JSON行时出错: {e}")
                    continue
        return data_list
    except IOError as e:
        print(f"读取文件 {filename} 时出错: {e}")
        return []

def merge_data(dismap_data, httpx_data):
    def format_tech(tech_value):
        """将tech字段转换为空格分隔的字符串"""
        if not tech_value:
            return None
        if isinstance(tech_value, list):
            return ' '.join(tech_value)
        return str(tech_value)

    httpx_dict = {(entry['host'], int(entry['port'])): entry for entry in httpx_data}
    
    # 用于存储已处理的条目
    processed_entries = set()
    merged_data = []
    
    # 首先按host和port对dismap数据进行分组
    dismap_groups = {}
    for entry in dismap_data:
        key = (entry['host'], int(entry['port']))
        if key not in dismap_groups:
            dismap_groups[key] = []
        dismap_groups[key].append(entry)
    
    # 处理每组dismap数据
    for key, entries in dismap_groups.items():
        if len(entries) > 1:
            # 可能存在http到https重定向
            http_entry = None
            https_entry = None
            for entry in entries:
                if entry.get('protocol') == 'http' and entry.get('identify.string') == '[400]':
                    http_entry = entry
                elif entry.get('protocol') == 'https':
                    https_entry = entry
            
            if http_entry and https_entry:
                # 合并http和https的信息
                httpx_entry = httpx_dict.get(key)
                merged_entry = {
                    'host': https_entry['host'],
                    'port': https_entry['port'],
                    'identify_string': https_entry.get('identify.string'),
                    'protocol': 'https',
                    'banner_string': https_entry.get('banner.string'),
                    'url': httpx_entry.get('url') if httpx_entry else None,
                    'title': httpx_entry.get('title') if httpx_entry else None,
                    'webserver': httpx_entry.get('webserver') if httpx_entry else None,
                    'tech': format_tech(httpx_entry.get('tech')) if httpx_entry else None,
                    'status_code': httpx_entry.get('status_code') if httpx_entry else None,
                    'content_length': httpx_entry.get('content_length') if httpx_entry else None,
                    'redirect_note': None
                }
                merged_data.append(merged_entry)
                processed_entries.add(key)
                if httpx_entry:
                    del httpx_dict[key]
                continue
        
        # 处理普通条目
        for entry in entries:
            if key in processed_entries:
                continue
                
            httpx_entry = httpx_dict.get(key)
            merged_entry = {
                'host': entry['host'],
                'port': entry['port'],
                'identify_string': entry.get('identify.string'),
                'protocol': entry.get('protocol'),
                'banner_string': entry.get('banner.string'),
                'url': httpx_entry.get('url') if httpx_entry else None,
                'title': httpx_entry.get('title') if httpx_entry else None,
                'webserver': httpx_entry.get('webserver') if httpx_entry else None,
                'tech': format_tech(httpx_entry.get('tech')) if httpx_entry else None,
                'status_code': httpx_entry.get('status_code') if httpx_entry else None,
                'content_length': httpx_entry.get('content_length') if httpx_entry else None,
                'redirect_note': None
            }
            merged_data.append(merged_entry)
            processed_entries.add(key)
            if httpx_entry:
                del httpx_dict[key]
    
    # 添加未匹配的httpx条目
    for httpx_entry in httpx_dict.values():
        merged_entry = {
            'host': httpx_entry['host'],
            'port': httpx_entry['port'],
            'identify_string': None,
            'protocol': None, 
            'banner_string': None,
            'url': httpx_entry.get('url'),
            'title': httpx_entry.get('title'),
            'webserver': httpx_entry.get('webserver'),
            'tech': format_tech(httpx_entry.get('tech')),
            'status_code': httpx_entry.get('status_code'),
            'content_length': httpx_entry.get('content_length'),
            'redirect_note': None
        }
        merged_data.append(merged_entry)
    
    return merged_data

def validate_input_file(filename: str) -> bool:
    """验证输入文件是否存在且是JSON格式"""
    if not filename.endswith('.json'):
        print(f"错误: {filename} 不是JSON文件")
        return False
    if not os.path.exists(filename):
        print(f"错误: 文件 {filename} 不存在")
        return False
    return True

def ensure_excel_extension(filename: str) -> str:
    """确保文件名有.xlsx后缀"""
    if not filename.lower().endswith('.xlsx'):
        filename += '.xlsx'
    return filename

def write_to_excel(data, output_filename):
    try:
        # 确保输出目录存在
        output_path = Path(output_filename).parent
        output_path.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame(data)
        output_filename = ensure_excel_extension(output_filename)
        df.to_excel(output_filename, index=False)
        print(f"已将数据成功写入 {output_filename} 文件。")
    except PermissionError:
        print(f"错误: 无法写入文件 {output_filename}，可能是文件被占用")
    except Exception as e:
        print(f"写入Excel文件时出错: {e}")

def main():
    try:
        # 默认文件名
        dismap_file = "dismap.json"
        httpx_file = "httpx.json"
        
        # 检查默认文件是否存在
        if not os.path.exists(dismap_file):
            print(f"未找到默认的 {dismap_file}")
            while True:
                dismap_file = input("请输入Dismap的JSON文件名（包括文件扩展名）：")
                if validate_input_file(dismap_file):
                    break
        
        if not os.path.exists(httpx_file):
            print(f"未找到默认的 {httpx_file}")
            while True:    
                httpx_file = input("请输入HTTPX的JSON文件名（包括文件扩展名）：")
                if validate_input_file(httpx_file):
                    break
        
        # 生成带时间戳的输出文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"merged_data_{timestamp}.xlsx"
        
        print("正在读取Dismap数据...")
        dismap_data = read_json_file(dismap_file)
        if not dismap_data:
            print("错误: 未能读取到Dismap数据")
            return
        print(f"已读取 {len(dismap_data)} 条Dismap记录")
        
        print("正在读取HTTPX数据...")
        httpx_data = read_json_file(httpx_file)
        if not httpx_data:
            print("错误: 未能读取到HTTPX数据")
            return
        print(f"已读取 {len(httpx_data)} 条HTTPX记录")
        
        print("正在合并数据...")
        merged_data = merge_data(dismap_data, httpx_data)
        if not merged_data:
            print("错误: 数据合并失败")
            return
        print(f"合并完成,共 {len(merged_data)} 条记录")
        
        write_to_excel(merged_data, output_file)
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")

if __name__ == "__main__":
    main()
