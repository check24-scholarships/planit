
import typing
from collections import namedtuple


Position = typing.Tuple[int, int]

# Empty / No plants are None
Plant = typing.Union[str, None]

BBox = namedtuple("BBox", ("x0", "y0", "x1", "y1"))
