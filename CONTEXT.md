# 프로젝트 컨텍스트

## 사용자 환경
- OS: Windows 10
- Python: 설치됨

## 프로젝트 구조
- `/home/user/cheonmyeongdang/` - 메인 프로젝트
- `/home/user/cheonmyeongdang/video_editor/` - Gradio 기반 영상 자동 편집기
  - `app.py` - 메인 앱 (Whisper 자막, BGM 추가, 하이라이트 추출)
  - `requirements.txt` - 의존성
  - `install.sh` - 설치 스크립트

## 완료된 작업
- video_editor 앱 GitHub에 커밋 및 푸시
- 서버 의존성 설치 완료 (pip install -r requirements.txt)

## 현재 이슈
- 앱이 Linux 서버에서 실행되므로 사용자의 Windows localhost:7860으로 접근 불가
- 해결 방법: 사용자 Windows에서 직접 실행 필요

## 다음 세션에서 할 작업
- 사용자 Windows에서 앱 실행 지원
  1. `git clone https://github.com/ghdejr11-beep/cheonmyeongdang.git`
  2. `cd cheonmyeongdang\video_editor`
  3. `pip install -r requirements.txt`
  4. `python app.py`
  5. 브라우저에서 `http://localhost:7860` 접속

## Git 브랜치
- 작업 브랜치: `claude/configure-repo-storage-YNoJp`
