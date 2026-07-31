# -*- coding: utf-8 -*-
"""Dung chung cho cac file train: bo feature, 3 thuat toan, ham danh gia.

Cach dung trong notebook:
    from _common_train import CAT, B_NUM, dat_categories, prep, ALGOS, metrics
    df = pd.read_parquet(...)
    df = dat_categories(df)          # BAT BUOC, truoc khi chia train/test
    ...
    m.fit(prep(tr, B_NUM), y_tr)
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb
import xgboost as xgb

CAT = ["service_name", "pickup_location_name", "dropoff_location_name", "weather_main"]

# Huong 1 - gia cuoi truc tiep (dung latest_observed_price, da gom surge)
D_NUM = ["quote_distance", "quote_duration", "gio_vn", "latest_observed_price",
         "history_60m_price_mean", "history_60m_price_std", "history_60m_price_slope_per_minute",
         "latest_observed_quote_distance", "latest_observed_quote_duration", "actual_observation_age_minutes"]

# Hybrid - gia co ban (dung latest_observed_base, da bo surge)
B_NUM = ["quote_distance", "quote_duration", "gio_vn", "latest_observed_base",
         "history_60m_price_mean", "history_60m_price_std", "history_60m_price_slope_per_minute",
         "latest_observed_quote_distance", "latest_observed_quote_duration", "actual_observation_age_minutes"]

# He so nhan - nhom cung-cau
M_NUM = ["pricing_market_imbalance_5m_lag", "pricing_demand_index_5m_lag", "pricing_supply_index_5m_lag",
         "pricing_quote_count_5m_lag", "latest_observed_multiplier", "gio_vn", "actual_observation_age_minutes"]


def dat_categories(df):
    """Chuyen cac cot CAT sang dtype 'category' voi DANH MUC CO DINH tu toan bo du lieu.

    PHAI goi 1 lan tren df day du, TRUOC khi chia train/test.

    Vi sao bat buoc: neu de prep() tu cast tren tung tap con, pandas sinh danh muc
    rieng theo gia tri co trong tap con do -> train va test co the co MA SO KHAC NHAU
    cho cung mot gia tri (vd 'Clear' = 0 o train nhung = 1 o test). Hau qua:
      - XGBoost (enable_categorical): bao loi "Found a category not in the training set"
      - HistGB / LightGBM: KHONG bao loi nhung doc sai ma -> du doan sai am tham
    Cast 1 lan tren df day du thi loc theo dong van giu nguyen toan bo danh muc.
    """
    for c in CAT:
        df[c] = df[c].astype("category")
    return df


def prep(d, num):
    """Chon cot feature. Giu nguyen dtype 'category' da dat boi dat_categories()."""
    X = d[CAT + num].copy()
    for c in CAT:
        if not isinstance(X[c].dtype, pd.CategoricalDtype):
            raise TypeError(
                f"Cot '{c}' chua co dtype 'category'. Goi dat_categories(df) tren df day du "
                "TRUOC khi chia train/test (xem docstring dat_categories)."
            )
    return X


def tao_histgb():
    return HistGradientBoostingRegressor(
        max_iter=500, learning_rate=0.05, l2_regularization=1.0,
        early_stopping=True, validation_fraction=0.1, n_iter_no_change=20,
        categorical_features=CAT, random_state=42)


def tao_lightgbm():
    return lgb.LGBMRegressor(
        n_estimators=800, learning_rate=0.03, num_leaves=63,
        subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
        random_state=42, verbose=-1)


def tao_xgboost():
    return xgb.XGBRegressor(
        n_estimators=800, learning_rate=0.03, max_depth=7,
        subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
        tree_method="hist", enable_categorical=True, random_state=42,
        early_stopping_rounds=20, eval_metric="rmse")


ALGOS = {
    "HistGB": tao_histgb,
    "LightGBM": tao_lightgbm,
    "XGBoost": tao_xgboost,
}


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    return dict(MAE=mean_absolute_error(y, p), RMSE=mean_squared_error(y, p) ** .5,
                R2=r2_score(y, p), MAPE=np.mean(np.abs((y - p) / y)) * 100)
