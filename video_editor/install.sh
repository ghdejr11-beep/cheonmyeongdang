#!/bin/bash
# 필요한 패키지 설치

echo "📦 Python 패키지 설치 중..."
pip install -r requirements.txt

# ffmpeg 설치 확인
if ! command -v ffmpeg &> /dev/null; then
    echo "🔧 ffmpeg 설치 중..."
    sudo apt-get update && sudo apt-get install -y ffmpeg
else
    echo "✅ ffmpeg 이미 설치됨"
fi

echo ""
echo "✅ 설치 완료! 아래 명령어로 실행하세요:"
echo "   python app.py"
echo ""
echo "🌐 브라우저에서 http://localhost:7860 접속"
