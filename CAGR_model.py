import pandas as pd
import numpy as np

df = pd.read_csv("analysis_results_final.csv")

df.head()

df2  = df[["Symbol","Increase_9m_Pct","CAGR_Prev_5yr","CAGR_Prev_3yr","Market_Cap"]]

conditions = [
    df2["Increase_9m_Pct"] <= 5,
    (df2["Increase_9m_Pct"] > 5) & (df2["Increase_9m_Pct"] <= 15),
    df2["Increase_9m_Pct"] > 15
]

choices = ["Sell", "Hold", "Buy"]

df2["Signal"] = np.select(conditions, choices, default="Hold")

df2_unique = (
    df2.sort_values("Increase_9m_Pct", ascending=False)
       .drop_duplicates(subset="Symbol", keep="first")
)

from sklearn.model_selection import train_test_split

# Features (X) and Target (y)
X = df2_unique[[
    "Increase_9m_Pct",
    "CAGR_Prev_5yr",
    "CAGR_Prev_3yr",
    "Cap"
]]

y = df2_unique["Signal"]   
# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y   
)

print(X_train.shape, X_test.shape)
print(y_train.value_counts(normalize=True))
print(y_test.value_counts(normalize=True))

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

numeric_features = [
    "Increase_9m_Pct",
    "CAGR_Prev_5yr",
    "CAGR_Prev_3yr"
]

categorical_features = ["Cap"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cap", OneHotEncoder(handle_unknown="ignore", drop="first"), categorical_features)
    ]
)

model = Pipeline([
    ("preprocess", preprocessor),
    ("clf", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ))
])

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(y_pred)

results_df = X_test.copy()

results_df["Actual_Signal"] = y_test.values
results_df["Predicted_Signal"] = y_pred

results_df["Symbol"] = df2_unique.loc[X_test.index, "Symbol"].values

results_df = results_df[[
    "Symbol",
    "Increase_9m_Pct",
    "CAGR_Prev_5yr",
    "CAGR_Prev_3yr",
    "Cap",
    "Actual_Signal",
    "Predicted_Signal"
]]

print(results_df)

results_df.to_csv("stock_prediction_results2.csv", index=False)
