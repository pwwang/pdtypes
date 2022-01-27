
from pandas.io.formats import format, html, string
from pandas.core.groupby import DataFrameGroupBy
from .formatters import (
    # patched formatters
    PdtypesDataFrameFormatter,
    PdtypesGenericArrayFormatter,
    PdtypesHTMLFormatter,
    PdtypesNotebookFormatter,
    PdtypesStringFormatter,
    # original formatters
    DataFrameFormatter,
    GenericArrayFormatter,
    HTMLFormatter,
    NotebookFormatter,
    StringFormatter,
)
from .groupby import (
    orig_dataframegroupby_repr_html_,
    orig_dataframegroupby__repr__,
    dataframegroupby_repr_html_,
    dataframegroupby__repr__,
)


def patch() -> None:
    """Money-patch pandas dataframe formatters to show data types in terminal
    and notebooks"""
    format.DataFrameFormatter = PdtypesDataFrameFormatter
    format.GenericArrayFormatter = PdtypesGenericArrayFormatter
    html.HTMLFormatter = PdtypesHTMLFormatter
    html.NotebookFormatter = PdtypesNotebookFormatter
    string.StringFormatter = PdtypesStringFormatter
    DataFrameGroupBy._repr_html_ = dataframegroupby_repr_html_
    DataFrameGroupBy.__repr__ = dataframegroupby__repr__


def unpatch() -> None:
    """Unpatch pandas, get everything back to what it was."""
    format.DataFrameFormatter = DataFrameFormatter
    format.GenericArrayFormatter = GenericArrayFormatter
    html.HTMLFormatter = HTMLFormatter
    html.NotebookFormatter = NotebookFormatter
    string.StringFormatter = StringFormatter
    DataFrameGroupBy._repr_html_ = orig_dataframegroupby_repr_html_
    DataFrameGroupBy.__repr__ = orig_dataframegroupby__repr__
