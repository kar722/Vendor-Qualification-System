from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
import traceback

from app.matching import load_and_prepare_data, filter_by_category, compute_similarity
from app.ranking import rank_vendors

app = FastAPI(
    title="Vendor Qualification System",
    description="Ranks software vendors based on feature similarity and trust metrics.",
    version="1.0"
)

DATA_PATH = "data/G2 software - CRM Category Product Overviews.csv"
df_master = load_and_prepare_data(DATA_PATH)

class VendorQuery(BaseModel):
    software_category: str
    capabilities: List[str]


@app.post("/vendor_qualification")
def vendor_qualification(query: VendorQuery):
    try:
        df_filtered = filter_by_category(df_master, query.software_category)
        if df_filtered.empty:
            valid_categories = df_master['main_category'].dropna().unique().tolist()
            raise HTTPException(
                status_code=404,
                detail=f"No vendors found in category '{query.software_category}'. "
                       f"Available categories: {valid_categories}"
            )

        df_similar = compute_similarity(df_filtered, query.capabilities)
        if df_similar.empty:
            raise HTTPException(status_code=404, detail="No vendors matched the capabilities.")

        df_ranked = rank_vendors(df_similar, query.capabilities)

        return df_ranked[[
            "product_name",
            "similarity_score",
            "rating",
            "reviews_count",
            "final_score",
            "exact_match"
        ]].to_dict(orient="records")

    except HTTPException as e:
        raise e
    except Exception as e:
        print("EXCEPTION TRACEBACK:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)