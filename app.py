import io
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

app = FastAPI(title="Batch CSV Predictor")


def load_model(model_path: str = "model.pkl"):
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    with open(path, "rb") as f:
        return pickle.load(f)


def safe_read_csv(raw: bytes, sep: str, decimal: str) -> pd.DataFrame:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(io.BytesIO(raw), encoding=enc, sep=sep, decimal=decimal)
            return df
        except UnicodeDecodeError:
            continue
    raise HTTPException(status_code=400, detail="Could not decode CSV (try UTF-8).")

def to_csv_response(df: pd.DataFrame, filename: str) -> StreamingResponse:
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    sep: str = ",",                 
    decimal: str = ".",             
    model_path: str = "xgb_model.pkl", 
    pred_col: str = "prediction",   
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    raw = await file.read()
    df = safe_read_csv(raw, sep=sep, decimal=decimal)

    df = df.replace([np.inf, -np.inf], np.nan)

    for maybe_target in ("SalePrice", "target", "y"):
        if maybe_target in df.columns:
            df = df.drop(columns=[maybe_target])

    try:
        model = load_model(model_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {e!r}")

    try:
        preds = model.predict(df)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {e!r}. Ensure the saved object is the FULL pipeline, not just the estimator.",
        )

    out = df.copy()
    out[pred_col] = np.asarray(preds).ravel()

    stem = Path(file.filename).stem or "predictions"
    out_name = f"{stem}_predictions.csv"

    return to_csv_response(out, out_name)
