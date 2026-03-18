from ....NXOpen import *
from ...CAE import *

import typing
import enum

class Utils(Utilities.NXRemotableObject):
    def __init__(self, owner: CAE.CaeSession) -> None: ...
    def CreateMappedPanelsFromNodes(self, sourceGroups: typing.List[CAE.CaeGroup], targetObjects: typing.List[TaggedObject], maxDistance: float, numInfluencingNodes: int, groupNames: str, panelNames: str) -> None: ...
    def Tag(self) -> Tag: ...



class NamespaceDoc(System.Object):
    def __init__(self) -> None: ...


