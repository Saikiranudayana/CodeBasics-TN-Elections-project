# utils package

# Pandas compat: Styler.map was added in 2.1; alias applymap for older versions
try:
    from pandas.io.formats.style import Styler as _Styler
    if not hasattr(_Styler, "map"):
        _Styler.map = _Styler.applymap
except Exception:
    pass
