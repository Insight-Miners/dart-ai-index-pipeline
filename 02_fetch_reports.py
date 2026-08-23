# -*- coding: utf-8 -*-
"""
02_fetch_reports.py
각 (기업, 연도)의 사업보고서 원문을 다운로드함
※ DART는 전문 키워드 검색을 지원하지 않으므로 rcept_no로 원문을 통째로 받아 로컬 저장
핵심: (1) 캐싱(이미 받은 건 건너뜀), (2) 실패·누락 로그, (3) 최종본(정정 최신) 기준
출력: data/raw_reports/{종목코드}_{연도}.txt , data/fetch_failures.csv
"""

import time
import pandas as pd
import OpenDartReader
import config


def get_business_report_rcept(dart, corp_code, year):
    """
    해당 연도 사업보고서(정기보고서 kind='A')의 접수번호를 찾음
    사업보고서는 보통 다음해 3월 제출 → 조회구간을 넉넉히 잡음
    정정본이 있으면 최신(rcept_no 최대) 건을 최종본으로 선택
    """
    start = f"{year+1}0101"
    end = f"{year+1}0630"
    lst = dart.list(corp=corp_code, start=start, end=end, kind="A", final=True)
    if lst is None or len(lst) == 0:
        return None
    # 보고서명에 '사업보고서' 포함되고 대상 사업연도가 맞는 건만
    mask = lst["report_nm"].str.contains("사업보고서", na=False)
    cand = lst[mask]
    if len(cand) == 0:
        return None
    # 접수일자 최신(정정 최종본) 기준
    cand = cand.sort_values("rcept_no", ascending=False)
    return cand.iloc[0]["rcept_no"]


def fetch_all():
    api_key = config.load_dart_api_key()
    dart = OpenDartReader(api_key)

    universe = pd.read_csv(config.UNIVERSE_CSV, dtype={"종목코드": str})
    universe["종목코드"] = universe["종목코드"].str.zfill(6)

    failures = []
    total = len(universe)
    for i, row in universe.reset_index(drop=True).iterrows():
        code, year, name = row["종목코드"], int(row["연도"]), row["기업명"]
        out_path = config.RAW_DIR / f"{code}_{year}.txt"

        if out_path.exists():        # ── 캐싱: 이미 받은 파일은 건너뜀 ──
            continue

        try:
            rcept = get_business_report_rcept(dart, code, year)
            if rcept is None:
                failures.append({"종목코드": code, "연도": year, "기업명": name,
                                 "사유": "사업보고서 없음"})
                continue
            raw = dart.document(rcept)      # 원문(HTML/XML) 다운로드
            if not raw:
                failures.append({"종목코드": code, "연도": year, "기업명": name,
                                 "사유": "원문 비어있음", "rcept_no": rcept})
                continue
            out_path.write_text(raw, encoding="utf-8")
        except Exception as e:
            failures.append({"종목코드": code, "연도": year, "기업명": name,
                             "사유": f"{type(e).__name__}: {str(e)[:80]}"})

        if (i + 1) % 50 == 0:
            print(f"  진행 {i+1}/{total} ...")
        time.sleep(0.2)              # 일 20,000건 호출 제한 대응(호출 간 간격)

    if failures:
        pd.DataFrame(failures).to_csv(config.FAIL_LOG, index=False, encoding="utf-8-sig")
        print(f"\n실패·누락 {len(failures)}건 → {config.FAIL_LOG}")
    n_files = len(list(config.RAW_DIR.glob("*.txt")))
    print(f"완료: 원문 캐시 {n_files}개 → {config.RAW_DIR}")


if __name__ == "__main__":
    fetch_all()
