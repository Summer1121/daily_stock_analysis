# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from typing import List

from storage import get_db, DatabaseManager, AnalysisRecord

router = APIRouter()


@router.get("/analysis/{stock_code}", response_model=List[dict])
def get_analysis_history(stock_code: str, db: DatabaseManager = Depends(get_db)):
    """Get historical analysis records for a stock"""
    records = db.get_analysis_records(stock_code)
    return [record.to_dict() for record in records]
