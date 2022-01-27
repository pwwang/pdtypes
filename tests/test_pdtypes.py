import pytest
import pdtypes
import pandas as pd

@pytest.fixture
def patched():
    pdtypes.patch()
    yield
    pdtypes.unpatch()

@pytest.fixture
def unpatched():
    pdtypes.unpatch()
    yield
    pdtypes.patch()

@pytest.fixture
def df():
    return pd.DataFrame({"x": [1,1,2,2], "y": [1.0,2.0,3.0,4.0]})

@pytest.fixture
def big_df():
    data = {}
    for i in range(100):
        data[f"v{i}"] = range(100)
    return pd.DataFrame(data).set_index(["v0", "v1"])

@pytest.fixture
def df_df():
    df1 = pd.DataFrame({"x": [1,1,2,2], "y": [1,2,3,4]})
    df2 = pd.DataFrame({"a": [1, 2], "b": [df1, df1]})
    return df2

@pytest.fixture
def mf():
    return pd.DataFrame(
        {"x": [1,1,2,2], "y": [1,2,3,4], "z": [5,6,7,7]}
    ).set_index(["x", "y"])

@pytest.fixture
def gf():
    return pd.DataFrame({"x": [1,1,2,2], "y": [1,2,3,4]}).groupby("x")

def test_unpatched_df(unpatched, df, gf, df_df):
    assert "<int64>" not in str(df)
    assert "<int64>" not in df._repr_html_()
    assert "<pandas.core.groupby.generic.DataFrameGroupBy" in str(gf)
    assert getattr(gf, "_repr_html_", None) is None
    assert "x  y" in str(df_df)

def test_patched_df(patched, df, gf, df_df, big_df):
    assert "<int64>" in str(df)
    assert "<int64>" in str(gf)
    assert "&lt;int64&gt;" in gf._repr_html_()
    assert "Groups" in str(gf)
    assert "Groups" in gf._repr_html_()
    assert "<DF 4x2>" in str(df_df)
    assert "&lt;DF 4x2&gt;" in df_df._repr_html_()
    assert "..." in str(big_df)

def test_patched_multiindex_df(patched, mf):
    assert "x y <int64>" in str(mf)
    assert str(mf).count("<int64>") == 1