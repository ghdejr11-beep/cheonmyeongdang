# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-04-25 21:00 | **비용**: $0.0032

**요약**: Claude Agent SDK를 사용해 분류 재판정 및 PR 자동 생성 로직

## 코드 초안
```python
import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

def classify_and_fix(item: dict) -> dict:
    """분류 재판정 후 자동 PR 생성"""
    prompt = f"""다음 항목을 세금 관련 분류로 재판정하세요:
{json.dumps(item, ensure_ascii=False, indent=2)}

응답 형식: {"category": "...", "severity": "high/medium/low", "fix_needed": true/false}"""
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    result = json.loads(response.content[0].text)
    
    if result.get("fix_needed"):
        pr_title = f"[TAX] {result['category']} - Auto-fix {datetime.now().strftime('%Y%m%d')}"
        pr_body = f"""자동 분류 재판정 결과:
- 분류: {result['category']}
- 심각도: {result['severity']}
- 원본: {item.get('id', 'unknown')}"""
        result["pr"] = {"title": pr_title, "body": pr_body, "branch": f"tax/auto-fix-{datetime.now().timestamp()}"}
    
    return result

# 사용 예시
test_item = {"id": "TAX-001", "type": "deduction", "amount": 50000}
print(json.dumps(classify_and_fix(test_item), ensure_ascii=False, indent=2))
```

