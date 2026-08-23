# -*- coding: utf-8 -*-
"""
ai_index_core.py
AI 도입강도 지수 계산의 핵심 로직 (네트워크 불필요, 단독 검증 가능).
- 광의 지수(Broad): AI 명사 사전 총 빈도 / 총 토큰 × 10,000
- 협의 지수(Narrow): AI 명사가 ±N토큰 윈도우 안에서 실질 동사와 공출현한 경우만 카운트
"""

import re

# ── 키워드 사전 ────────────────────────────────────────────────
AI_NOUNS = [
    "인공지능", "AI", "머신러닝", "기계학습", "딥러닝", "심층학습",
    "생성형AI", "생성형 인공지능", "LLM", "대규모언어모델", "자연어처리", "NLP",
    "컴퓨터비전", "챗봇", "AI챗봇", "보이스봇", "AICC", "AI컨택센터",
    "RPA", "예측모형", "추천시스템", "이상탐지", "알고리즘 트레이딩",
]
ACTION_VERBS = [
    "도입", "구축", "적용", "개발", "출시", "운영",
    "고도화", "확대", "투자", "자동화", "전환", "상용화",
]


def clean_text(raw: str) -> str:
    """HTML/XML 태그 제거 → 순수 텍스트."""
    text = re.sub(r"<[^>]+>", " ", raw)        # 태그 제거
    text = re.sub(r"&[a-zA-Z]+;", " ", text)   # HTML 엔티티 제거
    text = re.sub(r"\s+", " ", text)           # 공백 정규화
    return text.strip()


def tokenize(text: str):
    """간이 토큰화: 한글/영문/숫자 덩어리 기준. (정규식 기반, 형태소분석 대체)"""
    return re.findall(r"[가-힣A-Za-z0-9]+", text)


def _compile_noun_pattern(nouns):
    """긴 키워드부터 매칭되도록 정렬 후 정규식 컴파일. 'AI'는 대소문자·경계 주의."""
    ordered = sorted(nouns, key=len, reverse=True)
    parts = []
    for n in ordered:
        esc = re.escape(n)
        if re.fullmatch(r"[A-Za-z]+", n):
            # 영문 약어(AI, LLM, NLP 등): 앞뒤가 영문자가 아닌 경우만 (AI를/AI가 는 잡되 AID 는 제외)
            parts.append(rf"(?<![A-Za-z]){esc}(?![A-Za-z])")
        else:
            parts.append(esc)
    return re.compile("|".join(parts), re.IGNORECASE)


NOUN_RE = _compile_noun_pattern(AI_NOUNS)


def count_broad(text: str):
    """광의: AI 명사 총 출현 횟수."""
    return len(NOUN_RE.findall(text))


def count_narrow(tokens, window: int = 20):
    """
    협의: AI 명사 토큰 기준 ±window 토큰 안에 실질 동사가 있으면 1건 카운트.
    tokens: tokenize() 결과 리스트.
    """
    verb_set = set(ACTION_VERBS)
    # 각 토큰이 AI 명사를 포함하는지 판정.
    # search()를 써서 조사 결합("AI를", "AI챗봇") 및 복합어를 잡되,
    # NOUN_RE의 경계 조건이 'AID'/'AIDS' 같은 오탐은 그대로 배제한다.
    def is_ai_noun(tok):
        return bool(NOUN_RE.search(tok))
    # 동사 포함 여부 (동사는 조사 결합 대비 startswith 허용: 도입/도입했다/도입하여)
    def has_verb(tok):
        return any(tok.startswith(v) for v in verb_set)

    n = len(tokens)
    narrow_hits = 0
    for i, tok in enumerate(tokens):
        if is_ai_noun(tok):
            lo, hi = max(0, i - window), min(n, i + window + 1)
            if any(has_verb(tokens[j]) for j in range(lo, hi) if j != i):
                narrow_hits += 1
    return narrow_hits


def compute_indices(raw_report: str, window: int = 20):
    """
    보고서 원문(raw) → (광의지수, 협의지수, 총토큰수) 반환. 만분율 정규화.
    """
    text = clean_text(raw_report)
    tokens = tokenize(text)
    total = len(tokens)
    if total == 0:
        return 0.0, 0.0, 0
    broad_cnt = count_broad(text)
    narrow_cnt = count_narrow(tokens, window=window)
    broad_idx = broad_cnt / total * 10000
    narrow_idx = narrow_cnt / total * 10000
    return round(broad_idx, 4), round(narrow_idx, 4), total
