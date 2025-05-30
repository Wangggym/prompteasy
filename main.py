import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from case_runner import run_case
from datetime import datetime

TESTCASES_DIR = 'testcases'
OUTPUTS_DIR = 'outputs'
MAX_WORKERS = 4  # 可根据需要调整并发数


def main():
    # 创建带日期和时间戳的输出目录
    now = datetime.now()
    date_dir = now.strftime('%Y%m%d')
    time_dir = now.strftime('%H%M%S')
    run_output_dir = os.path.join(OUTPUTS_DIR, date_dir, time_dir)
    os.makedirs(run_output_dir, exist_ok=True)
    print(f"[INFO] Output directory: {run_output_dir}")

    case_files = [f for f in os.listdir(TESTCASES_DIR) if f.endswith('.json')]
    case_paths = [os.path.join(TESTCASES_DIR, f) for f in case_files]
    print(f"[INFO] Found {len(case_paths)} test cases.")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for case_path in case_paths:
            print(f"[INFO] Submitting case: {case_path}")
            futures[executor.submit(run_case, case_path, run_output_dir)] = case_path
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