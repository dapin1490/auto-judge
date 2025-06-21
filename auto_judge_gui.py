import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QPlainTextEdit, QMessageBox, QScrollArea, QFrame
)
import time


class TestCaseWidget(QFrame):
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.input_edit = QPlainTextEdit()
        self.output_edit = QPlainTextEdit()

        layout.addWidget(QLabel(f"입력 #{self.index}"))
        layout.addWidget(self.input_edit)
        layout.addWidget(QLabel(f"출력 #{self.index}"))
        layout.addWidget(self.output_edit)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

    def get_input_output(self):
        return self.input_edit.toPlainText(), self.output_edit.toPlainText()

class JudgeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("C++ 자동 채점기")
        self.testcases = []
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 버튼 영역
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("테스트케이스 추가")
        self.remove_button = QPushButton("삭제")
        self.judge_button = QPushButton("채점 실행")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.judge_button)
        self.main_layout.addLayout(button_layout)

        # 스크롤 가능한 테스트케이스 영역
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_area_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.main_layout.addWidget(self.scroll_area)

        # 결과 출력
        self.result_display = QPlainTextEdit()
        self.result_display.setReadOnly(True)
        self.main_layout.addWidget(QLabel("결과"))
        self.main_layout.addWidget(self.result_display)

        self.add_button.clicked.connect(self.add_testcase)
        self.remove_button.clicked.connect(self.remove_testcase)
        self.judge_button.clicked.connect(self.run_judge)

        self.add_testcase()  # 기본 1개

    def add_testcase(self):
        widget = TestCaseWidget(len(self.testcases) + 1)
        self.testcases.append(widget)
        self.scroll_layout.addWidget(widget)

    def remove_testcase(self):
        if self.testcases:
            widget = self.testcases.pop()
            self.scroll_layout.removeWidget(widget)
            widget.deleteLater()

    def compile_cpp(self):
        result = subprocess.run(['g++', 'solution.cpp', '-o', 'solution.exe'],
                                capture_output=True, text=True)
        if result.returncode != 0:
            return False, result.stderr
        return True, ""

    def warmup_exe(self):
        try:
            subprocess.run(["solution.exe"], input="\n", capture_output=True, text=True, timeout=2)
        except Exception:
            pass  # 실제 출력 무시

    def run_judge(self):
        success, error_msg = self.compile_cpp()
        if not success:
            self.result_display.setPlainText("컴파일 오류:\n" + error_msg)
            return

        self.result_display.clear()
        self.warmup_exe()

        passed = 0
        total = len(self.testcases)

        for i, case in enumerate(self.testcases, start=1):
            input_text, expected_output = case.get_input_output()
            expected_output = expected_output.strip()
            try:
                start_time = time.perf_counter()

                proc = subprocess.Popen(
                    ['solution.exe'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                stdout, stderr = proc.communicate(input=input_text, timeout=2)
                end_time = time.perf_counter()
                actual_output = stdout.strip()

                elapsed_ms = int((end_time - start_time) * 1000)

            except subprocess.TimeoutExpired:
                proc.kill()
                self.result_display.appendPlainText(f"[Case {i}] 시간 초과\n")
                continue

            self.result_display.appendPlainText(f"[Case {i}] 실행 시간: {elapsed_ms} ms")

            if actual_output == expected_output:
                passed += 1
                self.result_display.appendPlainText(f"[Case {i}] 정답")
            else:
                self.result_display.appendPlainText(f"[Case {i}] 오답")
                self.result_display.appendPlainText("입력:\n" + input_text)
                self.result_display.appendPlainText("기대 출력:\n" + expected_output)
                self.result_display.appendPlainText("실제 출력:\n" + actual_output)

                exp_lines = expected_output.splitlines()
                act_lines = actual_output.splitlines()
                for j in range(max(len(exp_lines), len(act_lines))):
                    e = exp_lines[j] if j < len(exp_lines) else "(없음)"
                    a = act_lines[j] if j < len(act_lines) else "(없음)"
                    if e != a:
                        self.result_display.appendPlainText(f"[Line {j+1}]\n기대: {e}\n실제: {a}")
                self.result_display.appendPlainText("-" * 40)

        self.result_display.appendPlainText(f"\n총 {total}개 중 {passed}개 정답")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JudgeApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
