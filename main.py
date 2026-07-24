import json
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="마이 헬스 로그 API", version="1.0")

DATA_FILE = "data.json"

# --- JSON 파일 읽기 / 쓰기 함수 ---
def load_records() -> list:
    """JSON 파일에서 기록 데이터를 읽어옵니다."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_records(records: list):
    """기록 데이터를 JSON 파일에 저장합니다."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

# --- 건강 수치 계산 및 판정 로직 ---
def calculate_health_status(data: dict) -> dict:
    height_m = data["height"] / 100
    bmi = round(data["weight"] / (height_m * height_m), 1)
    
    if bmi < 18.5:
        bmi_category = "저체중"
    elif 18.5 <= bmi <= 22.9:
        bmi_category = "정상"
    elif 23.0 <= bmi <= 24.9:
        bmi_category = "과체중"
    else:
        bmi_category = "비만"

    s = data["systolic"]
    d = data["diastolic"]
    if s < 120 and d < 80:
        bp_category = "정상"
    elif s >= 140 or d >= 90:
        bp_category = "고혈압"
    else:
        bp_category = "주의"

    sugar = data["blood_sugar"]
    if sugar < 100:
        sugar_category = "정상"
    elif 100 <= sugar <= 125:
        sugar_category = "공복혈당장애"
    else:
        sugar_category = "당뇨 의심"

    warnings = []
    if bmi_category == "비만":
        warnings.append("BMI 비만 판정: 체중 관리가 필요합니다.")
    if bp_category == "고혈압":
        warnings.append("고혈압 경고: 혈압 관리에 주의하세요.")
    if sugar_category == "당뇨 의심":
        warnings.append("당뇨 의심 경고: 전문의 상담을 권장합니다.")

    result = data.copy()
    result["bmi"] = bmi
    result["bmi_category"] = bmi_category
    result["bp_category"] = bp_category
    result["sugar_category"] = sugar_category
    result["warnings"] = warnings
    return result

# --- 입력 데이터 모델 ---
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

@app.get("/")
def read_root():
    return {"message": "마이 헬스 로그 API 실행 중!"}

# POST /records - 기록 추가
@app.post("/records")
def create_record(record: RecordIn):
    records = load_records()
    processed_data = calculate_health_status(record.dict())
    
    # 새로운 고유 ID 부여
    next_id = max([r["id"] for r in records], default=0) + 1
    processed_data["id"] = next_id
    
    records.append(processed_data)
    save_records(records)
    return processed_data

# GET /records - 전체 조회
@app.get("/records")
def get_records():
    records = load_records()
    return {"total": len(records), "data": records}

# 💡 [신규] GET /search - 날짜 범위 검색
@app.get("/search")
def search_records(
    start: str = Query(..., description="시작일 (YYYY-MM-DD)"),
    end: str = Query(..., description="종료일 (YYYY-MM-DD)")
):
    records = load_records()
    filtered = [r for r in records if start <= r["date"] <= end]
    return {"start": start, "end": end, "total": len(filtered), "data": filtered}

# 💡 [신규] GET /stats - 건강 수치 통계
@app.get("/stats")
def get_stats():
    records = load_records()
    if not records:
        return {"message": "등록된 기록이 없어 통계를 제공할 수 없습니다."}

    total_count = len(records)
    avg_weight = round(sum(r["weight"] for r in records) / total_count, 1)
    avg_sugar = round(sum(r["blood_sugar"] for r in records) / total_count, 1)
    avg_systolic = round(sum(r["systolic"] for r in records) / total_count, 1)
    avg_diastolic = round(sum(r["diastolic"] for r in records) / total_count, 1)

    return {
        "total_records": total_count,
        "average_weight": avg_weight,
        "average_blood_sugar": avg_sugar,
        "average_bp": f"{avg_systolic}/{avg_diastolic}"
    }

# GET /records/{record_id} - 단건 조회
@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = load_records()
    for r in records:
        if r["id"] == record_id:
            return r
    raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")

# PUT /records/{record_id} - 수정
@app.put("/records/{record_id}")
def update_record(record_id: int, record: RecordIn):
    records = load_records()
    for i, r in enumerate(records):
        if r["id"] == record_id:
            updated_data = calculate_health_status(record.dict())
            updated_data["id"] = record_id
            records[i] = updated_data
            save_records(records)
            return updated_data
    raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")

# DELETE /records/{record_id} - 삭제
@app.delete("/records/{record_id}")
def delete_record(record_id: int):
    records = load_records()
    for i, r in enumerate(records):
        if r["id"] == record_id:
            del records[i]
            save_records(records)
            return {"message": "삭제되었습니다."}
    raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")