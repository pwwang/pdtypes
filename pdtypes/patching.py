
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
    # pandas 2.2
    format._GenericArrayFormatter = PdtypesGenericArrayFormatter
    format.GenericArrayFormatter = PdtypesGenericArrayFormatter
    format.DataFrameFormatter = PdtypesDataFrameFormatter
    html.HTMLFormatter = PdtypesHTMLFormatter
    html.NotebookFormatter = PdtypesNotebookFormatter
    string.StringFormatter = PdtypesStringFormatter
    DataFrameGroupBy._repr_html_ = dataframegroupby_repr_html_
    DataFrameGroupBy.__repr__ = dataframegroupby__repr__


def unpatch() -> None:
    """Unpatch pandas, get everything back to what it was."""
    # pandas 2.2
    format._GenericArrayFormatter = GenericArrayFormatter
    format.DataFrameFormatter = DataFrameFormatter
    format.GenericArrayFormatter = GenericArrayFormatter
    html.HTMLFormatter = HTMLFormatter
    html.NotebookFormatter = NotebookFormatter
    string.StringFormatter = StringFormatter
    DataFrameGroupBy._repr_html_ = orig_dataframegroupby_repr_html_
    DataFrameGroupBy.__repr__ = orig_dataframegroupby__repr__
