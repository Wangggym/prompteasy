import os
import json
import time
import uuid
from typing import Dict, List, Optional, Union, Any
import requests
from urllib.parse import urlparse, parse_qs
from utils import safe_filename, parse_response_content
from dotenv import load_dotenv

load_dotenv()

API_URL: str = os.environ.get(
    'API_URL',
    ''
)

def parse_url_params(url: str) -> Optional[Dict[str, List[str]]]:
    """Parse URL query parameters into a dictionary.
    
    Args:
        url (str): The URL to parse
        
    Returns:
        Optional[Dict[str, List[str]]]: Dictionary of query parameters where values are lists of strings,
        or None if no query parameters exist
    """
    parsed = urlparse(url)
    return parse_qs(parsed.query) if parsed.query else None

def run_case(case_path: str, outputs_dir: str, independent_sessions: bool = False) -> str:
    """Run a test case and save the results.
    
    Args:
        case_path (str): Path to the test case JSON file
        outputs_dir (str): Directory to save the output results
        independent_sessions (bool): Whether to use independent session_id for each request (now only set via test case JSON)
        
    Returns:
        str: Path to the output file
    """
    with open(case_path, 'r', encoding='utf-8') as f:
        case_data: Dict[str, Any] = json.load(f)
    requests_list: List[Dict[str, Any]] = case_data.get('requests', [])

    session_id: str = str(uuid.uuid4()) if not independent_sessions else None
    results: List[Dict[str, Any]] = []
    total: int = len(requests_list)

    for idx, req_body in enumerate(requests_list, 1):
        print(f"    [INFO] Running request {idx}/{total} for case '{os.path.basename(case_path)}'...")
        req_body = dict(req_body)
        if independent_sessions:
            req_body['session_id'] = str(uuid.uuid4())
            print(f"    [INFO] Using independent session_id: {req_body['session_id']}")
        else:
            req_body['session_id'] = session_id
            print(f"    [INFO] Using shared session_id: {session_id}")
            
        params=parse_url_params(API_URL)
        print(params)
        response = requests.post(
            API_URL,
            json=req_body,
            headers={'Content-Type': 'application/json'},
            params=params
        )
        try:
            resp_content: Union[Dict[str, Any], str] = response.json()
        except Exception:
            resp_content: str = response.text
        parsed_content: List[Any] = parse_response_content(resp_content)
        results.append({
            'request_index': idx,
            'request_body': req_body,
            'response_status': response.status_code,
            'response_content': parsed_content,
            'passed': None  # 验收逻辑后续补充
        })

    output: Dict[str, Any] = {
        'results': results,
        'passed': None  # 总体通过与否，后续补充
    }
    case_base: str = os.path.splitext(os.path.basename(case_path))[0]
    now = time.time()
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(now)) + f"_{int((now % 1) * 1000):03d}"
    output_path: str = os.path.join(outputs_dir, f"{safe_filename(case_base)}_output_{timestamp}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"    [INFO] Output written to {output_path}")
    return output_path 