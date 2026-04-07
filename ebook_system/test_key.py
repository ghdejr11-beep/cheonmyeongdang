"""
API 키가 살아있는지 직접 검증하는 도구.
환경변수, 터미널 복붙 등 모든 경로를 우회한다.

사용법:
    python test_key.py

→ 화면에 "Paste your API key:" 가 나오면 키를 붙여넣고 엔터.
→ 키가 작동하면 "✅ KEY WORKS" 가 나옴.
→ 안 되면 정확한 에러 원인이 표시됨.
"""

import sys
import getpass

def main():
    print("=" * 60)
    print(" Anthropic API 키 검증 도구")
    print("=" * 60)
    print()
    print("아래에 키를 붙여넣고 엔터:")
    print("(보안 위해 입력 시 화면에 안 보입니다 — 정상)")
    print()

    try:
        key = getpass.getpass("Key: ").strip()
    except Exception:
        # getpass 안 되면 일반 input
        key = input("Key: ").strip()

    if not key:
        print("\n❌ 키가 비어있습니다.")
        return 1

    print()
    print(f"길이: {len(key)}자")
    print(f"시작: {key[:15]}...")
    print(f"끝:   ...{key[-6:]}")
    print()

    # 형식 검증
    if not key.startswith("sk-ant-api03-"):
        print(f"❌ 형식이 잘못됨: 'sk-ant-api03-' 로 시작해야 합니다.")
        if key.startswith("sk-proj-") or key.startswith("sk-"):
            print("   → 이건 OpenAI 키입니다. Anthropic 키 발급:")
            print("   → https://console.anthropic.com/settings/keys")
        return 1

    if len(key) < 50:
        print(f"⚠️  길이가 너무 짧음 ({len(key)}자). 정상은 95~110자.")
        print("   → 복사할 때 잘렸을 가능성. 다시 복사해보세요.")

    print("Anthropic 서버에 테스트 요청 중...")
    print()

    try:
        import anthropic
    except ImportError:
        print("❌ anthropic SDK 가 설치되지 않음.")
        print("   pip install anthropic 실행 후 다시 시도.")
        return 1

    try:
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=20,
            messages=[{"role": "user", "content": "Reply with one word: ping"}],
        )
        text = "".join(b.text for b in msg.content if b.type == "text")
        print("=" * 60)
        print("✅ KEY WORKS")
        print(f"   응답: {text}")
        print(f"   사용량: input={msg.usage.input_tokens} output={msg.usage.output_tokens}")
        print("=" * 60)
        print()
        print("이 키는 정상입니다. 이제 영구 저장:")
        print()
        print('  [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "<위의키>", "User")')
        print()
        print("→ PowerShell 새 창 → cd ebook_system → python generate_book.py")
        return 0

    except anthropic.AuthenticationError as e:
        print("=" * 60)
        print("❌ AUTHENTICATION FAILED (401)")
        print("=" * 60)
        print()
        print(f"에러: {e}")
        print()
        print("가능한 원인:")
        print()
        print("1. 키가 콘솔에서 삭제됐음")
        print("   → https://console.anthropic.com/settings/keys")
        print("   → 화면에 '키가 보이지 않으면' 새로 발급")
        print()
        print("2. Billing 크레딧 0")
        print("   → https://console.anthropic.com/settings/billing")
        print("   → Credit balance 가 $0 이면 Add to balance")
        print()
        print("3. 다른 organization 의 키")
        print("   → Anthropic 콘솔 좌측 상단 organization 드롭다운 확인")
        print("   → 다른 워크스페이스로 잘못 전환됐을 수 있음")
        print()
        print("4. 키 복사 시 글자 빠짐")
        print(f"   → 위에 표시된 길이 ({len(key)}자) 가 100자 미만이면 잘림")
        print("   → 콘솔에서 키 옆 📋 복사 버튼 클릭으로 다시 복사")
        return 1

    except anthropic.PermissionDeniedError as e:
        print("❌ PERMISSION DENIED (403)")
        print(f"에러: {e}")
        print()
        print("→ 키는 살아있지만 권한 부족. Billing 또는 organization 권한 확인.")
        return 1

    except Exception as e:
        print(f"❌ 다른 에러: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
