import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

class DataPreprocessor:
    def __init__(self):
        self.scaler   = MinMaxScaler()
        self.encoders = {}

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        # Dublikatlarni olib tashlash
        before = len(df)
        df = df.drop_duplicates()

        # Bo'sh qiymatlarni to'ldirish
        for col in df.columns:
            is_numeric = pd.api.types.is_numeric_dtype(df[col])
            if not is_numeric:
                if df[col].mode().empty: continue
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df[col].fillna(df[col].mean())

        # Anomal qiymatlarni cheklash (IQR)
        num_cols = df.select_dtypes(include=np.number).columns
        for col in num_cols:
            Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            IQR = Q3 - Q1
            df[col] = df[col].clip(Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)

        return df

    def encode_and_scale(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cat_cols = df.select_dtypes(include='object').columns
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.encoders[col] = le

        num_cols = df.select_dtypes(include=np.number).columns
        if len(num_cols):
            df[num_cols] = self.scaler.fit_transform(df[num_cols])
        return df
