import pandas as pd
import numpy as np
import tushare as ts


class StockBase:
    def __init__(self):
        # self.industries = ts.get_industry_classified()
        self._concepts = ts.get_concept_classified()  # type: pd.DataFrame
        self._accessible_concepts = self._concepts.copy()  # type: pd.DataFrame

    @property
    def concepts(self):
        return self._accessible_concepts

    @property
    def names(self):
        return self._accessible_concepts.name.values

    @property
    def c_names(self):
        return self._accessible_concepts.c_name.values

    @property
    def codes(self):
        return self._accessible_concepts.code.values

    @property
    def shape(self):
        return self._accessible_concepts.shape

    @property
    def index(self):
        return self._accessible_concepts.index

    def filter_by(self, name=None, c_name=None, code=None):
        mask = pd.Series(np.ones(self.shape[0], dtype=np.bool))
        if name is not None:
            mask = mask & (self._accessible_concepts.name == name)
        if c_name is not None:
            mask = mask & (self._accessible_concepts.c_name == c_name)
        if code is not None:
            mask = mask & (self._accessible_concepts.code == code)

        self._accessible_concepts = self._accessible_concepts[mask]
        return self

    def grouped_by_c_names(self):
        df = self._accessible_concepts
        return [df[df.c_name == c_name] for c_name in np.unique(self.c_names)]

    def reset_filter(self):
        self._accessible_concepts = self._concepts.copy()
        return self


class DataFetcher:
    def __init__(self, stocks, start=None, end=None, **kwargs):
        if isinstance(stocks, pd.Series):
            self.stocks = stocks.to_frame()
        elif isinstance(stocks, pd.DataFrame):
            self.stocks = stocks
        else:
            raise TypeError("Unrecognized `stocks`, expected pd.DataFrame or pd.Series, got {}".format(type(stocks)))

        self.start = start
        self.end = end
        self.kwargs = kwargs
        self._k = None

    def _fetch_k(self):
        self._k = {code: ts.get_k_data(code, self.start, self.end, **self.kwargs) for code in self.stocks.code}

    @property
    def k(self):
        if self._k is None:
            self._fetch_k()
        return self._k


class DataParser:
    def __init__(self, data_dict: dict, clean=True):
        self.data = data_dict

        if clean:
            self.data = {k: v for k, v in self.data.items() if isinstance(v, pd.DataFrame) and v.shape[0] > 0}

    def get_column(self, col):
        return {code: df[col] for code, df in self.data.items()}

    def get_by_columns(self, *cols):
        cols = list(cols)
        return {code: df[cols] for code, df in self.data.items()}


if __name__ == '__main__':
    # industries = ts.get_industry_classified()
    # concepts = ts.get_concept_classified()
    # ts.get_k_data(code=..., start="2019-01-01", end="2019-01-31").close
    stock_base = StockBase()
    stock_groups = stock_base.grouped_by_c_names()

    fetcher = DataFetcher(stock_groups[0], start="2019-01-01", end="2019-01-31")
    parser = DataParser(fetcher.k)
    parser.get_by_columns("close")
