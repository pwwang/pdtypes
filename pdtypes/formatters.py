"""Monkey-patch data frame formatter to
1. add dtypes next to column names when printing
2. collapse data frames when they are elements of a parent data frame.
"""
from typing import Mapping, List

from pandas import DataFrame
from pandas.io.formats.html import (
    HTMLFormatter,
    NotebookFormatter,
    MultiIndex,
    get_level_lengths,
)
from pandas.io.formats.format import (
    DataFrameFormatter,
    lib,
    format_array,
)
try:
    from pandas.io.formats.format import (
        GenericArrayFormatter,
    )
except ImportError:  # pragma: no cover
    # pandas 2.2
    from pandas.io.formats.format import (
        _GenericArrayFormatter as GenericArrayFormatter,
    )

from pandas.io.formats.string import StringFormatter


class PdtypesDataFrameFormatter(DataFrameFormatter):
    """Custom formatter for DataFrame"""

    def get_strcols(self) -> List[List[str]]:
        strcols = self._get_strcols_without_index()

        if self.index:
            #           dtype
            str_index = [""] + self._get_formatted_index(self.tr_frame)
            strcols.insert(0, str_index)

        return strcols

    def format_col(self, i: int) -> List[str]:
        """Format column, add dtype ahead"""
        frame = self.tr_frame
        formatter = self._get_formatter(i)
        dtype = frame.iloc[:, i].dtype.name

        return [f"<{dtype}>"] + format_array(
            frame.iloc[:, i]._values,
            formatter,
            float_format=self.float_format,
            na_rep=self.na_rep,
            space=self.col_space.get(frame.columns[i]),
            decimal=self.decimal,
            leading_space=self.index,
        )

    def _truncate_horizontally(self) -> None:
        """Patch it to keep `_datar` metadata when truncating horizontally"""
        if "_datar" not in self.tr_frame._metadata:
            super()._truncate_horizontally()
        else:
            # pwwang/datar#208
            meta = self.tr_frame._datar
            super()._truncate_horizontally()
            self.tr_frame._datar = meta


class PdtypesGenericArrayFormatter(GenericArrayFormatter):
    """Generic Array Formatter to show DataFrame element in a cell in a
    collpased representation
    """

    def _format_strings(self) -> List[str]:
        out = super()._format_strings()
        for i, v in enumerate(self.values):
            if isinstance(v, DataFrame):
                out[i] = f"<DF {v.shape[0]}x{v.shape[1]}>"

        return out


class PdtypesHTMLFormatter(HTMLFormatter):
    """Fix nrows as we added one more row (dtype)"""

    def _write_regular_rows(
        self, fmt_values: Mapping[int, List[str]], indent: int
    ) -> None:
        is_truncated_horizontally = self.fmt.is_truncated_horizontally
        is_truncated_vertically = self.fmt.is_truncated_vertically

        nrows = len(self.fmt.tr_frame) + 1

        if self.fmt.index:
            fmtter = self.fmt._get_formatter("__index__") or str
            index_values = self.fmt.tr_frame.index.map(fmtter)

        # pandas 2.2
        index_values = list(index_values)
        # dtype row
        index_values.insert(0, "")

        row: List[str] = []
        for i in range(nrows):

            if (
                is_truncated_vertically
                and i == (self.fmt.tr_row_num)
            ):  # pragma: no cover
                str_sep_row = ["..."] * len(row)
                tags = (
                    {
                        j: 'style="font-style: italic;" '
                        for j, _ in enumerate(str_sep_row)
                    }
                    if i == 0
                    else None
                )

                self.write_tr(
                    str_sep_row,
                    indent,
                    self.indent_delta,
                    tags=tags,
                    nindex_levels=self.row_levels,
                )

            row = []
            if self.fmt.index:
                row.append(index_values[i])
            # see gh-22579
            # Column misalignment also occurs for
            # a standard index when the columns index is named.
            # Add blank cell before data cells.
            elif self.show_col_idx_names:  # pragma: no cover
                row.append("")
            row.extend(fmt_values[j][i] for j in range(self.ncols))

            if is_truncated_horizontally:  # pragma: no cover
                dot_col_ix = self.fmt.tr_col_num + self.row_levels
                row.insert(dot_col_ix, "...")

            tags = (
                {j: 'style="font-style: italic;" ' for j, _ in enumerate(row)}
                if i == 0
                else None
            )

            self.write_tr(
                row,
                indent,
                self.indent_delta,
                tags=tags,
                nindex_levels=self.row_levels,
            )

    def _write_hierarchical_rows(
        self, fmt_values: Mapping[int, List[str]], indent: int
    ) -> None:  # pragma: no cover
        template = 'rowspan="{span}" valign="top"'

        is_truncated_horizontally = self.fmt.is_truncated_horizontally
        is_truncated_vertically = self.fmt.is_truncated_vertically
        frame = self.fmt.tr_frame
        nrows = len(frame) + 1

        assert isinstance(frame.index, MultiIndex)
        try:
            idx_values = frame.index.format(
                sparsify=False, adjoin=False, names=False
            )
        except AttributeError:
            # pandas v3: Removed Index.format, use Index.astype() with str
            # or Index.map() with a formatter function instead (GH 55439)
            idx_values = frame.index._format_multi(
                sparsify=False, include_names=False
            )

        # add dtype row
        len_idx_values = len(idx_values)
        idx_values = list(zip(*idx_values))
        idx_values.insert(0, ("",) * len_idx_values)

        if self.fmt.sparsify:
            # GH3547
            sentinel = lib.no_default
            try:
                levels = frame.index.format(
                    sparsify=sentinel, adjoin=False, names=False
                )
            except AttributeError:
                # pandas v3: Removed Index.format, use Index.astype() with str
                # or Index.map() with a formatter function instead (GH 55439)
                levels = frame.index._format_multi(
                    sparsify=sentinel, include_names=False
                )

            levels = [("",) + level for level in levels]
            level_lengths = get_level_lengths(levels, sentinel)
            inner_lvl = len(level_lengths) - 1
            if is_truncated_vertically:
                # Insert ... row and adjust idx_values and
                # level_lengths to take this into account.
                ins_row = self.fmt.tr_row_num
                inserted = False
                for lnum, records in enumerate(level_lengths):
                    rec_new = {}
                    for tag, span in list(records.items()):
                        if tag >= ins_row:
                            rec_new[tag + 1] = span
                        elif tag + span > ins_row:
                            rec_new[tag] = span + 1

                            # GH 14882 - Make sure insertion done once
                            if not inserted:
                                dot_row = list(idx_values[ins_row - 1])
                                dot_row[-1] = "..."
                                idx_values.insert(ins_row, tuple(dot_row))
                                inserted = True
                            else:
                                dot_row = list(idx_values[ins_row])
                                dot_row[inner_lvl - lnum] = "..."
                                idx_values[ins_row] = tuple(dot_row)
                        else:
                            rec_new[tag] = span
                        # If ins_row lies between tags, all cols idx cols
                        # receive ...
                        if tag + span == ins_row:
                            rec_new[ins_row] = 1
                            if lnum == 0:
                                idx_values.insert(
                                    ins_row, tuple(["..."] * len(level_lengths))
                                )

                            # GH 14882 - Place ... in correct level
                            elif inserted:
                                dot_row = list(idx_values[ins_row])
                                dot_row[inner_lvl - lnum] = "..."
                                idx_values[ins_row] = tuple(dot_row)
                    level_lengths[lnum] = rec_new

                level_lengths[inner_lvl][ins_row] = 1
                for ix_col in range(len(fmt_values)):
                    fmt_values[ix_col].insert(ins_row, "...")
                nrows += 1

            for i in range(nrows):
                row = []
                tags = {}

                sparse_offset = 0
                j = 0
                for records, v in zip(level_lengths, idx_values[i]):
                    if i in records:
                        if records[i] > 1:
                            tags[j] = (
                                template.format(span=records[i])
                                if i > 0
                                else 'style="font-style: italic;" '
                            )
                    else:
                        sparse_offset += 1
                        continue

                    j += 1
                    row.append(v)

                row.extend(fmt_values[j][i] for j in range(self.ncols))
                if i == 0:
                    tags.update(
                        {
                            j + k: 'style="font-style: italic;" '
                            for k in range(self.ncols)
                        }
                    )

                if is_truncated_horizontally:
                    row.insert(
                        self.row_levels - sparse_offset + self.fmt.tr_col_num,
                        "...",
                    )

                self.write_tr(
                    row,
                    indent,
                    self.indent_delta,
                    tags=tags,
                    nindex_levels=len(levels) - sparse_offset,
                )
        else:
            row = []
            for i in range(len(frame) + 1):
                if is_truncated_vertically and i == (self.fmt.tr_row_num):
                    str_sep_row = ["..."] * len(row)
                    tags = (
                        {
                            j: 'style="font-style: italic;" '
                            for j, _ in enumerate(str_sep_row)
                        }
                        if i == 0
                        else None
                    )

                    self.write_tr(
                        str_sep_row,
                        indent,
                        self.indent_delta,
                        tags=tags,
                        nindex_levels=self.row_levels,
                    )

                idx_values = list(
                    zip(
                        *frame.index.format(
                            sparsify=False, adjoin=False, names=False
                        )
                    )
                )
                idx_values.insert(0, ("",) * len_idx_values)
                row = []
                row.extend(idx_values[i])
                row.extend(fmt_values[j][i] for j in range(self.ncols))
                if is_truncated_horizontally:
                    row.insert(self.row_levels + self.fmt.tr_col_num, "...")

                tags = (
                    {
                        j: 'style="font-style: italic;" '
                        for j, _ in enumerate(row)
                    }
                    if i == 0
                    else None
                )

                self.write_tr(
                    row,
                    indent,
                    self.indent_delta,
                    tags=tags,
                    nindex_levels=frame.index.nlevels,
                )

    def render(self) -> List[str]:
        """Render the df"""
        super().render()
        self.write(getattr(self.frame, "_html_footer", ""))

        return self.elements


class PdtypesNotebookFormatter(PdtypesHTMLFormatter, NotebookFormatter):
    """Notebook Formatter"""


class PdtypesStringFormatter(StringFormatter):
    """String Formatter"""

    def to_string(self) -> str:
        """To string representation"""
        text = super().to_string()
        str_footer = getattr(self.frame, "_str_footer", None)
        if str_footer:
            text = f"{text}\n{str_footer}"

        return text
