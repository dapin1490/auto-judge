import subprocess
import os
import time

CPP_FILE = 'solution.cpp'
EXEC_FILE = 'solution.exe'
TESTCASE_DIR = './testcases'
CASE_COUNT_FILE = 'cases.txt'
RESULT_FILE = 'results.txt'

def compile_cpp():
    result = subprocess.run(['g++', CPP_FILE, '-o', EXEC_FILE], capture_output=True, text=True)
    if result.returncode != 0:
        with open(RESULT_FILE, 'w', encoding='utf-8') as out:
            out.write("컴파일 오류:\n")
            out.write(result.stderr)
        return False
    return True

def read_case_count():
    if not os.path.exists(CASE_COUNT_FILE):
        return 0
    with open(CASE_COUNT_FILE, 'r') as f:
        line = f.readline().strip()
        if not line.isdigit():
            return 0
        return int(line)

def compare_outputs(expected: str, actual: str):
    expected_lines = expected.strip().splitlines()
    actual_lines = actual.strip().splitlines()
    max_len = max(len(expected_lines), len(actual_lines))

    differences = []
    for i in range(max_len):
        expected_line = expected_lines[i] if i < len(expected_lines) else "(없음)"
        actual_line = actual_lines[i] if i < len(actual_lines) else "(없음)"
        if expected_line != actual_line:
            differences.append((i + 1, expected_line, actual_line))
    return differences

def warmup_exe():
    """첫 실행 지연을 방지하기 위한 워밍업 실행"""
    try:
        subprocess.run([EXEC_FILE], input="\n", capture_output=True, text=True, timeout=1)
    except Exception:
        pass

def run_tests():
    case_count = read_case_count()
    if case_count == 0:
        with open(RESULT_FILE, 'w', encoding='utf-8') as out:
            out.write("예제 수가 0이거나 cases.txt 파일이 없습니다.\n")
        return

    passed = 0
    lines = []

    warmup_exe()  # 첫 실행 준비

    for i in range(1, case_count + 1):
        input_path = os.path.join(TESTCASE_DIR, f'input{i}.txt')
        expected_path = os.path.join(TESTCASE_DIR, f'output{i}.txt')

        if not os.path.exists(input_path) or not os.path.exists(expected_path):
            lines.append(f"[Case {i}] 입력 또는 출력 파일이 없습니다.\n")
            continue

        with open(input_path, 'r') as f:
            input_data = f.read()
        with open(expected_path, 'r') as f:
            expected_output = f.read().strip()

        try:
            start = time.perf_counter()
            result = subprocess.run(
                [EXEC_FILE],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=10
            )
            end = time.perf_counter()
            elapsed_ms = int((end - start) * 1000)
            actual_output = result.stdout.strip()
        except subprocess.TimeoutExpired:
            lines.append(f"[Case {i}] 시간 초과\n")
            continue

        lines.append(f"[Case {i}] 실행 시간: {elapsed_ms} ms\n")

        if actual_output == expected_output:
            passed += 1
            lines.append(f"[Case {i}] 정답\n\n")
        else:
            lines.append(f"[Case {i}] 오답\n\n")
            lines.append("입력:\n" + input_data + "\n")
            lines.append("기대 출력:\n" + expected_output + "\n")
            lines.append("실제 출력:\n" + actual_output + "\n\n")

            diffs = compare_outputs(expected_output, actual_output)
            if diffs:
                lines.append("차이:\n")
                for line_num, expected_line, actual_line in diffs:
                    lines.append(f"[Line {line_num}]\n기대: {expected_line}\n실제: {actual_line}\n")
            lines.append("-" * 40 + "\n")

    lines.append(f"\n총 {case_count}개 중 {passed}개 정답\n")

    with open(RESULT_FILE, 'w', encoding='utf-8') as out:
        out.writelines(lines)

if __name__ == '__main__':
    if compile_cpp():
        run_tests()
        print("테스트 실행 완료. 결과는 results.txt 파일을 확인하세요.")
    else:
        print("컴파일 오류가 발생했습니다. results.txt 파일을 확인하세요.")

    if os.path.exists(EXEC_FILE):
        os.remove(EXEC_FILE)
