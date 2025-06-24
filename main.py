import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from case_runner import run_case
from datetime import datetime
import argparse

TESTCASES_DIR = 'testcases'
OUTPUTS_DIR = 'outputs'
MAX_WORKERS = 4  # 可根据需要调整并发数


def main():
    parser = argparse.ArgumentParser(description='Run test cases')
    parser.add_argument('--case', type=str, help='Specific test case file to run')
    parser.add_argument('--case-keywords', type=str, nargs='*', help='Keywords to filter test case files (OR logic, fuzzy match)')
    parser.add_argument('--repeat', type=int, default=1, help='Number of times to repeat the test case')
    args = parser.parse_args()

    # 创建带日期和时间戳的输出目录
    now = datetime.now()
    date_dir = now.strftime('%Y%m%d')
    time_dir = now.strftime('%H%M%S')
    run_output_dir = os.path.join(OUTPUTS_DIR, date_dir, time_dir)
    os.makedirs(run_output_dir, exist_ok=True)
    print(f"[INFO] Output directory: {run_output_dir}")

    if args.case:
        # Run specific test case
        case_path = os.path.join(TESTCASES_DIR, args.case)
        if not os.path.exists(case_path):
            print(f"[ERROR] Test case {case_path} not found")
            return
        # Read the test case file to check for independent_sessions field
        with open(case_path, 'r', encoding='utf-8') as f:
            case_data = f.read()
        import json
        case_json = json.loads(case_data)
        case_independent_sessions = case_json.get('independent_sessions', False)
        case_paths = [(case_path, case_independent_sessions)] * args.repeat
        print(f"[INFO] Running test case {args.case} {args.repeat} times")
    elif args.case_keywords:
        # Run test cases matching any of the keywords
        case_files = [f for f in os.listdir(TESTCASES_DIR) if f.endswith('.json')]
        filtered_files = [f for f in case_files if any(kw in f for kw in args.case_keywords)]
        if not filtered_files:
            print(f"[ERROR] No test cases found matching keywords: {args.case_keywords}")
            return
        case_paths = []
        for f in filtered_files:
            case_path = os.path.join(TESTCASES_DIR, f)
            with open(case_path, 'r', encoding='utf-8') as cf:
                case_data = cf.read()
            import json
            case_json = json.loads(case_data)
            case_independent_sessions = case_json.get('independent_sessions', False)
            case_paths.append((case_path, case_independent_sessions))
        print(f"[INFO] Found {len(case_paths)} test cases matching keywords: {args.case_keywords}")
    else:
        # Run all test cases
        case_files = [f for f in os.listdir(TESTCASES_DIR) if f.endswith('.json')]
        case_paths = []
        for f in case_files:
            case_path = os.path.join(TESTCASES_DIR, f)
            with open(case_path, 'r', encoding='utf-8') as cf:
                case_data = cf.read()
            import json
            case_json = json.loads(case_data)
            case_independent_sessions = case_json.get('independent_sessions', False)
            case_paths.append((case_path, case_independent_sessions))
        print(f"[INFO] Found {len(case_paths)} test cases.")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for case_path, case_independent_sessions in case_paths:
            print(f"[INFO] Submitting case: {case_path} (independent_sessions={case_independent_sessions})")
            futures[executor.submit(run_case, case_path, run_output_dir, case_independent_sessions)] = case_path
        for i, future in enumerate(as_completed(futures), 1):
            case_path = futures[future]
            try:
                result = future.result()
                print(f"[INFO] ({i}/{len(case_paths)}) Case {case_path} finished: {result}")
            except Exception as e:
                print(f"[ERROR] ({i}/{len(case_paths)}) Case {case_path} failed: {e}")
    print("[INFO] All test cases finished.")


if __name__ == '__main__':
    main() 