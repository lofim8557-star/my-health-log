# 🩺 마이 헬스 LOG API

> 개인의 매일 건강 수치(체중, 혈압, 혈당)를 기록하고, 자동 계산된 BMI 및 건강 위험 경고와 기간별 통계를 제공하는 RESTful API 서비스입니다.

---

## 📌 주요 기능
- **건강 데이터 관리**: 기록 등록, 조회, 수정, 삭제 (CRUD)
- **자동 계산 & 분류**:
  - BMI 자동 계산 및 4단계 분류 (저체중, 정상, 과체중, 비만)
  - 혈압/혈당 상태 분류 및 위험군(고혈압, 당뇨 의심 등) 경고 메시지 생성
- **검색 및 통계**:
  - 날짜 범위 지정 검색 (`/search`)
  - 전체 평균 체중, 혈당, 혈압 통계 제공 (`/stats`)
- **데이터 저장**: JSON 파일 연동으로 서버 재시작 후에도 데이터 유지
- **도커 지원**: Docker 컨테이너 기반 실행 지원

---

## 🛠 기술 스택
- **Language**: Python 3.10
- **Framework**: FastAPI
- **Data Validation**: Pydantic
- **Container**: Docker

---

## 🚀 실행 방법

### 1. 로컬 환경 실행
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
uvicorn main:app --reload