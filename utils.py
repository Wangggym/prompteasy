import re
import json

def safe_filename(name):
    # 只保留字母、数字、下划线，其他替换为下划线
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)


def parse_response_content(resp_content):
    # 如果是字符串且包含 data:，则按行处理
    if isinstance(resp_content, str) and 'data:' in resp_content:
        lines = [line.strip() for line in resp_content.splitlines() if line.strip()]
        result = []
        for line in lines:
            if line.startswith('data:'):
                data_str = line[len('data:'):].strip()
                try:
                    data_json = json.loads(data_str)
                    result.append(data_json)
                except Exception:
                    result.append(data_str)
            else:
                result.append(line)
        return result
    # 如果本身就是 JSON 可格式化
    if isinstance(resp_content, dict) or isinstance(resp_content, list):
        return [resp_content] if isinstance(resp_content, dict) else resp_content
    return [resp_content] 