from contextlib import contextmanager
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

orig_dataframegroupby_repr_html_ = getattr(DataFrameGroupBy, "_repr_html_", None)
orig_dataframegroupby__repr__ = DataFrameGroupBy.__repr__
orig_dataframe_repr_html_ = getattr(DataFrame, "_repr_html_", None)
orig_dataframe__repr__ = DataFrame.__repr__


@contextmanager
def _with_footer_property(inst: DataFrameGroupBy, name: str, footer: str):
    target_class = inst.obj.__class__
    orig_prop = getattr(target_class, name, None)
    setattr(target_class, name, property(lambda x: footer))
    try:
        yield
    finally:
        if orig_prop is not None:
            setattr(target_class, name, orig_prop)
        else:
            delattr(target_class, name)


def dataframegroupby_repr_html_(self, *args, **kwargs) -> str:
    try:
        grouper = self._grouper  # pandas 2.2
    except AttributeError:
        grouper = self.grouper

    footer = (
        "<p>Groups: "
        f"{', '.join((str(name) for name in grouper.names))} "
        f"(n={grouper.ngroups})</p>"
    )
    with _with_footer_property(self, "_html_footer", footer):
        return DataFrame._repr_html_(self.obj, *args, **kwargs)


def dataframegroupby__repr__(self, *args, **kwargs) -> str:
    try:
        grouper = self._grouper  # pandas 2.2
    except AttributeError:
        grouper = self.grouper

    footer = (
        f"[Groups: {', '.join((str(name) for name in grouper.names))} "
        f"(n={grouper.ngroups})]"
    )
    with _with_footer_property(self, "_str_footer", footer):
        return DataFrame.__repr__(self.obj, *args, **kwargs)
