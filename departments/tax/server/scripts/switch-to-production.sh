#!/bin/bash
# CODEF 정식 승인 후 production 전환 스크립트
# Usage: bash switch-to-production.sh <NEW_CLIENT_ID> <NEW_CLIENT_SECRET>
#
# CODEF 영업팀에서 정식 client_id/secret 발급받으면:
#   bash switch-to-production.sh abc123... xyz456...
# 한 줄 실행으로 Vercel 환경변수 교체 + CODEF_ENV=production + 재배포 자동.

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: bash switch-to-production.sh <NEW_CLIENT_ID> <NEW_CLIENT_SECRET>"
  echo ""
  echo "CODEF 정식 승인 메일 받은 후 발급받은 키 2개를 인자로 전달하세요."
  exit 1
fi

NEW_ID="$1"
NEW_SECRET="$2"

cd "$(dirname "$0")/.."

echo "[1/4] 기존 CODEF 환경변수 삭제"
npx vercel env rm CODEF_CLIENT_ID production -y 2>/dev/null || true
npx vercel env rm CODEF_CLIENT_SECRET production -y 2>/dev/null || true
npx vercel env rm CODEF_ENV production -y 2>/dev/null || true

echo ""
echo "[2/4] 정식 CODEF 키 등록"
printf "%s" "$NEW_ID" | npx vercel env add CODEF_CLIENT_ID production
printf "%s" "$NEW_SECRET" | npx vercel env add CODEF_CLIENT_SECRET production
printf "production" | npx vercel env add CODEF_ENV production

echo ""
echo "[3/4] Vercel 재배포 (production)"
npx vercel --prod --yes

echo ""
echo "[4/4] 로컬 .secrets 백업 업데이트"
SECRETS_FILE="../../.secrets"
if [ -f "$SECRETS_FILE" ]; then
  sed -i "s|^CODEF_CLIENT_ID=.*$|CODEF_CLIENT_ID=$NEW_ID|" "$SECRETS_FILE"
  sed -i "s|^CODEF_CLIENT_SECRET=.*$|CODEF_CLIENT_SECRET=$NEW_SECRET|" "$SECRETS_FILE"
  echo "CODEF_ENV=production" >> "$SECRETS_FILE"
  echo "  → .secrets 업데이트 완료"
fi

echo ""
echo "=========================================="
echo "✅ production 전환 완료"
echo "=========================================="
echo ""
echo "테스트:"
echo "curl -X POST https://tax-n-benefit-api.vercel.app/api/connect \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"identity\":\"8601011234567\",\"userName\":\"홍길동\",\"phone\":\"01012345678\",\"loginTypeLevel\":\"1\"}'"
