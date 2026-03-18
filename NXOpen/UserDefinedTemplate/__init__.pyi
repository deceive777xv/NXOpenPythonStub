from ...NXOpen import *

import typing
import enum

class RootNode(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    @property
    def TemplateType(self) -> int: ...
    @TemplateType.setter
    def TemplateType(self, value: int) -> None: ...


class NamespaceDoc(System.Object):
    def __init__(self) -> None: ...


class ItemNodeTab(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...


class ItemNodeString(UserDefinedTemplate.ItemNodeExpression):
    def __init__(self) -> None: ...


class ItemNodeSketch(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    def SetSketch(self, sketch: NXObject) -> None: ...


class ItemNodeSeparator(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...


class ItemNodeRouting(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...


class ItemNodeReference(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    def SetReferenceObject(self, object: NXObject) -> None: ...
    def SetReferenceObjectName(self, name: str) -> None: ...
    def SetReferenceType(self, name: str) -> None: ...
    def SetOwningObject(self, object: NXObject) -> None: ...


class ItemNodePosition(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...


class ItemNodePoint(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    def SetPoint(self, point: NXObject) -> None: ...


class ItemNodeNumber(UserDefinedTemplate.ItemNodeExpression):
    def __init__(self) -> None: ...


class ItemNodeLayer(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    def UpdateLayerSetting(self, categoryName: str) -> None: ...


class ItemNodeLabel(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...


class ItemNodeInteger(UserDefinedTemplate.ItemNodeExpression):
    def __init__(self) -> None: ...


class ItemNodeGroup(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    @property
    def Expanded(self) -> bool: ...
    @Expanded.setter
    def Expanded(self, value: bool) -> None: ...


class ItemNodeGeometry(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    def SetWaveLink(self, waveLink: NXObject) -> None: ...


class ItemNodeFeatureBoolean(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...


class ItemNodeFamily(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    def CreateFamilyData(self) -> None: ...
    def UpdateFamilyData(self) -> None: ...
    def FreeFamilyData(self) -> None: ...
    def RefineFamilyMember(self, instanceIndex: int, name: str, memberIndex: int) -> None: ...


class ItemNodeExtract(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    def SetExtract(self, extract: NXObject) -> None: ...


class ItemNodeExpression(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    def SetReferenceExpression(self, expression: Expression) -> None: ...


class ItemNodeExplode(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...


class ItemNodeButton(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...


class ItemNodeBoolean(UserDefinedTemplate.ItemNodeExpression):
    def __init__(self) -> None: ...


class ItemNodeBody(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...
    def SetEntityObject(self, entity: NXObject) -> None: ...


class ItemNodeArrangement(UserDefinedTemplate.ConfigurableObject):
    def __init__(self) -> None: ...


class InstantiationBuilder(Builder):
    def __init__(self) -> None: ...
    def LoadAuthoringPart(self, authoringPartName: str) -> Part: ...
    def GetExpressions(self) -> typing.List[Expression]: ...
    def GetMatchedExpression(self, originalExpression: Expression, canBeEdited: bool) -> Expression: ...
    def GetReferences(self) -> typing.List[NXObject]: ...
    def GetMatchedReference(self, originalReference: NXObject, isDirectionFlipped: bool) -> NXObject: ...
    def SetMatchedReference(self, originalReference: NXObject, matchedReference: NXObject, flipDirection: bool) -> None: ...
    @property
    def BooleanFlag(self) -> UserDefinedTemplate.InstantiationBuilder.JaUserdefinedtemplateinstantiationBooleanOption: ...
    @BooleanFlag.setter
    def BooleanFlag(self, value: UserDefinedTemplate.InstantiationBuilder.JaUserdefinedtemplateinstantiationBooleanOption) -> None: ...
    @property
    def BooleanTarget(self) -> NXObject: ...
    @BooleanTarget.setter
    def BooleanTarget(self, value: NXObject) -> None: ...
    @property
    def Expandable(self) -> bool: ...
    @Expandable.setter
    def Expandable(self, value: bool) -> None: ...
    @property
    def ExplodeFlag(self) -> UserDefinedTemplate.InstantiationBuilder.JaUserdefinedtemplateinstantiationExplodeOption: ...
    @ExplodeFlag.setter
    def ExplodeFlag(self, value: UserDefinedTemplate.InstantiationBuilder.JaUserdefinedtemplateinstantiationExplodeOption) -> None: ...
    @property
    def Explosion(self) -> bool: ...
    @Explosion.setter
    def Explosion(self, value: bool) -> None: ...
    @property
    def LayerNumber(self) -> int: ...
    @LayerNumber.setter
    def LayerNumber(self, value: int) -> None: ...
    @property
    def LayerOption(self) -> UserDefinedTemplate.InstantiationBuilder.JaUserdefinedtemplateinstantiationLayerOption: ...
    @LayerOption.setter
    def LayerOption(self, value: UserDefinedTemplate.InstantiationBuilder.JaUserdefinedtemplateinstantiationLayerOption) -> None: ...


    class JaUserdefinedtemplateinstantiationLayerOption(enum.Enum):
        Work= 0
        Original= 1
        Specify= 2
    

    class JaUserdefinedtemplateinstantiationExplodeOption(enum.Enum):
        NotAllowed= -1
        None_= 0
        FeatureGroup= 1
        DesignGroup= 2
    

    class JaUserdefinedtemplateinstantiationBooleanOption(enum.Enum):
        NotAllowed= -1
        None_= 0
        Unite= 1
        Subtract= 2
        UserDefined= 3
    

class Instantiation(NXObject):
    def __init__(self) -> None: ...
    def GetFeature(self) -> Features.Feature: ...
    def GetExpressions(self) -> typing.List[Expression]: ...
    def GetPmis(self) -> typing.List[Annotations.Annotation]: ...
    def GetObjects(self) -> typing.List[NXObject]: ...


class DefinitionBuilder(Builder):
    def __init__(self) -> None: ...
    def SetObjects(self, objects: typing.List[NXObject]) -> None: ...
    def GetObjects(self) -> typing.List[NXObject]: ...
    def AddObjects(self, objects: typing.List[NXObject]) -> None: ...
    def RemoveObjects(self, objects: typing.List[NXObject]) -> None: ...
    def SetObjectVisibility(self, entity: int, isVisble: bool) -> None: ...
    def AddEditableExpressions(self, expressions: typing.List[Expression]) -> None: ...
    def RemoveEditableExpressions(self, expressions: typing.List[Expression]) -> None: ...
    def GetEditableExpressions(self) -> typing.List[Expression]: ...
    def GetReferences(self) -> typing.List[NXObject]: ...
    @property
    def ConfigurableObject(self) -> UserDefinedTemplate.ConfigurableObject: ...
    @ConfigurableObject.setter
    def ConfigurableObject(self, value: UserDefinedTemplate.ConfigurableObject) -> None: ...


class Definition(NXObject):
    def __init__(self) -> None: ...
    def GetObjects(self) -> typing.List[NXObject]: ...


class ConfigurationManager(Utilities.NXRemotableObject):
    def __init__(self, owner: Part) -> None: ...
    def CreateRootNode(self, templateType: UserDefinedTemplate.ConfigurationManager.TemplateType) -> UserDefinedTemplate.ConfigurableObject: ...
    def CreateItemNode(self, itemType: UserDefinedTemplate.ConfigurationManager.ItemType) -> UserDefinedTemplate.ConfigurableObject: ...
    def DragDropNode(self, rootNode: UserDefinedTemplate.ConfigurableObject, sourceNode: UserDefinedTemplate.ConfigurableObject, targetNode: UserDefinedTemplate.ConfigurableObject) -> None: ...
    def RemoveItemNode(self, targetNode: UserDefinedTemplate.ConfigurableObject) -> None: ...
    def MoveItemNode(self, moveType: UserDefinedTemplate.ConfigurationManager.MoveType, sourceNode: UserDefinedTemplate.ConfigurableObject) -> None: ...
    def Tag(self) -> Tag: ...



    class TemplateType(enum.Enum):
        None_= 0
        Pts= 1
        Fts= 2
    

    class MoveType(enum.Enum):
        Up= 0
        Down= 1
        Out= 2
    

    class ItemType(enum.Enum):
        Group= 0
        Tab= 1
        Button= 2
        Label= 3
        Separator= 4
        Layer= 5
        Routing= 6
        Arrangement= 7
        Family= 8
        Number= 9
        String= 10
        Boolean= 11
        Integer= 12
        Reference= 13
        Body= 14
        Sketch= 15
        Geometry= 16
        Extract= 17
        Point= 18
        Position= 19
    

class ConfigurableObject(NXObject):
    def __init__(self) -> None: ...
    def SetParameter(self, propertyId: UserDefinedTemplate.ConfigurableObject.PropertyId, value: str) -> None: ...
    def SetLogicalParameter(self, propertyId: UserDefinedTemplate.ConfigurableObject.PropertyId, value: bool) -> None: ...
    def SetMenuParameter(self, propertyId: UserDefinedTemplate.ConfigurableObject.PropertyId, menuIndex: int) -> None: ...
    def SetChoiceParameter(self, propertyId: UserDefinedTemplate.ConfigurableObject.PropertyId, choices: str) -> None: ...
    def SetTagParameter(self, propertyId: UserDefinedTemplate.ConfigurableObject.PropertyId, referenceObject: NXObject) -> None: ...
    def GetParameter(self, propertyId: UserDefinedTemplate.ConfigurableObject.PropertyId) -> str: ...
    def GetLogicalParameter(self, propertyId: UserDefinedTemplate.ConfigurableObject.PropertyId) -> bool: ...
    def GetMenuParameter(self, propertyId: UserDefinedTemplate.ConfigurableObject.PropertyId) -> int: ...
    def Update(self, updateType: UserDefinedTemplate.ConfigurableObject.UpdateType) -> None: ...


    class UpdateType(enum.Enum):
        None_= 0
        ExternalChange= 1
        PartFamily= 2
    

    class PropertyId(enum.Enum):
        Title= 0
        Cue= 1
        Helpcontext= 2
        TemplateName= 3
        TemplateLocation= 4
        AllowExplode= 5
        AllowBoolean= 6
        Expanded= 7
        Name= 8
        FileSystem= 9
        Bitmap= 10
        ItemRevision= 11
        Dataset= 12
        Update= 13
        DisplayStyle= 14
        Values= 15
        TooltipImages= 16
        ReturnType= 17
        OriginPoint= 18
        Vector= 19
        XVector= 20
        ZVector= 21
        Radius= 22
        Positive= 23
        MinValue= 24
        MinInclusive= 25
        MaxValue= 26
        MaxInclusive= 27
        Increment= 28
        DecimalPlaces= 29
        ListExpression= 30
        AllowDynamic= 31
        CheckMismatch= 32
        EnsureValue= 33
        ButtonAction= 34
        DatasetType= 35
        HelpUrl= 36
        Tooltip= 37
        UseAlert= 38
        ExternalLibrary= 39
        ClassName= 40
        MethodName= 41
        Parameters= 42
        VisualRules= 43
        JournalFile= 44
        VisEnabled= 45
        VisType= 46
        VisObject= 47
        VisComparison= 48
        VisValue= 49
        SensEnabled= 50
        SensType= 51
        SensObject= 52
        SensComparison= 53
        SensValue= 54
        TooltipText= 55
        BooleanOrder= 56
        ReferenceBehavior= 57
        ContentVisibility= 58
        Rollback= 59
        Optional= 60
        Target= 61
        ShowHandle= 62
        SelectionScope= 63
        Hd3d= 64
        Hd3dTitle1= 65
        Hd3dUrl1= 66
        Hd3dIcon1= 67
        Hd3dDescription1= 68
        Hd3dAnchor1= 69
        Hd3dTitle2= 70
        Hd3dUrl2= 71
        Hd3dIcon2= 72
        Hd3dDescription2= 73
        Hd3dAnchor2= 74
        Hd3dTitle3= 75
        Hd3dUrl3= 76
        Hd3dIcon3= 77
        Hd3dDescription3= 78
        Hd3dAnchor3= 79
        FreezeWaveUpdate= 80
        EnableCopyClone= 81
        RunRelinker= 82
        RunPartFamilyUpdate= 83
        ShowAssemblyInstances= 84
        UseDropPosition= 85
        LaunchRedefineConstraints= 86
        AllowQuickAccess= 87
        DefaultRefSet= 88
        ActiveRefSet= 89
        ActiveView= 90
        CheckTinyObjects= 91
        CheckMisalignedObjects= 92
        CheckBodyDataStructures= 93
        CheckBodyConsistency= 94
        CheckFaceFaceIntersection= 95
        CheckFaceSmoothness= 96
        CheckFaceSelfIntersection= 97
        CheckFaceSpikesCuts= 98
        CheckEdgeSmoothness= 99
        CheckEdgeTolerances= 100
        CheckOrphanBodies= 101
        CheckInterpartWaveLinks= 102
        CheckInterpartExpressionStatus= 103
        RelinkUnbroken= 104
        IncludeSuppressed= 105
        FaceCurveDirection= 106
        SourceScope= 107
        TargetScope= 108
        RelinkOption= 109
        BreakWaveLinksAfterUpdate= 110
        BreakExpLinksAfterUpdate= 111
        CheckTinyObjectsTol= 112
        CheckTinyObjectsLevel= 113
        CheckTinyObjectsDesc= 114
        CheckMisalignedObjectsTol= 115
        CheckMisalignedObjectsLevel= 116
        CheckMisalignedObjectsDesc= 117
        CheckBodyDataStructuresLevel= 118
        CheckBodyDataStructuresDesc= 119
        CheckBodyConsistencyLevel= 120
        CheckBodyConsistencyDesc= 121
        CheckFaceFaceIntersectionLevel= 122
        CheckFaceFaceIntersectionDesc= 123
        CheckFaceSmoothnessLevel= 124
        CheckFaceSmoothnessDesc= 125
        CheckFaceSelfIntersectionLevel= 126
        CheckFaceSelfIntersectionDesc= 127
        CheckFaceSpikesCutsTol= 128
        CheckFaceSpikesCutsLevel= 129
        CheckFaceSpikesCutsDesc= 130
        CheckEdgeSmoothnessTol= 131
        CheckEdgeSmoothnessLevel= 132
        CheckEdgeSmoothnessDesc= 133
        CheckEdgeTolerancesTol= 134
        CheckEdgeTolerancesLevel= 135
        CheckEdgeTolerancesDesc= 136
        CheckOrphanBodiesRefset= 137
        CheckOrphanBodiesLevel= 138
        CheckOrphanBodiesDesc= 139
        CheckInterpartWaveLinksStatus= 140
        CheckInterpartWaveLinksLevel= 141
        CheckInterpartWaveLinksDesc= 142
        CheckInterpartExpressionStatusLevel= 143
        CheckInterpartExpressionStatusDesc= 144
        LayerCategories= 145
        Preview= 146
        Positioning= 147
        ExternalState= 148
        TemplateOrder= 149
    

class Collection(TaggedObjectCollection):
    def EnumerateMoveNext(self, currentTag: Tag, state: bytes) -> int: ...
    def ToArray(self) -> typing.List[TaggedObject]: ...
    @typing.overload
    def __init__(self, owner: Part) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def CreateInstantiationBuilder(self, userDefinedTemplateInstantiation: UserDefinedTemplate.Instantiation) -> UserDefinedTemplate.InstantiationBuilder: ...
    def FindObject(self, journalIdentifier: str) -> TaggedObject: ...
    def CreateDefinitionBuilder(self, userDefinedTemplateDefinition: UserDefinedTemplate.Definition) -> UserDefinedTemplate.DefinitionBuilder: ...
    def FindInstantiationObject(self, journalIdentifier: str) -> UserDefinedTemplate.Instantiation: ...
    def FindDefinitionObject(self, journalIdentifier: str) -> UserDefinedTemplate.Definition: ...
    def CreatePartAttribute(self, categoryAlias: str, titleAlias: str, value: str, units: str, type: str) -> TaggedObject: ...
    def Tag(self) -> Tag: ...



