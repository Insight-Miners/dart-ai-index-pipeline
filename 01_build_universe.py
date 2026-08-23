# -*- coding: utf-8 -*-
"""
01_build_universe.py
분석 대상 기업 리스트(KOSPI200 + KOSDAQ 대표종목)를 연도별로 구축
※ 구성종목은 매년 바뀌므로 연도별로 각각 스냅샷을 받음(생존편향 방지).
출력: data/universe.csv  (컬럼: 연도, 종목코드, 기업명, 시장)
"""

import time
import pandas as pd
from pykrx import stock
import config


def year_end_date(year: int) -> str:
    """해당 연도 마지막 영업일(근사) — 12/29 기준, 없으면 직전 영업일로 대체됨."""
    return f"{year}1229"


def get_kospi200(date: str):
    """KOSPI200 구성종목 코드 리스트."""
    return stock.get_index_portfolio_deposit_file(config.KOSPI200_INDEX, date=date)


def get_kosdaq_top(date: str, top_n: int = 200):
    """KOSDAQ 시가총액 상위 종목(대표종목 대용). Premier 세그먼트 미제공 시 대체."""
    cap = stock.get_market_cap_by_ticker(date, market="KOSDAQ")
    cap = cap.sort_values("시가총액", ascending=False).head(top_n)
    return list(cap.index)


def build_universe():
    rows = []
    for year in config.YEARS:
        date = year_end_date(year)
        print(f"[{year}] 구성종목 수집 중... ({date})")
        try:
            kospi = get_kospi200(date)
            for code in kospi:
                rows.append({"연도": year, "종목코드": code,
                             "기업명": stock.get_market_ticker_name(code),
                             "시장": "KOSPI200"})
        except Exception as e:
            print(f"  ! KOSPI200 실패: {e}")
        try:
            kosdaq = get_kosdaq_top(date)
            for code in kosdaq:
                rows.append({"연도": year, "종목코드": code,
                             "기업명": stock.get_market_ticker_name(code),
                             "시장": "KOSDAQ"})
        except Exception as e:
            print(f"  ! KOSDAQ 실패: {e}")
        time.sleep(0.5)   # KRX 서버 부하 완화

    df = pd.DataFrame(rows).drop_duplicates(subset=["연도", "종목코드"])
    df.to_csv(config.UNIVERSE_CSV, index=False, encoding="utf-8-sig")
    print(f"\n완료: {len(df)}행 → {config.UNIVERSE_CSV}")
    print(df.groupby(["연도", "시장"]).size().unstack(fill_value=0))
    return df


if __name__ == "__main__":
    build_universe()
