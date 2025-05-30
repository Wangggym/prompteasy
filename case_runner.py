import os
import json
import uuid
import requests
from utils import safe_filename, parse_response_content
from dotenv import load_dotenv

load_dotenv()

API_URL = os.environ.get(
    'API_URL',
    ''
)

def run_case(case_path, outputs_dir):
    with open(case_path, 'r', encoding='utf-8') as f:
        case_data = json.load(f)
    requests_list = case_data.get('requests', [])

    session_id = str(uuid.uuid4())
    results = []
    total = len(requests_list)

    for idx, req_body in enumerate(requests_list, 1):
        print(f"    [INFO] Running request {idx}/{total} for case '{os.path.basename(case_path)}'...")
        req_body = dict(req_body)
        req_body['session_id'] = session_id
        response = requests.post(
            API_URL,
            json=req_body,
            headers={'Content-Type': 'application/json'}
        )
        try:
            resp_content = response.json()
        except Exception:
            resp_content = response.text
        parsed_content = parse_response_content(resp_content)
        results.append({
            'request_index': idx,
            'request_body': req_body,
            'response_status': response.status_code,
            'response_content': parsed_content,
            'passed': None  # 验收逻辑后续补充
        })

    output = {
        'results': results,
        'passed': None  # 总体通过与否，后续补充
    }
    case_base = os.path.splitext(os.path.basename(case_path))[0]
    output_path = os.path.join(outputs_dir, f"{safe_filename(case_base)}_output.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"    [INFO] Output written to {output_path}")
    return output_path 