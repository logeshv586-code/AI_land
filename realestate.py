# real_estate_service.py
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import joblib
import uvicorn

# ---------------------------
# 1) Utilities
# ---------------------------

def haversine(lon1, lat1, lon2, lat2):
    # return distance in kilometers
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def normalize_series(s):
    return (s - s.min()) / (s.max() - s.min()) if s.max() != s.min() else s * 0.0

# ---------------------------
# 2) Placeholder data loaders
# ---------------------------
# Replace these with real connectors (API calls, DB queries, CSV reads)

def load_property_data() -> pd.DataFrame:
    """
    Example synthetic property dataset. Replace with real data ingestion.
    Expected columns: property_id, lat, lon, beds, baths, sqft, year_built, sale_price, last_sale_date, assessor_id, ...
    """
    # Synthetic example
    rng = np.random.default_rng(42)
    n = 5000
    df = pd.DataFrame({
        "property_id": [f"P{1000+i}" for i in range(n)],
        "lat": rng.uniform(37.5, 42.5, n),   # IL approx lat range
        "lon": rng.uniform(-91.5, -87.0, n),
        "beds": rng.integers(1, 6, n),
        "baths": rng.integers(1, 4, n),
        "sqft": rng.integers(600, 4500, n),
        "year_built": rng.integers(1900, 2021, n),
        "sale_price": rng.integers(50000, 800000, n),
        "pct_flood_zone": rng.random(n),  # synthetic environmental risk indicator
        "crime_score_block": rng.uniform(0, 1, n),
        "school_rating": rng.integers(1, 10, n),
        "distance_to_hospital_km": rng.uniform(0.1, 20, n),
        "distance_to_major_employer_km": rng.uniform(0.1, 30, n)
    })
    return df

def load_poi_data() -> pd.DataFrame:
    """Placeholder for POIs like hospitals, schools, companies. Fill with real provider data."""
    # minimal example
    return pd.DataFrame([
        {"poi_id": "H1", "type": "hospital", "lat": 41.88, "lon": -87.62},
        {"poi_id": "S1", "type": "school", "lat": 41.90, "lon": -87.65},
    ])

def load_user_interactions() -> pd.DataFrame:
    """
    Placeholder for user interactions (for collaborative-style suggestions):
    columns: user_id, property_id, action (view, save, contact), timestamp
    """
    # Synthetic example small
    data = [
        ("user1", "P1000", "view"),
        ("user1", "P1002", "save"),
        ("user2", "P1001", "view"),
    ]
    return pd.DataFrame(data, columns=["user_id", "property_id", "action"])

# ---------------------------
# 3) Feature engineering
# ---------------------------

def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute features needed for AVM and beneficiary rate.
    Keep feature engineering deterministic and explainable.
    """
    df = df.copy()
    df["age"] = 2025 - df["year_built"]
    df["price_per_sqft"] = df["sale_price"] / df["sqft"]
    # Normalize some features for composite scoring
    df["norm_school"] = normalize_series(df["school_rating"])
    df["norm_crime_inv"] = 1.0 - normalize_series(df["crime_score_block"])  # higher is safer
    df["norm_flood_inv"] = 1.0 - normalize_series(df["pct_flood_zone"])
    df["norm_dist_hospital"] = 1.0 - normalize_series(df["distance_to_hospital_km"])
    df["norm_dist_employer"] = 1.0 - normalize_series(df["distance_to_major_employer_km"])
    # completeness metric: fraction of required non-null fields
    required = ["beds", "baths", "sqft", "year_built", "sale_price", "lat", "lon"]
    df["completeness"] = df[required].notnull().mean(axis=1)
    return df

# ---------------------------
# 4) AVM (value prediction) training + uncertainty
# ---------------------------

class AVMModel:
    def __init__(self):
        self.model = None
        self.features = ["beds", "baths", "sqft", "age", "price_per_sqft",
                         "norm_school", "norm_crime_inv", "norm_flood_inv",
                         "norm_dist_hospital", "norm_dist_employer"]

    def train(self, df: pd.DataFrame):
        df = compute_features(df)
        X = df[self.features].fillna(0)
        y = df["sale_price"]
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        self.model = rf
        # optionally save training metadata / feature distributions
        print("AVM trained. Validation size:", X_val.shape[0])

    def predict_with_uncertainty(self, inputs: pd.DataFrame):
        """
        Predict value and estimate uncertainty using tree ensemble variance.
        Returns (mean_prediction, std_of_tree_predictions)
        """
        X = inputs[self.features].fillna(0)
        preds_per_tree = np.array([t.predict(X) for t in self.model.estimators_])
        mean = preds_per_tree.mean(axis=0)
        std = preds_per_tree.std(axis=0)
        return mean, std

# ---------------------------
# 5) Beneficiary Rate calculation
# ---------------------------

def compute_beneficiary_rate(df: pd.DataFrame, weights: Optional[Dict[str, float]] = None) -> pd.Series:
    """
    Composite rate combining predicted value (normalized), safety, school, proximity, and hazard.
    weights: dict of factor weights (sum not required; result normalized)
    """
    default_w = {
        "value": 8.0,
        "school": 8.0,
        "crime_inv": 6.0,
        "env_inv": 5.0,
        "employer_proximity": 7.0,
    }
    if weights:
        default_w.update(weights)
    w = default_w

    # Normalize components
    # value component: use price_per_sqft as proxy (or the model predicted value)
    df = df.copy()
    df["norm_value"] = normalize_series(df["price_per_sqft"])
    # already have normalized components from compute_features
    components = {
        "value": df["norm_value"] * w["value"],
        "school": df["norm_school"] * w["school"],
        "crime": df["norm_crime_inv"] * w["crime_inv"],
        "env": df["norm_flood_inv"] * w["env_inv"],
        "employer": df["norm_dist_employer"] * w["employer_proximity"]
    }
    total = sum(components.values())
    # normalize beneficiary rate to 0-100 scale
    beneficiary_raw = total / (sum(w.values()))
    beneficiary_0_100 = (beneficiary_raw - beneficiary_raw.min()) / (beneficiary_raw.max() - beneficiary_raw.min()) * 100 \
                        if beneficiary_raw.max() != beneficiary_raw.min() else beneficiary_raw*0
    return beneficiary_0_100

# ---------------------------
# 6) Recommendation engine (hybrid)
# ---------------------------

class Recommender:
    def __init__(self):
        self.vec = DictVectorizer(sparse=False)
        self.content_matrix = None
        self.properties_index = None
        self.nn = None
        # collaborative interaction matrix
        self.interaction_matrix = None
        self.user_index = {}
        self.prop_index = {}

    def fit_content(self, df: pd.DataFrame, content_cols: List[str] = None):
        """
        Build vectors of property content features for content-based filtering.
        content_cols: e.g., ['beds', 'baths', 'sqft', 'school_rating', 'crime_score_block', 'pct_flood_zone']
        """
        if content_cols is None:
            content_cols = ['beds', 'baths', 'sqft', 'school_rating', 'crime_score_block', 'pct_flood_zone']
        props = df.copy()
        props["property_id"] = props["property_id"].astype(str)
        dicts = props[content_cols].fillna(0).to_dict(orient="records")
        self.content_matrix = self.vec.fit_transform(dicts)
        self.properties_index = props["property_id"].tolist()
        # build nn index
        self.nn = NearestNeighbors(n_neighbors=10, metric='cosine').fit(self.content_matrix)

    def recommend_content(self, property_id: str, top_k: int = 8):
        if property_id not in self.properties_index:
            return []
        idx = self.properties_index.index(property_id)
        vec = self.content_matrix[idx:idx+1]
        dists, inds = self.nn.kneighbors(vec, n_neighbors=top_k+1)
        recs = []
        for i in inds[0]:
            pid = self.properties_index[i]
            if pid != property_id:
                recs.append(pid)
        return recs[:top_k]

    def fit_collaborative(self, interactions_df: pd.DataFrame):
        """
        Build a simple user-property interaction matrix and apply nearest neighbors on property vectors.
        interactions_df: columns user_id, property_id, action
        We'll convert actions to weights (view=1, save=3, contact=5)
        """
        weights = {"view": 1.0, "save": 3.0, "contact": 5.0}
        interactions_df = interactions_df.copy()
        interactions_df["weight"] = interactions_df["action"].map(weights).fillna(1.0)
        users = interactions_df["user_id"].unique().tolist()
        props = interactions_df["property_id"].unique().tolist()
        self.user_index = {u: i for i, u in enumerate(users)}
        self.prop_index = {p: i for i, p in enumerate(props)}
        mat = np.zeros((len(users), len(props)))
        for _, row in interactions_df.iterrows():
            u = self.user_index[row["user_id"]]
            p = self.prop_index[row["property_id"]]
            mat[u, p] += row["weight"]
        # store item vectors (collaborative)
        self.interaction_matrix = mat
        # for recommending similar properties use item-item similarity
        self.item_sim = cosine_similarity(mat.T)
        self.collab_props = props

    def recommend_collaborative(self, property_id: str, top_k: int = 8):
        if property_id not in getattr(self, "collab_props", []):
            return []
        idx = self.collab_props.index(property_id)
        sims = self.item_sim[idx]
        best_idx = np.argsort(-sims)
        recs = [self.collab_props[i] for i in best_idx if i != idx]
        return recs[:top_k]

    def hybrid_recommend(self, property_id: str, top_k=8, alpha=0.6):
        """
        Mix content-based and collaborative scores. alpha weights content-based higher.
        """
        content = self.recommend_content(property_id, top_k=top_k*2)
        collab = self.recommend_collaborative(property_id, top_k=top_k*2)
        # scoring
        score_map = {}
        for i, pid in enumerate(content):
            score_map[pid] = score_map.get(pid, 0) + alpha * (1.0 / (1 + i))
        for i, pid in enumerate(collab):
            score_map[pid] = score_map.get(pid, 0) + (1 - alpha) * (1.0 / (1 + i))
        ranked = sorted(score_map.items(), key=lambda x: -x[1])
        return [p for p, s in ranked][:top_k]

# ---------------------------
# 7) Confidence score combining uncertainty and completeness
# ---------------------------

def compute_confidence(pred_std: np.ndarray, completeness: pd.Series):
    """
    pred_std: predicted standard deviation (higher = less confident)
    completeness: fraction 0..1 (higher = more data)
    Combine into 0..1 confidence score (1 best)
    Approach:
      - normalize std to 0..1 by dividing by (std + small epsilon) and invert
      - combine with completeness weighted average
    """
    eps = 1e-8
    norm_std = (pred_std - pred_std.min()) / (pred_std.max() - pred_std.min() + eps) if pred_std.max() != pred_std.min() else np.zeros_like(pred_std)
    inv_std = 1.0 - norm_std  # higher means more confident
    # combine: 70% model certainty, 30% data completeness (weights can be tuned)
    conf = 0.7 * inv_std + 0.3 * completeness.values
    # clip 0..1
    conf = np.clip(conf, 0.0, 1.0)
    return conf

# ---------------------------
# 8) API wrapper (FastAPI)
# ---------------------------

app = FastAPI(title="Illinois Real Estate Suggestion Service")

# load synthetic data & train models on startup (in prod, load persisted models)
property_df = load_property_data()
poi_df = load_poi_data()
interactions_df = load_user_interactions()

# compute features
property_df = compute_features(property_df)

# train avm
avm = AVMModel()
avm.train(property_df)

# recommender
reco = Recommender()
reco.fit_content(property_df)
try:
    reco.fit_collaborative(interactions_df)
except Exception:
    # interactions may be empty in synthetic case
    pass

# Pydantic models for requests
class PropertyQuery(BaseModel):
    property_id: str

class UserPref(BaseModel):
    user_id: Optional[str] = None
    must_have: Optional[Dict[str, float]] = None  # e.g., {"beds": 3}
    prefer: Optional[Dict[str, float]] = None     # e.g., {"school_rating": 8}
    location: Optional[Dict[str, float]] = None   # {"lat": , "lon": }
    radius_km: Optional[float] = 10.0

@app.get("/predict_value/{property_id}")
def predict_value(property_id: str):
    row = property_df[property_df["property_id"] == property_id]
    if row.empty:
        return {"error": "property not found"}
    mean, std = avm.predict_with_uncertainty(row)
    conf = compute_confidence(std, row["completeness"])
    return {
        "property_id": property_id,
        "predicted_value": float(mean[0]),
        "value_std": float(std[0]),
        "confidence": float(conf[0])
    }

@app.post("/beneficiary_rate")
def beneficiary_endpoint(q: PropertyQuery):
    row = property_df[property_df["property_id"] == q.property_id]
    if row.empty:
        return {"error": "property not found"}
    br = compute_beneficiary_rate(row)
    # also return components
    comps = {
        "norm_school": float(row["norm_school"].iloc[0]),
        "norm_crime_inv": float(row["norm_crime_inv"].iloc[0]),
        "norm_flood_inv": float(row["norm_flood_inv"].iloc[0]),
        "norm_dist_employer": float(row["norm_dist_employer"].iloc[0]),
        "price_per_sqft": float(row["price_per_sqft"].iloc[0])
    }
    return {
        "property_id": q.property_id,
        "beneficiary_rate": float(br.iloc[0]),
        "components": comps
    }

@app.post("/recommendations")
def recommend(q: UserPref):
    # If user passes a property_id in must_have, or location, fallback to content-based nearest
    # For simplicity we accept user-provided property_id in must_have with key 'property_id'
    prop_id = None
    if q.must_have and "property_id" in q.must_have:
        prop_id = q.must_have["property_id"]
    if prop_id:
        recs = reco.hybrid_recommend(prop_id, top_k=8)
        # attach beneficiary rate and confidence for each suggestion
        out = []
        for pid in recs:
            row = property_df[property_df["property_id"] == pid]
            if row.empty:
                continue
            mean, std = avm.predict_with_uncertainty(row)
            conf = compute_confidence(std, row["completeness"])
            br = compute_beneficiary_rate(row)
            out.append({
                "property_id": pid,
                "predicted_value": float(mean[0]),
                "confidence": float(conf[0]),
                "beneficiary_rate": float(br.iloc[0])
            })
        return {"recommendations": out}
    # Fallback: search by location & score
    if q.location:
        lat = q.location.get("lat")
        lon = q.location.get("lon")
        radius = q.radius_km or 10.0
        # filter by distance
        property_df["dist_km"] = property_df.apply(lambda r: haversine(lon, lat, r["lon"], r["lat"]), axis=1)
        cand = property_df[property_df["dist_km"] <= radius].copy()
        if cand.empty:
            return {"recommendations": []}
        # score candidates by beneficiary_rate * completeness
        cand["beneficiary_rate"] = compute_beneficiary_rate(cand)
        cand["score"] = cand["beneficiary_rate"] * cand["completeness"]
        top = cand.sort_values("score", ascending=False).head(8)
        out = []
        for _, row in top.iterrows():
            mean, std = avm.predict_with_uncertainty(pd.DataFrame([row]))
            conf = compute_confidence(std, pd.Series([row["completeness"]]))
            out.append({
                "property_id": row["property_id"],
                "beneficiary_rate": float(row["beneficiary_rate"]),
                "predicted_value": float(mean[0]),
                "confidence": float(conf[0]),
                "distance_km": float(row["dist_km"])
            })
        return {"recommendations": out}

    return {"error": "provide must_have.property_id or location"}

# ---------------------------
# 9) Run
# ---------------------------

if __name__ == "__main__":
    # in real deployment use gunicorn/uvicorn with workers and proper process manager
    uvicorn.run("real_estate_service:app", host="0.0.0.0", port=8000, log_level="info")
