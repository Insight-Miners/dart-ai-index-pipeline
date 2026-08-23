# -*- coding: utf-8 -*-
"""
03_build_ai_index.py
저장된 사업보고서 원문에서 광의·협의 AI 도입강도 지수를 계산함
지수 계산 로직은 ai_index_core.py 에 있으며 단독 검증이 끝남
출력: data/ai_index.csv (컬럼: 종목코드, 연도, 광의지수, 협의지수, 총토큰수)
"""

import pandas as pd
import config
from ai_index_core import compute_indices


def build_index():
    rows = []
    files = sorted(config.RAW_DIR.glob("*.txt"))
    print(f"원문 {len(files)}개 처리 시작...")

    for i, fp in enumerate(files):
        # 파일명 규칙: {종목코드}_{연도}.txt
        stem = fp.stem
        try:
            code, year = stem.split("_")
            year = int(year)
        except ValueError:
            print(f"  ! 파일명 형식 오류, 건너뜀: {fp.name}")
            continue

        raw = fp.read_text(encoding="utf-8", errors="ignore")
        broad, narrow, total = compute_indices(
            raw, window=config.COOCCURRENCE_WINDOW
        )
        rows.append({"종목코드": code, "연도": year,
                     "광의지수": broad, "협의지수": narrow, "총토큰수": total})

        if (i + 1) % 100 == 0:
            print(f"  진행 {i+1}/{len(files)} ...")

    df = pd.DataFrame(rows).sort_values(["종목코드", "연도"])
    df.to_csv(config.AI_INDEX_CSV, index=False, encoding="utf-8-sig")
    print(f"\n완료: {len(df)}행 → {config.AI_INDEX_CSV}")
    print("\n[요약 통계]")
    print(df[["광의지수", "협의지수", "총토큰수"]].describe().round(2))
    return df


if __name__ == "__main__":
    build_index()
