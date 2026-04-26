# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-04-24 22:18 | **비용**: $0.0046

**요약**: Claude Agent SDK를 활용한 분류 재판정 및 자동 PR 생성 엔진

## 코드 초안
```python
import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

def classify_and_fix(item_text: str) -> dict:
    """분류 재판정 + auto_fix PR 생성"""
    
    # Step 1: Claude Agent로 분류 재판정
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=[
            {
                "name": "classify_item",
                "description": "TODO 항목 분류 및 수정 제안",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "classification": {"type": "string", "enum": ["code_draft", "research_note", "user_only", "skip"]},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "fix_needed": {"type": "boolean"},
                        "fix_description": {"type": "string"}
                    },
                    "required": ["classification", "confidence"]
                }
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"다음 항목을 분류하고 개선사항을 제안하세요: {item_text}"
            }
        ]
    )
    
    # Tool call 처리
    tool_result = None
    for block in response.content:
        if block.type == "tool_use":
            tool_result = block.input
    
    # Step 2: auto_fix 필요시 PR 자동 생성
    pr_data = None
    if tool_result and tool_result.get("fix_needed"):
        pr_data = {
            "title": f"[Auto-Fix] {item_text[:50]}",
            "description": tool_result.get("fix_description", ""),
            "branch": f"auto-fix/{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "labels": ["tax", "auto-generated"]
        }
    
    return {
        "classification": tool_result.get("classification") if tool_result else "skip",
        "confidence": tool_result.get("confidence", 0) if tool_result else 0,
        "pr_generated": pr_data is not None,
        "pr": pr_data
    }

# 사용 예
result = classify_and_fix("세금 계산 로직 검증")
print(json.dumps(result, indent=2, ensure_ascii=False))
```

