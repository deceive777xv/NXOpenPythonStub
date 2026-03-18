from ...NXOpen import *

import typing
import enum

class PlacementSolution(NXObject):
    def __init__(self) -> None: ...


class PlacementEngineBuilder(Builder):
    def __init__(self) -> None: ...
    def ComputePlacementSolutions(self) -> typing.List[Placement.PlacementSolution]: ...
    def SetFilteredPlacementSolutions(self, placementSolutions: typing.List[Placement.PlacementSolution]) -> None: ...
    def ApplyPlacementSolution(self, placementSolution: Placement.PlacementSolution) -> None: ...


class NamespaceDoc(System.Object):
    def __init__(self) -> None: ...


