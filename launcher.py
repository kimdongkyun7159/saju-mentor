"""사주멘토 런처 — 서버 시작 + 브라우저 오픈 + 트레이 아이콘"""

import os
import sys
import shutil
import subprocess
import webbrowser
import time
import ctypes
from pathlib import Path

APP_NAME = "사주멘토"
PORT = 5031
URL = f"http://localhost:{PORT}"


def get_app_dir():
    """exe 또는 py 파일이 있는 디렉토리"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def find_python():
    """시스템 Python 경로 찾기"""
    # frozen exe에서는 sys.executable이 exe 자신이므로 직접 찾아야 함
    if not getattr(sys, 'frozen', False):
        return sys.executable
    # PATH에서 python 찾기
    python_path = shutil.which('python')
    if python_path:
        return python_path
    # 일반적인 설치 경로 확인
    for candidate in [
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Python/Python313/python.exe',
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Python/Python312/python.exe',
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Python/Python311/python.exe',
        Path('C:/Python313/python.exe'),
        Path('C:/Python312/python.exe'),
    ]:
        if candidate.exists():
            return str(candidate)
    return None


def is_port_in_use(port):
    """포트 사용 중인지 확인"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def kill_existing(port):
    """기존 서버 종료"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port} | findstr LISTENING',
            shell=True, capture_output=True, text=True
        )
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                pid = line.strip().split()[-1]
                subprocess.run(f'taskkill /F /PID {pid}', shell=True,
                               capture_output=True)
    except Exception:
        pass


def main():
    app_dir = get_app_dir()
    app_py = app_dir / "app.py"

    if not app_py.exists():
        ctypes.windll.user32.MessageBoxW(
            0, f"app.py를 찾을 수 없습니다.\n경로: {app_dir}",
            APP_NAME, 0x10
        )
        return

    python = find_python()
    if not python:
        ctypes.windll.user32.MessageBoxW(
            0, "Python을 찾을 수 없습니다.\nPython 3.11 이상을 설치해주세요.",
            APP_NAME, 0x10
        )
        return

    # 이미 실행 중이면 브라우저만 열기
    if is_port_in_use(PORT):
        webbrowser.open(URL)
        ctypes.windll.user32.MessageBoxW(
            0, f"서버가 이미 실행 중입니다.\n{URL}",
            APP_NAME, 0x40
        )
        return

    # 콘솔 창 숨기기 (exe 실행 시)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0  # SW_HIDE

    # 서버 시작
    proc = subprocess.Popen(
        [python, str(app_py)],
        cwd=str(app_dir),
        startupinfo=startupinfo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 서버 준비 대기 (최대 10초)
    for _ in range(20):
        if is_port_in_use(PORT):
            break
        if proc.poll() is not None:
            # 서버가 비정상 종료
            stderr = proc.stderr.read().decode('utf-8', errors='replace')
            ctypes.windll.user32.MessageBoxW(
                0, f"서버 시작 실패:\n{stderr[:500]}",
                APP_NAME, 0x10
            )
            return
        time.sleep(0.5)
    else:
        ctypes.windll.user32.MessageBoxW(
            0, "서버 시작 시간 초과 (10초)",
            APP_NAME, 0x10
        )
        proc.terminate()
        return

    # 브라우저 열기
    webbrowser.open(URL)

    # 종료 대기 (메시지 박스)
    ctypes.windll.user32.MessageBoxW(
        0,
        f"🔮 {APP_NAME} 실행 중!\n\n"
        f"주소: {URL}\n\n"
        f"[확인]을 누르면 서버가 종료됩니다.",
        APP_NAME,
        0x40  # MB_ICONINFORMATION
    )

    # 서버 종료
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    # 혹시 남은 프로세스 정리
    kill_existing(PORT)


if __name__ == '__main__':
    main()
