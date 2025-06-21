# C++ 자동 채점 프로그램
- 답안 작성: [solution.cpp](solution.cpp)
- 예제 입력: [testcases/](testcases/)
- CLI 실행 결과 확인: [results.txt](results.txt)
- 시간 측정 기능은 있으나 메모리 측정 기능은 실행 환경에 따른 부정확성 이슈로 없음.
- Window OS 한정 실행 가능, gcc 설치 및 환경 세팅 완료되어 있어야 함.

## CLI 버전
```shell
python auto_judge_cli.py
```

## GUI 버전
```shell
pyinstaller --noconfirm --onefile --windowed auto_judge_gui.py --distpath .
```

이후 exe 실행