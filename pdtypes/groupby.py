from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

orig_dataframegroupby_repr_html_ = getattr(
    DataFrameGroupBy,
    "_repr_html_",
    None,
)

orig_dataframegroupby__repr__ = DataFrameGroupBy.__repr__


def dataframegroupby_repr_html_(self, *args, **kwargs) -> str:
    self.obj.attrs["_html_footer"] = getattr(
        self,
        "_html_footer",
        (
            f"<p>Groups: {', '.join(self.grouper.names)} "
            f"(n={self.grouper.ngroups})</p>"
        ),
    )
    out = DataFrame._repr_html_(self.obj, *args, **kwargs)
    del self.obj.attrs["_html_footer"]
    return out


def dataframegroupby__repr__(self, *args, **kwargs) -> str:
    self.obj.attrs["_str_footer"] = getattr(
        self,
        "_str_footer",
        (
            f"[Groups: {', '.join(self.grouper.names)} "
            f"(n={self.grouper.ngroups})]"
        ),
    )
    out = DataFrame.__repr__(self.obj, *args, **kwargs)
    del self.obj.attrs["_str_footer"]
    return out
