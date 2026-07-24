"""
Feature preprocessing for ML pipelines.

Scalers, encoders, imputers, polynomial features, and column-wise composition.
All transformers follow ``fit`` / ``transform`` / ``fit_transform``.

Examples
--------
>>> from aion.preprocessing import StandardScaler, SimpleImputer, PreprocessingPipeline
>>> pipe = PreprocessingPipeline([
...     ("impute", SimpleImputer(strategy="median")),
...     ("scale", StandardScaler()),
... ])
>>> X_train = pipe.fit_transform(X_train)
"""

from ._base import TransformerMixin
from .scalers import StandardScaler, MinMaxScaler, RobustScaler, Normalizer
from .encoders import LabelEncoder, OneHotEncoder, OrdinalEncoder
from .imputers import SimpleImputer
from .transforms import PolynomialFeatures, Binarizer, KBinsDiscretizer
from .pipeline import ColumnTransformer, PreprocessingPipeline

__all__ = [
    "TransformerMixin",
    "StandardScaler",
    "MinMaxScaler",
    "RobustScaler",
    "Normalizer",
    "LabelEncoder",
    "OneHotEncoder",
    "OrdinalEncoder",
    "SimpleImputer",
    "PolynomialFeatures",
    "Binarizer",
    "KBinsDiscretizer",
    "ColumnTransformer",
    "PreprocessingPipeline",
]
