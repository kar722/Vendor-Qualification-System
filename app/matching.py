import pandas as pd
import ast
import numpy as np
from sentence_transformers import SentenceTransformer, util

# === Load SBERT model once globally ===
model = SentenceTransformer('all-MiniLM-L6-v2')


def extract_feature_names(raw_features: str) -> str:
    """
    Parse the 'Features' column to extract clean feature names from nested JSON.
    Returns a space-separated string of all feature 'name' values.
    """
    try:
        outer_list = ast.literal_eval(raw_features)
        feature_names = []

        for item in outer_list:
            for feat in item.get("features", []):
                if isinstance(feat, dict):
                    name = feat.get("name", "").strip().lower()
                    if name:
                        feature_names.append(name)

        return " ".join(feature_names)
    except Exception:
        return ""


def load_and_prepare_data(path: str) -> pd.DataFrame:
    """
    Load and clean the dataset.
    Extract key columns and parsed features for semantic similarity matching.
    """
    df = pd.read_csv(path)
    cols = ['product_name', 'main_category', 'Features', 'rating', 'reviews_count']
    df = df[cols].dropna(subset=['product_name', 'main_category', 'Features']).copy()

    df['main_category'] = df['main_category'].str.strip()
    df['product_name'] = df['product_name'].str.strip()
    df['parsed_features'] = df['Features'].apply(extract_feature_names)

    return df


def filter_by_category(df: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    Return only vendors matching the requested software category.
    """
    return df[df['main_category'].str.lower() == category.lower()].reset_index(drop=True)


def has_exact_match(parsed_features: str, capabilities: list) -> bool:
    """
    Returns True if any user capability appears exactly in the parsed feature string.
    """
    return any(cap.lower() in parsed_features for cap in capabilities)


def compute_similarity(df: pd.DataFrame, user_capabilities: list, threshold: float = 0.30) -> pd.DataFrame:
    """
    Compute semantic similarity using SBERT between the user query and vendor features.
    - Applies a pre-boost similarity threshold to filter irrelevant vendors.
    - Applies an exact match boost (+0.05) for vendors that contain literal feature matches.
    Returns a sorted DataFrame of relevant vendors with similarity scores.
    """
    query_string = " ".join([cap.lower().strip() for cap in user_capabilities])

    # Compute embeddings
    vendor_embeddings = model.encode(df['parsed_features'].tolist(), convert_to_tensor=True)
    query_embedding = model.encode(query_string, convert_to_tensor=True)

    # Compute cosine similarity
    similarity_scores = util.cos_sim(query_embedding, vendor_embeddings)[0].cpu().numpy()
    df['similarity_score'] = similarity_scores

    # Filter vendors based on pre-boost threshold
    df = df[df['similarity_score'] >= threshold].copy()

    # Apply exact match boost
    df['exact_match'] = df['parsed_features'].apply(
        lambda f: has_exact_match(f, user_capabilities)
    )
    df['similarity_score'] += 0.05 * df['exact_match'].astype(float)

    return df.sort_values(by='similarity_score', ascending=False).reset_index(drop=True)