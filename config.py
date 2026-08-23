# -*- coding: utf-8 -*-
"""
config.py
전역 설정: API 키, 분석 대상 연도, 경로, 키워드 사전.
"""

import os
from pathlib import Path

# ── API 키 로드 (하드코딩 금지) ────────────────────────────────
def load_dart_api_key() -> str:
    key = os.environ.get("DART_API_KEY")
    if key:
        return key.strip()
    secret = Path(__file__).parent / "secret.txt"
    if secret.exists():
        return secret.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "DART API 키가 없습니다. 환경변수 DART_API_KEY를 설정하거나 "
        "secret.txt 파일에 키를 저장하세요. (secret.txt는 .gitignore에 추가)"
    )

# ── 분석 대상 연도 ─────────────────────────────────────────────
START_YEAR = 2015
END_YEAR = 2025
YEARS = list(range(START_YEAR, END_YEAR + 1))

# ── 경로 ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw_reports"       # 다운로드 원문 캐시
UNIVERSE_CSV = DATA_DIR / "universe.csv"
AI_INDEX_CSV = DATA_DIR / "ai_index.csv"
FINANCIALS_CSV = DATA_DIR / "financials.csv"
PANEL_CSV = DATA_DIR / "panel.csv"
FAIL_LOG = DATA_DIR / "fetch_failures.csv"
EXCEL_OUT = DATA_DIR / "AI도입강도_결과.xlsx"

for d in (DATA_DIR, RAW_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── 지수 계산 파라미터 ────────────────────────────────────────
COOCCURRENCE_WINDOW = 20   # 협의 지수 공출현 윈도우 (±토큰)
NORMALIZE_PER = 10000      # 만분율 정규화

# ── KOSPI200 지수 코드 (pykrx) ────────────────────────────────
KOSPI200_INDEX = "1028"

# ── 키워드 사전 ───────────────────────────────────────────────
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
