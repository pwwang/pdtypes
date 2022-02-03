# pdtypes

Show data types for pandas data frames in terminal and notebooks by monkey-patching pandas formatters

| Turn this | into |
| --------- | ---- |
| ![terminal_without_pdtypes][1] | ![terminal_with_pdtypes][2] |
| ![terminal_without_pdtypes_gf][3] | ![terminal_with_pdtypes_gf][4] |
| ![notebook_without_pdtypes][5] | ![notebook_with_pdtypes][6] |
| ![notebook_without_pdtypes_gf][7] | ![notebook_with_pdtypes_gf][8] |



## Installation
```shell
pip install -U pdtypes
```

## Usage
```python
# Patching enabled by default
import pdtypes
```

To disable patching (get everything back to what it was)
```python
import pdtypes

# ...
pdtypes.unpatch()

# To patch again
pdtypes.patch()

```


[1]: docs/terminal_without_pdtypes.png
[2]: docs/terminal_with_pdtypes.png
[3]: docs/terminal_without_pdtypes_gf.png
[4]: docs/terminal_with_pdtypes_gf.png
[5]: docs/notebook_without_pdtypes.png
[6]: docs/notebook_with_pdtypes.png
[7]: docs/notebook_without_pdtypes_gf.png
[8]: docs/notebook_with_pdtypes_gf.png
