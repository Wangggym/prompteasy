import xml.etree.ElementTree as ET
import json

def xml_to_string(xml_file_path):
    # 读取文件内容
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
        
    # 将XML内容转换为JSON字符串格式
    # 这样可以确保所有特殊字符都被正确转义
    json_str = json.dumps(xml_content)
    
    # 移除开头和结尾的引号（可选，取决于你的需求）
    # json_str = json_str[1:-1]
    
    return json_str

if __name__ == "__main__":
    # 替换为你的XML文件路径
    xml_file_path = "window_dump_choose_gift_for_mom.uix"
    xml_string = xml_to_string(xml_file_path)
    print(xml_string)
    
    # 也可以将结果保存到文件中
    with open('postman_string.txt', 'w', encoding='utf-8') as f:
        f.write(xml_string)