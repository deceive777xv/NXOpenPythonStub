from ....NXOpen import *
from ...PDM import *

import typing
import enum

class SaveObserver(TaggedObjectCollection):
    def EnumerateMoveNext(self, currentTag: Tag, state: bytes) -> int: ...
    def ToArray(self) -> typing.List[PDM.SaveManagement.SaveCallbackData]: ...
    @typing.overload
    def __init__(self, owner: PDM.PdmSession) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def AddInitializeCallback(self, initializeCb: PDM.SaveManagement.SaveObserver.InitializeCb) -> int: ...
    def RemoveInitializeCallback(self, id: int) -> None: ...
    def AddAutoassignCallback(self, autoassignCb: PDM.SaveManagement.SaveObserver.AutoassignCb) -> int: ...
    def RemoveAutoassignCallback(self, id: int) -> None: ...
    def Tag(self) -> Tag: ...



    

    

    

    

    

    

class SaveCallbackData(TaggedObject):
    def __init__(self) -> None: ...
    def GetSaveObjects(self, saveObjects: typing.List[PDM.SmartSaveObject]) -> None: ...


class NamespaceDoc(System.Object):
    def __init__(self) -> None: ...


