import subprocess
import os
import time

CPP_FILE = 'solution.cpp'
EXEC_FILE = 'solution.exe'
TESTCASE_DIR = './testcases'
CASE_COUNT_FILE = 'cases.txt'
RESULT_FILE = 'results.txt'

def compile_cpp():
    result = subprocess.run(
        ['g++', CPP_FILE, '-o', EXEC_FILE],
        capture_output=True, text=True
    )
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
        return int(line) if line.isdigit() else 0

def compare_outputs(expected: str, actual: str):
    exp_lines = expected.strip().splitlines()
    act_lines = actual.strip().splitlines()
    diffs = []
    for i in range(max(len(exp_lines), len(act_lines))):
        e = exp_lines[i] if i < len(exp_lines) else "(없음)"
        a = act_lines[i] if i < len(act_lines) else "(없음)"
        if e != a:
            diffs.append((i+1, e, a))
    return diffs

def warmup_exe():
    """첫 실행 지연을 방지하기 위한 워밍업 실행"""
    try:
        subprocess.run([EXEC_FILE], input="\n", capture_output=True,
                       text=True, timeout=1)
    except:
        pass

def run_tests():
    case_count = read_case_count()
    if case_count == 0:
        with open(RESULT_FILE, 'w', encoding='utf-8') as out:
            out.write("예제 수가 0이거나 cases.txt 파일이 없습니다.\n")
        return

    lines = []
    passed = 0

    warmup_exe()  # 첫 실행 준비

    for i in range(1, case_count+1):
        in_path = os.path.join(TESTCASE_DIR, f'input{i}.txt')
        out_path = os.path.join(TESTCASE_DIR, f'output{i}.txt')
        if not os.path.exists(in_path) or not os.path.exists(out_path):
            lines.append(f"[Case {i}] 입력 또는 출력 파일이 없습니다.\n")
            continue

        with open(in_path, 'r') as f: input_data = f.read()
        with open(out_path, 'r') as f: expected = f.read().strip()

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
        except subprocess.TimeoutExpired:
            lines.append(f"[Case {i}] 시간 초과\n")
            continue

        elapsed_ms = int((end - start)*1000)
        actual = result.stdout.strip()
        stderr = result.stderr.strip()

        lines.append(f"[Case {i}] 실행 시간: {elapsed_ms} ms\n")

        # 1) 반환 코드가 0이 아니면 런타임 오류로 처리
        if result.returncode != 0:
            err_msg = stderr or f"비정상 종료 (return code {result.returncode})"
            lines.append(f"[Case {i}] 실행 중 오류 발생:\n{err_msg}\n\n")
            continue

        # 2) 정상 실행된 경우
        if actual == expected:
            passed += 1
            lines.append(f"[Case {i}] 정답\n\n")
        else:
            lines.append(f"[Case {i}] 오답\n\n")
            lines.append("입력:\n" + input_data + "\n")
            lines.append("기대 출력:\n" + expected + "\n")
            lines.append("실제 출력:\n" + actual + "\n\n")
            diffs = compare_outputs(expected, actual)
            if diffs:
                lines.append("차이:\n")
                for ln, e, a in diffs:
                    lines.append(f"[Line {ln}]\n기대: {e}\n실제: {a}\n")
            lines.append("-"*40 + "\n")

    lines.append(f"\n총 {case_count}개 중 {passed}개 정답\n")

    with open(RESULT_FILE, 'w', encoding='utf-8') as out:
        out.writelines(lines)

if __name__ == '__main__':
    if compile_cpp():
        run_tests()
        print("테스트 실행 완료. 결과는 results.txt 파일을 확인하세요.")
    else:
        print("컴파일 오류가 발생했습니다. results.txt 파일을 확인하세요.")

    # 실행 파일 삭제
    if os.path.exists(EXEC_FILE):
        os.remove(EXEC_FILE)
