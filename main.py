from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="마이 헬스 로그 API", version="1.0")

records = []

# 입력받을 데이터 모델
class RecordIn(BaseModel):
    date: str
    weight: float
    height: float
    systolic: int
    diastolic: int
    blood_sugar: int
    steps: int = 0
    sleep_hours: float = 0.0
    memo: str = ""

# 💡 [핵심] 건강 수치 자동 계산 및 분류 함수
def calculate_health_status(data: dict) -> dict:
    # 1. BMI 계산 (키 cm -> m 변환)
    height_m = data["height"] / 100
    bmi = round(data["weight"] / (height_m * height_m), 1)
    
    # BMI 분류
    if bmi < 18.5:
        bmi_category = "저체중"
    elif 18.5 <= bmi <= 22.9:
        bmi_category = "정상"
    elif 23.0 <= bmi <= 24.9:
        bmi_category = "과체중"
    else:
        bmi_category = "비만"

    # 2. 혈압 분류
    s = data["systolic"]
    d = data["diastolic"]
    if s < 120 and d < 80:
        bp_category = "정상"
    elif s >= 140 or d >= 90:
        bp_category = "고혈압"
    else:
        bp_category = "주의"

    # 3. 공복 혈당 분류
    sugar = data["blood_sugar"]
    if sugar < 100:
        sugar_category = "정상"
    elif 100 <= sugar <= 125:
        sugar_category = "공복혈당장애"
    else:
        sugar_category = "당뇨 의심"

    # 4. 경고(warnings) 목록 생성
    warnings = []
    if bmi_category == "비만":
        warnings.append("BMI 비만 판정: 체중 관리가 필요합니다.")
    if bp_category == "고혈압":
        warnings.append("고혈압 경고: 혈압 관리에 주의하세요.")
    if sugar_category == "당뇨 의심":
        warnings.append("당뇨 의심 경고: 전문의 상담을 권장합니다.")

    # 계산된 결과 추가
    result = data.copy()
    result["bmi"] = bmi
    result["bmi_category"] = bmi_category
    result["bp_category"] = bp_category
    result["sugar_category"] = sugar_category
    result["warnings"] = warnings
    
    return result

@app.get("/")
def read_root():
    return {"message": "마이 헬스 로그 API 실행 중!"}

# POST /records - 기록 추가 (계산 로직 포함)
@app.post("/records")
def create_record(record: RecordIn):
    raw_data = record.dict()
    processed_data = calculate_health_status(raw_data)
    processed_data["id"] = len(records) + 1
    records.append(processed_data)
    return processed_data

# GET /records - 전체 조회
@app.get("/records")
def get_records():
    return {"total": len(records), "data": records}

# GET /records/{record_id} - 단건 조회
@app.get("/records/{record_id}")
def get_record(record_id: int):
    for r in records:
        if r["id"] == record_id:
            return r
    raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")

# 💡 [신규] PUT /records/{record_id} - 기록 수정
@app.put("/records/{record_id}")
def update_record(record_id: int, record: RecordIn):
    for i, r in enumerate(records):
        if r["id"] == record_id:
            updated_data = calculate_health_status(record.dict())
            updated_data["id"] = record_id
            records[i] = updated_data
            return updated_data
    raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")

# DELETE /records/{record_id} - 삭제
@app.delete("/records/{record_id}")
def delete_record(record_id: int):
    for i, r in enumerate(records):
        if r["id"] == record_id:
            del records[i]
            return {"message": "삭제되었습니다."}
    raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")