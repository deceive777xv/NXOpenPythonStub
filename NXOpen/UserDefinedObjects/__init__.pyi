from ...NXOpen import *

import typing
import enum

class UserDefinedObjectManager(Utilities.NXRemotableObject):
    def __init__(self, owner: BasePart) -> None: ...
    def CreateUserDefinedObject(self, udoClass: UserDefinedObjects.UserDefinedClass) -> UserDefinedObjects.UserDefinedObject: ...
    def GetUdosOfClass(self, udoClass: UserDefinedObjects.UserDefinedClass) -> typing.List[UserDefinedObjects.UserDefinedObject]: ...
    def IsObjectLinkable(self, linkObject: TaggedObject, linkType: UserDefinedObjects.UserDefinedObject.LinkType) -> bool: ...
    def IsObjectLinkedToUserDefinedObject(self, linkObject: TaggedObject) -> bool: ...
    def GetLinksToObject(self, linkObject: TaggedObject) -> typing.List[UserDefinedObjects.UserDefinedObjectManager.LinkedUdoDefinition]: ...
    def IsObjectOwnedByUserDefinedObject(self, linkObject: TaggedObject) -> bool: ...
    def GetOwningUserDefinedObject(self, linkObject: TaggedObject) -> UserDefinedObjects.UserDefinedObject: ...
    def Tag(self) -> Tag: ...



    class UserDefinedObjectManagerLinkedUdoDefinition():
        @property
        def LinkType(self) -> UserDefinedObjects.UserDefinedObject.LinkType: ...
        @LinkType.setter
        def LinkType(self, value: UserDefinedObjects.UserDefinedObject.LinkType) -> None: ...
        @property
        def AssociatedUdo(self) -> UserDefinedObjects.UserDefinedObject: ...
        @AssociatedUdo.setter
        def AssociatedUdo(self, value: UserDefinedObjects.UserDefinedObject) -> None: ...
        @property
        def Status(self) -> UserDefinedObjects.UserDefinedObject.LinkStatus: ...
        @Status.setter
        def Status(self, value: UserDefinedObjects.UserDefinedObject.LinkStatus) -> None: ...
        def ToString(self) -> str: ...
        def __init__(self, LinkType: UserDefinedObjects.UserDefinedObject.LinkType, AssociatedUdo: UserDefinedObjects.UserDefinedObject, Status: UserDefinedObjects.UserDefinedObject.LinkStatus) -> None: ...
    

    class UserDefinedObjectManager_LinkedUdoDefinition():
        @property
        def link_type(self) -> UserDefinedObjects.UserDefinedObject.LinkType: ...
        @link_type.setter
        def link_type(self, value: UserDefinedObjects.UserDefinedObject.LinkType) -> None: ...
        @property
        def associated_udo(self) -> Tag: ...
        @associated_udo.setter
        def associated_udo(self, value: Tag) -> None: ...
        @property
        def status(self) -> UserDefinedObjects.UserDefinedObject.LinkStatus: ...
        @status.setter
        def status(self, value: UserDefinedObjects.UserDefinedObject.LinkStatus) -> None: ...
    

class UserDefinedObjectDisplayContext(TransientObject):
    def __init__(self, ptr: int) -> None: ...
    def FreeResource(self) -> None: ...
    def DisplayArc(self, center: Point3d, original: Matrix3x3, radius: float, startAngle: float, endAngle: float) -> None: ...
    def DisplayCircle(self, center: Point3d, original: Matrix3x3, radius: float, filled: bool) -> None: ...
    def DisplayPolyline(self, points: typing.List[Point3d]) -> None: ...
    def DisplayPoints(self, points: typing.List[Point3d], markerType: UserDefinedObjects.UserDefinedObjectDisplayContext.PolyMarker) -> None: ...
    def DisplayPolygon(self, points: typing.List[Point3d], filled: bool) -> None: ...
    def DisplayFacets(self, numVertices: int, numFacets: int, vertices: typing.List[Point3d], normals: typing.List[Vector3d], typeOfFacet: UserDefinedObjects.UserDefinedObjectDisplayContext.FacetType) -> None: ...
    def DisplayText(self, text: str, textCoordinates: Point3d, referencePoint: UserDefinedObjects.UserDefinedObjectDisplayContext.TextRef) -> None: ...
    def DisplayAbsoluteStandardText(self, fontIndex: int, fontStyle: str, textCoordinates: Point3d, referencePointType: UserDefinedObjects.UserDefinedObjectDisplayContext.StandardTextRef, string: str, glyphWidth: float, glyphHeight: float) -> None: ...
    def DisplayMultiLineAbsoluteStandardText(self, fontIndex: int, fontStyle: str, textCoordinates: Point3d, referencePointType: UserDefinedObjects.UserDefinedObjectDisplayContext.StandardTextRef, strings: str, glyphWidth: float, glyphHeight: float) -> None: ...
    def DisplayScreenStandardText(self, fontIndex: int, fontStyle: str, textCoordinates: Point3d, referencePointType: UserDefinedObjects.UserDefinedObjectDisplayContext.StandardTextRef, string: str, textSize: UserDefinedObjects.UserDefinedObjectDisplayContext.TextSize) -> None: ...
    def DisplayMultiLineScreenStandardText(self, fontIndex: int, fontStyle: str, textCoordinates: Point3d, referencePointType: UserDefinedObjects.UserDefinedObjectDisplayContext.StandardTextRef, strings: str, textSize: UserDefinedObjects.UserDefinedObjectDisplayContext.TextSize) -> None: ...
    def DisplayAbsoluteRotationScreenSizeStandardText(self, fontIndex: int, fontStyle: str, textCoordinates: Point3d, referencePointType: UserDefinedObjects.UserDefinedObjectDisplayContext.StandardTextRef, string: str, textSize: UserDefinedObjects.UserDefinedObjectDisplayContext.TextSize) -> None: ...
    def DisplayMultiLineAbsoluteRotationScreenSizeStandardText(self, fontIndex: int, fontStyle: str, textCoordinates: Point3d, referencePointType: UserDefinedObjects.UserDefinedObjectDisplayContext.StandardTextRef, strings: str, textSize: UserDefinedObjects.UserDefinedObjectDisplayContext.TextSize) -> None: ...
    def DisplayUnicodeMarker(self, unicodeChar: str, fontIndex: int, fontStyle: str, markerCoordinates: Point3d, markerSize: float) -> None: ...
    def GetViewMode(self, isViewModeValid: bool, viewMode: UserDefinedObjects.UserDefinedObjectDisplayContext.ViewMode, isAttenPtValid: bool, attentionPoint: Point3d, isDrawingViewOpen: bool) -> View: ...


    class ViewMode(enum.Enum):
        NotShaded= 1
        PartiallyShaded= 2
        FullyShaded= 3
        AnalysisShaded= 4
        StudioShaded= 5
    

    class TextSize(enum.Enum):
        Small= 0
        Normal= 1
        Medium= 1
        Large= 2
        NumSizes= 3
    

    class TextRef(enum.Enum):
        SystemDefault= 0
        TopLeft= 1
        TopCenter= 2
        TopRight= 3
        MiddleLeft= 4
        MiddleCenter= 5
        MiddleRight= 6
        BottomLeft= 7
        BottomCenter= 8
        BottomRight= 9
    

    class StandardTextRef(enum.Enum):
        SystemDefault= 0
        BaselineStart= 0
        BaselineCenter= 1
        BaselineEnd= 2
        TopLeft= 3
        TopCenter= 4
        TopRight= 5
        MiddleLeft= 6
        MiddleCenter= 7
        MiddleRight= 8
        BottomLeft= 9
        BottomCenter= 10
        BottomRight= 11
    

    class PolyMarker(enum.Enum):
        NoMarker= 0
        Point= 1
        Dot= 2
        Asterisk= 3
        Circle= 4
        Poundsign= 5
        X= 6
        Gridpoint= 7
        Square= 8
        TriangleMarker= 9
        Diamond= 10
        Centerline= 11
        ConsFix= 12
        ConsHorizontal= 13
        ConsVertical= 14
        ConsParallel= 15
        ConsPerpendicular= 16
        ConsTangent= 17
        ConsConcentric= 18
        ConsCoincident= 19
        ConsCollinear= 20
        ConsPointOnCurve= 21
        ConsMidpoint= 22
        ConsEqualLength= 23
        ConsEqualRadius= 24
        ConsConstantLength= 25
        ConsConstantAngle= 26
        ConsMirror= 27
        DimRadius= 28
        DimDiameter= 29
        DimParallel= 30
        DimPerpendicular= 31
        ConsSlope= 32
        ConsString= 33
        ConsUniformScaled= 34
        ConsNonUniformScaled= 35
        ConsAssocTrim= 36
        ConsAssocOffset= 37
        Disp2tResSpotWeld= 38
        Disp3tResSpotWeld= 39
        Disp4tResSpotWeld= 40
        Disp2tDcSpotWeld= 41
        Disp3tDcSpotWeld= 42
        Disp4tDcSpotWeld= 43
        Disp2tKpcSpotWeld= 44
        Disp3tKpcSpotWeld= 45
        Disp4tKpcSpotWeld= 46
        Disp2tProcSpotWeld= 47
        Disp3tProcSpotWeld= 48
        Disp4tProcSpotWeld= 49
        ArcSpotWeld= 50
        ClinchWeld= 51
        Anchor= 52
        LeftLeaderConnection= 53
        RightLeaderConnection= 54
        FilledCircle= 55
        FilledSquare= 56
        LargeFilledSquare= 57
        DatumPoint= 58
        SnappingDiamond= 59
        CircleInCircle= 60
        CircleInSquare= 61
        SquareInSquare= 62
        FilledLeftTriangle= 63
        FilledRightTriangle= 64
        FilledUpTriangle= 65
        FilledDownTriangle= 66
        FilledLeftTriangleInCircle= 67
        FilledRightTriangleInCircle= 68
        FilledUpTriangleInCircle= 69
        FilledDownTriangleInCircle= 70
        FilledLeftTriangleInSquare= 71
        FilledRightTriangleInSquare= 72
        FilledUpTriangleInSquare= 73
        FilledDownTriangleInSquare= 74
        RoundedCross= 75
        FilledDiamond= 76
        UpDownTriangles= 77
        LeftRightTriangles= 78
        SmallWheel= 79
        LargeWheel= 80
        HollowCircle= 81
        PreviewPerpendicular= 82
        PreviewHorizontal= 83
        PreviewVertical= 84
        PreviewTangent= 85
        PreviewParallel= 86
        PreviewPointOnCurve= 87
        PreviewCollinear= 88
        Ruler= 89
        Protractor= 90
        SketchNotebook= 91
        ArcEndPoint= 92
        Disp2PtArcMarker= 93
        BigAsterisk= 94
        LineInCircle= 95
        PlusInCircle= 96
        CenterOfRotation= 97
        PreviewX= 98
        PreviewY= 99
        PreviewZ= 100
        Disp2tGeneralSpotWeld= 101
        Disp3tGeneralSpotWeld= 102
        Disp4tGeneralSpotWeld= 103
        Disp2tVitalSpotWeld= 104
        Disp3tVitalSpotWeld= 105
        Disp4tVitalSpotWeld= 106
        Disp2tImportantSpotWeld= 107
        Disp3tImportantSpotWeld= 108
        Disp4tImportantSpotWeld= 109
        Disp2tSemipanelSpotWeld= 110
        Disp3tSemipanelSpotWeld= 111
        Disp4tSemipanelSpotWeld= 112
        InvalidMarker= 113
    

    class FacetType(enum.Enum):
        Triangle= 0
        Polygon= 1
        Tristrip= 2
    

class UserDefinedObject(DisplayableObject):
    def __init__(self) -> None: ...
    def GetUserDefinedObjectStatus(self) -> int: ...
    def ClearUserDefinedObjectStatus(self) -> None: ...
    def GetUserDefinedObjectFeature(self) -> Features.UserDefinedObjectFeature: ...
    @typing.overload
    def GetIntegers(self) -> int: ...
    @typing.overload
    def GetIntegers(self, offset: int, length: int) -> int: ...
    @typing.overload
    def SetIntegers(self, integers: int) -> None: ...
    @typing.overload
    def SetIntegers(self, offset: int, length: int, integers: int) -> None: ...
    def PopIntegers(self, numIntegers: int) -> int: ...
    def PushIntegers(self, integers: int) -> None: ...
    @typing.overload
    def GetDoubles(self) -> float: ...
    @typing.overload
    def GetDoubles(self, offset: int, length: int) -> float: ...
    @typing.overload
    def SetDoubles(self, doubles: float) -> None: ...
    @typing.overload
    def SetDoubles(self, offset: int, length: int, doubles: float) -> None: ...
    def PopDoubles(self, numDoubles: int) -> float: ...
    def PushDoubles(self, doubles: float) -> None: ...
    @typing.overload
    def GetStrings(self) -> str: ...
    @typing.overload
    def GetStrings(self, offset: int, length: int) -> str: ...
    @typing.overload
    def SetStrings(self, strings: str) -> None: ...
    @typing.overload
    def SetStrings(self, offset: int, length: int, strings: str) -> None: ...
    def PopStrings(self, numStrings: int) -> str: ...
    def PushStrings(self, strings: str) -> None: ...
    @typing.overload
    def GetLengths(self) -> float: ...
    @typing.overload
    def GetLengths(self, offset: int, length: int) -> float: ...
    @typing.overload
    def SetLengths(self, lengths: float) -> None: ...
    @typing.overload
    def SetLengths(self, offset: int, length: int, lengths: float) -> None: ...
    def PopLengths(self, numLengths: int) -> float: ...
    def PushLengths(self, lengths: float) -> None: ...
    @typing.overload
    def GetAreas(self) -> float: ...
    @typing.overload
    def GetAreas(self, offset: int, length: int) -> float: ...
    @typing.overload
    def SetAreas(self, areas: float) -> None: ...
    @typing.overload
    def SetAreas(self, offset: int, length: int, areas: float) -> None: ...
    def PopAreas(self, numAreas: int) -> float: ...
    def PushAreas(self, areas: float) -> None: ...
    @typing.overload
    def GetVolumes(self) -> float: ...
    @typing.overload
    def GetVolumes(self, offset: int, length: int) -> float: ...
    @typing.overload
    def SetVolumes(self, volumes: float) -> None: ...
    @typing.overload
    def SetVolumes(self, offset: int, length: int, volumes: float) -> None: ...
    def PopVolumes(self, numVolumes: int) -> float: ...
    def PushVolumes(self, volumes: float) -> None: ...
    @typing.overload
    def GetLinks(self, linkType: UserDefinedObjects.UserDefinedObject.LinkType) -> typing.List[UserDefinedObjects.UserDefinedObject.LinkDefinition]: ...
    @typing.overload
    def GetLinks(self, linkType: UserDefinedObjects.UserDefinedObject.LinkType, offset: int, length: int) -> typing.List[UserDefinedObjects.UserDefinedObject.LinkDefinition]: ...
    @typing.overload
    def SetLinks(self, linkType: UserDefinedObjects.UserDefinedObject.LinkType, links: typing.List[UserDefinedObjects.UserDefinedObject.LinkDefinition]) -> None: ...
    @typing.overload
    def SetLinks(self, linkType: UserDefinedObjects.UserDefinedObject.LinkType, offset: int, length: int, links: typing.List[UserDefinedObjects.UserDefinedObject.LinkDefinition]) -> None: ...
    def PopLinks(self, linkType: UserDefinedObjects.UserDefinedObject.LinkType, numLinks: int) -> typing.List[UserDefinedObjects.UserDefinedObject.LinkDefinition]: ...
    def PushLinks(self, linkType: UserDefinedObjects.UserDefinedObject.LinkType, links: typing.List[UserDefinedObjects.UserDefinedObject.LinkDefinition]) -> None: ...
    @property
    def ClassName(self) -> str: ...
    @ClassName.setter
    def ClassName(self, value: str) -> None: ...
    @property
    def UserDefinedClass(self) -> UserDefinedObjects.UserDefinedClass: ...
    @UserDefinedClass.setter
    def UserDefinedClass(self, value: UserDefinedObjects.UserDefinedClass) -> None: ...


    class LinkType(enum.Enum):
        Owning= 0
        Type1= 1
        Type2= 2
        Type3= 3
        Type4= 4
    

    class LinkStatus(enum.Enum):
        UpToDate= 0
        OutOfDate= 1
    

    class UserDefinedObjectLinkDefinition():
        @property
        def AssociatedObject(self) -> TaggedObject: ...
        @AssociatedObject.setter
        def AssociatedObject(self, value: TaggedObject) -> None: ...
        @property
        def Status(self) -> UserDefinedObjects.UserDefinedObject.LinkStatus: ...
        @Status.setter
        def Status(self, value: UserDefinedObjects.UserDefinedObject.LinkStatus) -> None: ...
        def ToString(self) -> str: ...
        def __init__(self, AssociatedObject: TaggedObject, Status: UserDefinedObjects.UserDefinedObject.LinkStatus) -> None: ...
    

    class UserDefinedObject_LinkDefinition():
        @property
        def associated_object(self) -> Tag: ...
        @associated_object.setter
        def associated_object(self, value: Tag) -> None: ...
        @property
        def status(self) -> UserDefinedObjects.UserDefinedObject.LinkStatus: ...
        @status.setter
        def status(self, value: UserDefinedObjects.UserDefinedObject.LinkStatus) -> None: ...
    

class UserDefinedLinkEvent(UserDefinedObjects.UserDefinedEvent):
    def __init__(self, ptr: int) -> None: ...
    def FreeResource(self) -> None: ...
    @property
    def AssociatedObject(self) -> TaggedObject: ...
    @AssociatedObject.setter
    def AssociatedObject(self, value: TaggedObject) -> None: ...
    @property
    def LinkStatus(self) -> int: ...
    @LinkStatus.setter
    def LinkStatus(self, value: int) -> None: ...
    @property
    def LinkType(self) -> int: ...
    @LinkType.setter
    def LinkType(self, value: int) -> None: ...


class UserDefinedEvent(TransientObject):
    def __init__(self, ptr: int) -> None: ...
    def FreeResource(self) -> None: ...
    @property
    def EventReason(self) -> UserDefinedObjects.UserDefinedEvent.Reason: ...
    @EventReason.setter
    def EventReason(self, value: UserDefinedObjects.UserDefinedEvent.Reason) -> None: ...
    @property
    def UserDefinedObject(self) -> UserDefinedObjects.UserDefinedObject: ...
    @UserDefinedObject.setter
    def UserDefinedObject(self, value: UserDefinedObjects.UserDefinedObject) -> None: ...


    class Reason(enum.Enum):
        Display= 0
        Delete= 1
        Update= 2
        Selection= 3
        Fit= 4
        AttentionPoint= 5
        Info= 7
        Edit= 8
        Suppress= 9
        ScreenSizeFit= 10
    

class UserDefinedDisplayEvent(UserDefinedObjects.UserDefinedEvent):
    def __init__(self, ptr: int) -> None: ...
    def FreeResource(self) -> None: ...
    @property
    def DisplayContext(self) -> UserDefinedObjects.UserDefinedObjectDisplayContext: ...
    @DisplayContext.setter
    def DisplayContext(self, value: UserDefinedObjects.UserDefinedObjectDisplayContext) -> None: ...


class UserDefinedClassManager(Utilities.NXRemotableObject):
    def __init__(self, owner: Session) -> None: ...
    def NewUserDefinedClass(self) -> UserDefinedObjects.UserDefinedClass: ...
    def CreateUserDefinedObjectClass(self, className: str, friendlyName: str) -> UserDefinedObjects.UserDefinedClass: ...
    def GetUserDefinedClassFromClassName(self, className: str) -> UserDefinedObjects.UserDefinedClass: ...
    def Tag(self) -> Tag: ...



class UserDefinedClass(TransientObject):
    def __init__(self, ptr: int) -> None: ...
    def FreeResource(self) -> None: ...
    def GetIsOccurrenceableFlag(self) -> bool: ...
    def SetIsOccurrenceableFlag(self, isOccurrenceable: bool) -> None: ...
    def AddDisplayHandler(self, displayEvent: UserDefinedObjects.UserDefinedClass.DisplayCallback) -> None: ...
    def AddSelectionHandler(self, displayEvent: UserDefinedObjects.UserDefinedClass.DisplayCallback) -> None: ...
    def AddAttentionPointHandler(self, displayEvent: UserDefinedObjects.UserDefinedClass.DisplayCallback) -> None: ...
    def AddFitHandler(self, displayEvent: UserDefinedObjects.UserDefinedClass.DisplayCallback) -> None: ...
    def AddScreenSizeFitHandler(self, displayEvent: UserDefinedObjects.UserDefinedClass.DisplayCallback) -> None: ...
    def AddUpdateHandler(self, linkEvent: UserDefinedObjects.UserDefinedClass.LinkCallback) -> None: ...
    def AddDeleteHandler(self, linkEvent: UserDefinedObjects.UserDefinedClass.LinkCallback) -> None: ...
    def AddInformationHandler(self, udoEvent: UserDefinedObjects.UserDefinedClass.GenericCallback) -> None: ...
    def AddEditHandler(self, udoEvent: UserDefinedObjects.UserDefinedClass.GenericCallback) -> None: ...
    def AddSuppressHandler(self, udoEvent: UserDefinedObjects.UserDefinedClass.GenericCallback) -> None: ...
    @property
    def AllowOwnedObjectSelectionOption(self) -> UserDefinedObjects.UserDefinedClass.AllowOwnedObjectSelection: ...
    @AllowOwnedObjectSelectionOption.setter
    def AllowOwnedObjectSelectionOption(self, value: UserDefinedObjects.UserDefinedClass.AllowOwnedObjectSelection) -> None: ...
    @property
    def AllowQueryClassFromName(self) -> UserDefinedObjects.UserDefinedClass.AllowQueryClass: ...
    @AllowQueryClassFromName.setter
    def AllowQueryClassFromName(self, value: UserDefinedObjects.UserDefinedClass.AllowQueryClass) -> None: ...
    @property
    def ClassName(self) -> str: ...
    @ClassName.setter
    def ClassName(self, value: str) -> None: ...
    @property
    def FriendlyName(self) -> str: ...
    @FriendlyName.setter
    def FriendlyName(self, value: str) -> None: ...
    @property
    def WarnUserFlag(self) -> bool: ...
    @WarnUserFlag.setter
    def WarnUserFlag(self, value: bool) -> None: ...


    class Selection(enum.Enum):
        Off= 1
        On= 2
    

    

    

    

    class AllowQueryClass(enum.Enum):
        Off= 1
        On= 2
    

    class AllowOwnedObjectSelection(enum.Enum):
        Off= 1
        On= 2
    

    

    

    

    

    

    

class NamespaceDoc(System.Object):
    def __init__(self) -> None: ...


