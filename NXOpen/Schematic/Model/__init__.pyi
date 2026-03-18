from ....NXOpen import *
from ...Schematic import *

import typing
import enum

class BaseObject(NXObject):
    def __init__(self) -> None: ...
    @property
    def Identifier(self) -> str: ...
    @Identifier.setter
    def Identifier(self, value: str) -> None: ...


