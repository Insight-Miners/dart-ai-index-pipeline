# DART 사업보고서 기반 AI 도입강도 지수 구축 파이프라인

> **"사업보고서 텍스트마이닝을 활용한 AI 도입강도 측정과 기업 재무성과 분석"**  
> *2026 성균관대학교 응용AI융합학부 학술경진대회 출품작*

본 프로젝트는 금융감독원 DART(전자공시시스템)의 사업보고서 원문을 수집·파싱하여 기업별·연도별 **'AI 도입강도 지수(AI Adoption Intensity Index)'** 를 구축하고, 그 결과를 분석용 데이터셋 및 엑셀 리포트로 자동 생성하는 엔드투엔드 데이터 파이프라인입니다.

---

## 📌 주요 특징 (Key Features)

1. **원문 기반 자체 변수 구축 (Data Sovereignty)**  
   - 외부 가공 변수를 구입하는 대신, DART 사업보고서 원문 HTML/XML을 직접 다운로드하고 파싱하여 지수를 직접 생성했습니다.
2. **홍보성 언론 노이즈 필터링 (Broad vs. Narrow Index)**  
   - 단순 AI 키워드 빈도를 측정하는 **광의 지수(Broad Index)** 와, AI 키워드가 실질 동작 동사(도입, 구축, 운영 등)와 ±20토큰 내에 공출현하는 **협의 지수(Narrow Index)** 를 분리 산출하여 단순 홍보성 언급을 엄격히 차단했습니다.
3. **생존편향(Survivorship Bias) 방지**  
   - 매년 변경되는 KOSPI200 및 KOSDAQ 상위 구성종목의 연도별 스냅샷을 수집하여 시점간 생존편향을 방지했습니다.
4. **로컬 캐싱 & 정정 최신본 반영**  
   - DART API의 전문 검색 미지원 제약을 극복하기 위해 `rcept_no` 기반 원문 수집 알고리즘을 구현했으며, Caching/Fail-log 및 정정보고서 발생 시 최신 공시 자동선택 로직을 탑재했습니다.

---

## 🏗️ 파이프라인 구조 (Repository Structure)

```text
dart-ai-index-pipeline/
├── .gitignore            # Git 추적 제외 설정 (비밀키, 데이터 파일 등)
├── README.md             # 프로젝트 안내 문서
├── requirements.txt      # 의존성 라이브러리 목록
├── secret.txt            # DART API(직접 생성 필요)
├── config.py             # [Core] 전역 설정 (API Key, 연도, 경로, 키워드 사전)
├── ai_index_core.py      # [Core] 광의/협의 지수 계산 핵심 모듈
├── 01_build_universe.py  # [Step 1] 연도별 분석 대상 기업 Universe 구축 (KOSPI200+KOSDAQ)
├── 02_fetch_reports.py   # [Step 2] DART 사업보고서 원문 다운로드 (캐싱 & 실패로그)
├── 03_build_ai_index.py  # [Step 3] 원문 텍스트마이닝 및 지수 일괄 계산
├── 04_export_excel.py    # [Step 4] 엑셀 리포트(다중 시트 + 헤더 서식) 자동 생성
└── data/                 # 데이터 저장 디렉토리 (Git 미추적, 실행 시 자동 생성)
    ├── raw_reports/      # 다운로드된 원문 텍스트 캐시 (*.txt), 실행 시 자동 생성
    ├── universe.csv      # 수집 대상 기업 리스트, 실행 시 자동 생성
    ├── ai_index.csv      # 계산된 기업-연도별 AI 지수, 실행 시 자동 생성
    ├── fetch_failures.csv# 수집 실패 로그, 실행 시 자동 생성
    └── AI도입강도_결과.xlsx # 최종 엑셀 리포트, 실행 시 자동 생성
```

---

## 🛠️ 모듈별 역할 및 설명

| 모듈 파일명 | 역할 | 핵심 포인트 |
| :--- | :--- | :--- |
| `config.py` | 전역 설정 관리 | API 키 보안 로드(환경변수/`secret.txt`), 경로, 키워드 사전(명사 23종, 동사 12종) 통합 관리 |
| `01_build_universe.py` | 대상 기업 구축 | `pykrx`를 통해 매년 말 기준 KOSPI200 + KOSDAQ 대표종목 스냅샷 수집 (생존편향 방지) |
| `02_fetch_reports.py` | 원문 다운로드 | `OpenDartReader` 기반 사업보고서(`kind='A'`) 수집, 최신 정정본 자동 선택, 로컬 캐싱 |
| `ai_index_core.py` | 지수 계산 로직 | 정규식을 통한 오탐 방지(`AID`/`AIDS` 배제), ±20 토큰 공출현 윈도우 계산, 만분율 정규화 |
| `03_build_ai_index.py` | 지수 일괄 산출 | `data/raw_reports/` 내 원문 파일 배치 처리 후 `ai_index.csv` 생성 |
| `04_export_excel.py` | 엑셀 리포팅 | `openpyxl` 서식 적용 (다중 시트, 헤더 고정, 열 너비 자동 맞춤, 파랑 헤더 서식) |

---

## ⚙️ 사전 준비 및 설치 (Installation)

### 1. Repository 클론 및 라이브러리 설치
```bash
git clone https://github.com/Insight-Miners/dart-ai-index-pipeline.git
cd dart-ai-index-pipeline
pip install -r requirements.txt
```

### 2. DART API Key 설정 (보안)
OpenDART([https://opendart.fss.or.kr](https://opendart.fss.or.kr))에서 인증키를 무료 발급받은 후, **다음 두 가지 방법 중 하나**로 설정합니다.

- **방법 A: 환경변수 설정 (권장)**
  ```bash
  export DART_API_KEY="your_opendart_api_key_here"
  ```
- **방법 B: `secret.txt` 파일 생성**
  프로젝트 루트 디렉토리에 `secret.txt` 파일을 만들어 발급받은 API 키를 텍스트로 저장합니다. (`.gitignore`에 등록되어 있어 Git에 커밋되지 않습니다.)

  `secret.txt` 예시: 
  ```text
  YOUR_DART_API_KEY_HERE    # 따옴표 등 없이 API KEY만 기재
  ```

---

## 🚀 실행 순서 (Usage)

파이프라인은 아래의 순서대로 순차 실행합니다.

```bash
# 1) 연도별 분석 대상 기업 Universe 구축 (data/universe.csv)
python 01_build_universe.py

# 2) DART 사업보고서 원문 다운로드 (data/raw_reports/*.txt)
python 02_fetch_reports.py

# 3) AI 도입강도 지수(광의/협의) 산출 (data/ai_index.csv)
python 03_build_ai_index.py

# 4) 최종 엑셀 리포트 생성 (data/AI도입강도_결과.xlsx)
python 04_export_excel.py
```

---

## 🔬 핵심 계산 로직 및 검증 (Methodology & Validation)

### 지수 산출식
- **광의 지수 (Broad Index)**: $\left( \frac{\text{AI 명사 키워드 총 빈도}}{\text{문서 총 토큰 수}} \right) \times 10,000$ (만분율)
- **협의 지수 (Narrow Index)**: $\left( \frac{\text{±20 토큰 내 실질 동사 공출현 AI 명사 빈도}}{\text{문서 총 토큰 수}} \right) \times 10,000$ (만분율)

### 로직 검증 결과
합성 사업보고서 데이터를 통해 3가지 패턴(실질 도입형, 홍보 언급형, 무관형)에 대한 로직 검증을 수행하였습니다.

| 보고서 유형 | 내용 특징 | 광의 지수 | 협의 지수 | 해석 및 의의 |
| :--- | :--- | :---: | :---: | :--- |
| **실질 도입형** | AI 챗봇 개발·도입, ML 이상탐지 구축·운영 | **3,500** | **3,500** | 실질적 도입 활동이 존재하여 두 지수 모두 높음 |
| **홍보 언급형** | "AI는 미래 핵심기술" 式 나열 및 단순 언급 | **4,545** | **0** | 광의 지수는 최고치나, 협의 지수는 0으로 **홍보성 언급 완벽 차단** |
| **무관형** | AI 관련 내용 미언급 | **0** | **0** | 모두 0으로 정상 산출 |

> **💡 학술적/실무적 의의:**  
> "단순 키워드 빈도 측정 시 기업의 홍보성 언급이 교란 요인으로 작용한다"는 한계를 협의 지수를 통해 성공적으로 방어하였습니다. 또한, 정규화를 통해 `AID`, `AIDS` 등 영문 오탐을 배제하고 `AI를`, `AI챗봇` 등 한국어 조사/복합어 결합을 정상 포착하도록 정교화했습니다.

---

## 📊 실증분석 및 통계 검증 결과 (Empirical Analysis Results)

본 저장소는 AI 도입강도 지수를 구축하는 데이터 전처리 파이프라인(Step 1~4)과 함께, 본 연구의 **최종 분석 결과물**을 참고 자료로 공개하고 있습니다. 

분석에 활용된 재무 데이터 결합 및 패널 고정효과 모형(PanelOLS)의 통계적 산출 결과는 아래 경로의 엑셀 파일에서 확인하실 수 있습니다.

- **파일 위치:** `results/최종 분석 결과물.xlsx`
- **주요 포함 내용:**
  1. **주회귀분석 및 강건성 검정 (H1, H2):** 기업 및 연도 양방향 고정효과(Two-way Fixed Effects)를 통제하고 기업 단위 클러스터링(Cluster-robust SE)을 적용한 수익성(ROA, ROE, OPM) 회귀분석 결과 및 1SD(표준편차) 효과 크기
  2. **조절효과 분석 (H3):** 기업 규모(Size) 및 IT 집약도(IT Intensive)에 따른 교호작용(Interaction) 검증 결과
  3. **지수 타당도 검증 (Validity):** 무작위 추출 30개사 대상 수작업 라벨링(1~5점) 기반 정성평가 결과와 본 파이프라인 산출 지수 간의 상관관계(Pearson/Spearman) 분석
  4. **기술통계 및 연도별 추이:** 모델에 투입된 전체 통제변수의 기초 통계량 및 KOSPI/KOSDAQ 기업의 연도별 AI 언급 비중 변화 추이

---

## 📜 라이선스 (License)

본 프로젝트는 [MIT License](LICENSE)에 따라 자유롭게 이용, 수정 및 배포할 수 있습니다.

---

### 👥 참가 팀원
- **고명원**
- **김예빈**
- **박주희**

