# -*- coding: utf-8 -*-
"""
04_export_excel.py
수집·계산 결과를 하나의 엑셀 파일로 보기 좋게 정리
시트 구성:
  1) AI지수      - 기업×연도 광의/협의 지수
  2) 요약통계    - 연도별 평균 지수
  3) 수집현황    - 다운로드 성공/실패 요약
출력: data/AI도입강도_결과.xlsx
"""

import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import config


def _style_header(ws):
    """헤더 행 서식(진한 파랑 배경 + 흰 글씨 + 가운데 정렬)."""
    fill = PatternFill("solid", fgColor="2F5496")
    font = Font(color="FFFFFF", bold=True, name="맑은 고딕")
    thin = Side(style="thin", color="D0D0D0")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for cell in ws[1]:
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border
    ws.freeze_panes = "A2"   # 헤더 고정


def _autofit(ws, df):
    for i, col in enumerate(df.columns, start=1):
        width = max(len(str(col)), df[col].astype(str).map(len).max() if len(df) else 0)
        ws.column_dimensions[get_column_letter(i)].width = min(max(width + 3, 10), 40)


def export():
    ai = pd.read_csv(config.AI_INDEX_CSV, dtype={"종목코드": str})

    # 시트2: 연도별 평균
    summary = (ai.groupby("연도")[["광의지수", "협의지수"]]
                 .mean().round(3).reset_index())

    # 시트3: 수집현황
    n_ok = len(list(config.RAW_DIR.glob("*.txt")))
    if config.FAIL_LOG.exists():
        fails = pd.read_csv(config.FAIL_LOG)
        fail_summary = fails["사유"].value_counts().reset_index()
        fail_summary.columns = ["실패사유", "건수"]
    else:
        fail_summary = pd.DataFrame({"실패사유": ["없음"], "건수": [0]})
    status = pd.DataFrame({"항목": ["다운로드 성공(원문 캐시)", "지수 계산 완료 행"],
                           "값": [n_ok, len(ai)]})

    with pd.ExcelWriter(config.EXCEL_OUT, engine="openpyxl") as xw:
        ai.to_excel(xw, sheet_name="AI지수", index=False)
        summary.to_excel(xw, sheet_name="연도별요약", index=False)
        status.to_excel(xw, sheet_name="수집현황", index=False, startrow=0)
        fail_summary.to_excel(xw, sheet_name="수집현황", index=False, startrow=len(status)+3)

        wb = xw.book
        _style_header(wb["AI지수"]);      _autofit(wb["AI지수"], ai)
        _style_header(wb["연도별요약"]);  _autofit(wb["연도별요약"], summary)

    print(f"완료: 엑셀 리포트 → {config.EXCEL_OUT}")


if __name__ == "__main__":
    export()
