from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, cast

import NXOpen
import NXOpen.Assemblies
import NXOpen.Features


DEFAULT_GRID_SIZE = (3, 3, 3)
MAX_GRID_AXIS_CELLS = 8
SAMPLE_MATRIX_FALLBACK_INDEX = 1
MEASURE_ACCURACY = 0.99
EPSILON = 1.0e-9
# GridSize stores the resolved `(x, y, z)` matrix dimensions.
GridSize = Tuple[int, int, int]
# GridSizeOverrides maps component identifiers to manual grid-size inputs.
GridSizeOverrides = Mapping[str, Sequence[int]]

# Manual per-component grid overrides. Keys can be either
# component.JournalIdentifier or component.DisplayName.
COMPONENT_GRID_SIZE_OVERRIDES: GridSizeOverrides = {}


@dataclass
class BodyGeometryInfo:
    component_name: str
    component_journal_identifier: str
    body_journal_identifier: str
    area: float
    mass: float
    centroid: Tuple[float, float, float]
    bbox_min: Tuple[float, float, float]
    bbox_max: Tuple[float, float, float]
    bbox_center: Tuple[float, float, float]
    bbox_size: Tuple[float, float, float]
    matrix_range_min: Tuple[int, int, int]
    matrix_range_max: Tuple[int, int, int]


@dataclass
class SpatialBodyMatrix:
    shape: Tuple[int, int, int]
    cells: List[List[List[List[BodyGeometryInfo]]]]

    def __getitem__(self, index: Tuple[int, int, int]) -> List[BodyGeometryInfo]:
        ix, iy, iz = index
        return self.cells[ix][iy][iz]


@dataclass
class ComponentBodyAnalysis:
    component_name: str
    component_journal_identifier: str
    prototype_part_name: str
    component_bbox_min: Tuple[float, float, float]
    component_bbox_max: Tuple[float, float, float]
    matrix: SpatialBodyMatrix
    bodies: List[BodyGeometryInfo]


def _normalize_grid_size(grid_size: Sequence[int]) -> GridSize:
    if len(grid_size) != 3:
        raise ValueError("grid_size must contain exactly three axis values.")

    normalized = tuple(int(value) for value in grid_size)
    if any(value <= 0 for value in normalized):
        raise ValueError("grid_size axis values must be positive integers.")

    return cast(GridSize, normalized)


def _resolve_component_grid_size(
    component: NXOpen.Assemblies.Component,
    grid_size: Optional[GridSize],
    grid_size_overrides: Optional[GridSizeOverrides],
) -> Optional[GridSize]:
    if grid_size_overrides is not None:
        override = grid_size_overrides.get(component.JournalIdentifier)
        if override is None:
            override = grid_size_overrides.get(component.DisplayName)
        if override is not None:
            return _normalize_grid_size(override)

    if grid_size is None:
        return None

    return grid_size

def _deleteFeature(session: NXOpen.Session, work_part: NXOpen.Part, id):
    markId = session.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Delete")
    session.UpdateManager.ClearErrorList()
    objects = [NXOpen.TaggedObject.Null] * 1
    feature = work_part.Features.FindObject(f"{id}")
    objects[0] = feature
    nErrs1 = session.UpdateManager.AddObjectsToDeleteList(objects)
    id = session.NewestVisibleUndoMark
    nErrs2 = session.UpdateManager.DoUpdate(id)
    if markId:
        session.DeleteUndoMark(markId, "Delete Mark")

def _walk_components(
    component: NXOpen.Assemblies.Component,
) -> List[NXOpen.Assemblies.Component]:
    items = [component]
    for child in component.GetChildren():
        items.extend(_walk_components(child))
    return items


def _point_to_tuple(point: NXOpen.Point3d) -> Tuple[float, float, float]:
    return (point.X, point.Y, point.Z)


def _component_prototype_part(component: NXOpen.Assemblies.Component) -> NXOpen.Part:
    return cast(NXOpen.Part, component.Prototype)


def _mass_units(part: NXOpen.Part) -> List[NXOpen.Unit]:
    unit_collection = part.UnitCollection
    massUnits = [NXOpen.Unit.Null] * 8
    massUnits[0] = unit_collection.FindObject("MilliMeter")
    massUnits[1] = unit_collection.FindObject("SquareMilliMeter")
    massUnits[2] = unit_collection.FindObject("CubicMilliMeter")
    massUnits[3] = unit_collection.FindObject("KilogramPerCubicMilliMeter")
    massUnits[4] = unit_collection.FindObject("Kilogram")
    massUnits[5] = unit_collection.FindObject("KilogramMilliMeterSquared")
    massUnits[6] = unit_collection.FindObject("KilogramMilliMeter")
    massUnits[7] = unit_collection.FindObject("Newton")
    return massUnits


def _collector_for_body(part: NXOpen.Part, body: NXOpen.Body, builder: NXOpen.Features.ToolingBoxBuilder) -> NXOpen.ScCollector:
    bodyDumbRule = part.ScRuleFactory.CreateRuleBodyDumb([body], True)
    collector = builder.BoundedObject
    rules = [None] * 1
    rules[0] = bodyDumbRule
    collector.ReplaceRules(rules, False)
    return collector


def _extract_scalar_from_expression(expression: NXOpen.Expression) -> float:
    for getter_name in ("Value", "NumberValue", "GetValueUsingUnits"):
        getter = getattr(expression, getter_name, None)
        if getter is None:
            continue

        try:
            value = (
                getter(NXOpen.Expression.UnitsOption.Base)
                if getter_name == "GetValueUsingUnits"
                else getter
            )
        except Exception:
            continue

        if isinstance(value, (int, float)):
            return float(value)

    raise ValueError("Unable to resolve numeric value from tooling box expression.")

def _box_builder_init(part: NXOpen.Part):
    toolingBoxBuilder = part.Features.ToolingFeatureCollection.CreateToolingBoxBuilder(
        NXOpen.Features.ToolingBox.Null
    )
    toolingBoxBuilder.Type = NXOpen.Features.ToolingBoxBuilder.Types.BoundedBlock
    matrix = NXOpen.Matrix3x3()
    matrix.Xx = 1.0
    matrix.Xy = 0.0
    matrix.Xz = 0.0
    matrix.Yx = 0.0
    matrix.Yy = 1.0
    matrix.Yz = 0.0
    matrix.Zx = 0.0
    matrix.Zy = 0.0
    matrix.Zz = 1.0
    position = NXOpen.Point3d(0.0, 0.0, 0.0)
    toolingBoxBuilder.setBoxMatrixandPosition(matrix, position)
    return toolingBoxBuilder

def _body_bbox(
    part: NXOpen.Part,
    body: NXOpen.Body,
) -> Tuple[NXOpen.NXObject, Tuple[float, float, float]]:
    """Measure a body's bbox via ``CreateToolingBoxBuilder``."""
    
    builder: Optional[NXOpen.Features.ToolingBoxBuilder] = None
    try:
        builder = _box_builder_init(part)
        collector = _collector_for_body(part, body, builder)
        selections = [NXOpen.NXObject.Null] * 1
        selections[0] = body
        deselections = []
        builder.SetSelectedOccurrences(selections, deselections)
        builder.CalculateBoxSize()
        bbox = builder.Commit()
        bbox_size = (
            builder.CommitFeature().GetExpressions()[1].Value,
            builder.CommitFeature().GetExpressions()[2].Value,
            builder.CommitFeature().GetExpressions()[3].Value,
        )
        return bbox, bbox_size
    except:
        return NXOpen.NXObject.Null, (0, 0, 0)
    finally:
        if builder is not None:
            builder.Destroy()
        # collector.Destroy()


def _axis_cell_range(
    axis_min: float,
    axis_max: float,
    global_min: float,
    global_max: float,
    bucket_count: int,
) -> Tuple[int, int]:
    """Map an axis-aligned body extent onto inclusive matrix cell indices."""
    if bucket_count <= 1 or abs(global_max - global_min) < EPSILON:
        return (0, 0)

    span = global_max - global_min
    start_ratio = (axis_min - global_min) / span
    end_ratio = (axis_max - global_min) / span

    start_index = int(start_ratio * bucket_count)
    end_index = int(end_ratio * bucket_count)

    if start_index >= bucket_count:
        start_index = bucket_count - 1
    if end_index >= bucket_count:
        end_index = bucket_count - 1

    return (max(0, start_index), max(0, end_index))


def _body_geometry(
    session: NXOpen.Session,
    part: NXOpen.Part,
    component: NXOpen.Assemblies.Component,
    body: NXOpen.Body,
) -> BodyGeometryInfo:
    mass_properties = part.MeasureManager.NewMassProperties(
        _mass_units(part), MEASURE_ACCURACY, [body]
    )
    try:
        centroid = _point_to_tuple(mass_properties.Centroid)
        area = mass_properties.Area
        mass = mass_properties.Mass
    finally:
        mass_properties.Dispose()

    bbox, bbox_size = _body_bbox(part, body)
    try:
        bbox_body = part.Bodies.FindObject(bbox.JournalIdentifier)
        bbox_properties = part.MeasureManager.NewMassProperties(
            _mass_units(part), MEASURE_ACCURACY, [bbox_body]
        )
        bbox_center = _point_to_tuple(mass_properties.Centroid)
        bbox_properties.Dispose()
    except:
        bbox_center = centroid
    try:
        _deleteFeature(session, part, bbox.JournalIdentifier)
    except:
        pass
    bbox_max = (
        bbox_center[0] + 0.5*bbox_size[0],
        bbox_center[1] + 0.5*bbox_size[1],
        bbox_center[2] + 0.5*bbox_size[2],
    )
    bbox_min = (
        bbox_center[0] - 0.5*bbox_size[0],
        bbox_center[1] - 0.5*bbox_size[1],
        bbox_center[2] - 0.5*bbox_size[2],
    )

    return BodyGeometryInfo(
        component_name=component.DisplayName,
        component_journal_identifier=component.JournalIdentifier,
        body_journal_identifier=body.JournalIdentifier,
        area=area,
        mass=mass,
        centroid=centroid,
        bbox_min=bbox_min,
        bbox_max=bbox_max,
        bbox_center=bbox_center,
        bbox_size=bbox_size,
        matrix_range_min=(0, 0, 0),
        matrix_range_max=(0, 0, 0),
    )


def _empty_matrix(
    shape: Tuple[int, int, int],
) -> List[List[List[List[BodyGeometryInfo]]]]:
    x_count, y_count, z_count = shape
    return [
        [[[] for _ in range(z_count)] for _ in range(y_count)] for _ in range(x_count)
    ]


def _component_bbox(
    body_infos: List[BodyGeometryInfo],
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    return (
        (
            min(info.bbox_min[0] for info in body_infos),
            min(info.bbox_min[1] for info in body_infos),
            min(info.bbox_min[2] for info in body_infos),
        ),
        (
            max(info.bbox_max[0] for info in body_infos),
            max(info.bbox_max[1] for info in body_infos),
            max(info.bbox_max[2] for info in body_infos),
        ),
    )


def _auto_grid_size(body_infos: List[BodyGeometryInfo]) -> Tuple[int, int, int]:
    """Estimate a grid from body count and overall component span.

    The component bbox is derived from the body bboxes, normalized by the
    dominant span, then scaled so the resulting grid roughly tracks the number
    of bodies while respecting flat or degenerate geometry.

    Returns:
        A tuple of ``(x, y, z)`` grid dimensions. Empty input falls back to
        ``DEFAULT_GRID_SIZE`` and fully degenerate geometry resolves to
        ``(1, 1, 1)``.
    """
    if not body_infos:
        return DEFAULT_GRID_SIZE

    component_bbox_min, component_bbox_max = _component_bbox(body_infos)
    spans = tuple(
        max(component_bbox_max[index] - component_bbox_min[index], 0.0)
        for index in range(3)
    )
    active_axes = [index for index, span in enumerate(spans) if span >= EPSILON]
    if not active_axes:
        return (1, 1, 1)

    body_count = len(body_infos)
    axis_cap = max(1, min(MAX_GRID_AXIS_CELLS, body_count))
    max_span = max(spans[index] for index in active_axes)
    normalized_spans = [1.0, 1.0, 1.0]
    active_product = 1.0
    for index in active_axes:
        normalized_spans[index] = spans[index] / max_span
        active_product *= normalized_spans[index]

    # active_axes is bounded by the three model-space axes.
    active_axis_count = len(active_axes)
    max_cell_count = axis_cap ** active_axis_count
    target_cell_count = min(body_count, max_cell_count)
    effective_active_product = max(active_product, EPSILON)
    # active_axis_count is guaranteed to be non-zero because empty active_axes
    # returns earlier. Very small products are clamped to EPSILON so
    # flat-but-active geometry still produces a finite nth-root scale.
    nth_root_exponent = 1.0 / active_axis_count
    scale = (float(target_cell_count) / effective_active_product) ** nth_root_exponent

    axis_counts = [1, 1, 1]
    for index in active_axes:
        axis_counts[index] = max(
            1, min(axis_cap, int(normalized_spans[index] * scale))
        )

    if body_count > 1 and all(axis_counts[index] == 1 for index in active_axes):
        dominant_axis = max(active_axes, key=lambda index: spans[index])
        axis_counts[dominant_axis] = min(axis_cap, 2)

    return cast(Tuple[int, int, int], tuple(axis_counts))


def analyze_component_bodies(
    session: NXOpen.Session,
    component: NXOpen.Assemblies.Component,
    grid_size: Optional[GridSize] = None,
) -> ComponentBodyAnalysis:
    """Analyze one component and build its spatial body matrix.

    When ``grid_size`` is ``None``, the matrix shape is derived automatically
    from the collected body data; otherwise the provided grid size is used.

    Returns:
        ``ComponentBodyAnalysis`` with the component metadata, overall bounding
        box, resolved spatial matrix, and collected per-body geometry entries.
    """
    prototype_part = _component_prototype_part(component)
    partLoadStatus = session.Parts.SetWorkComponent(component, NXOpen.PartCollection.RefsetOption.Entire,
                                                   NXOpen.PartCollection.WorkComponentOption.Visible)
    part = session.parts.Work
    partLoadStatus.Dispose()
    prototype_bodies = prototype_part.Bodies

    body_infos: List[BodyGeometryInfo] = []
    for body in prototype_bodies:
        if body.IsBlanked:
            continue
        body_infos.append(
            _body_geometry(session, part, component, body)
        )

    if not body_infos:
        resolved_grid_size = grid_size or DEFAULT_GRID_SIZE
        return ComponentBodyAnalysis(
            component_name=component.DisplayName,
            component_journal_identifier=component.JournalIdentifier,
            prototype_part_name=prototype_part.Leaf,
            component_bbox_min=(0.0, 0.0, 0.0),
            component_bbox_max=(0.0, 0.0, 0.0),
            matrix=SpatialBodyMatrix(
                resolved_grid_size, _empty_matrix(resolved_grid_size)
            ),
            bodies=[],
        )

    component_bbox_min, component_bbox_max = _component_bbox(body_infos)
    resolved_grid_size = grid_size or _auto_grid_size(body_infos)

    matrix_cells = _empty_matrix(resolved_grid_size)
    for info in body_infos:
        x_range = _axis_cell_range(
            info.bbox_min[0],
            info.bbox_max[0],
            component_bbox_min[0],
            component_bbox_max[0],
            resolved_grid_size[0],
        )
        y_range = _axis_cell_range(
            info.bbox_min[1],
            info.bbox_max[1],
            component_bbox_min[1],
            component_bbox_max[1],
            resolved_grid_size[1],
        )
        z_range = _axis_cell_range(
            info.bbox_min[2],
            info.bbox_max[2],
            component_bbox_min[2],
            component_bbox_max[2],
            resolved_grid_size[2],
        )

        info.matrix_range_min = (x_range[0], y_range[0], z_range[0])
        info.matrix_range_max = (x_range[1], y_range[1], z_range[1])

        for ix in range(x_range[0], x_range[1] + 1):
            for iy in range(y_range[0], y_range[1] + 1):
                for iz in range(z_range[0], z_range[1] + 1):
                    matrix_cells[ix][iy][iz].append(info)

    return ComponentBodyAnalysis(
        component_name=component.DisplayName,
        component_journal_identifier=component.JournalIdentifier,
        prototype_part_name=prototype_part.Leaf,
        component_bbox_min=component_bbox_min,
        component_bbox_max=component_bbox_max,
        matrix=SpatialBodyMatrix(resolved_grid_size, matrix_cells),
        bodies=body_infos,
    )


def build_component_spatial_matrices(
    work_part: NXOpen.Part,
    grid_size: Optional[GridSize] = None,
    grid_size_overrides: Optional[GridSizeOverrides] = None,
) -> Dict[str, ComponentBodyAnalysis]:
    """Build component analyses keyed by component journal identifier.

    When ``grid_size`` is ``None``, each component resolves its own automatic
    grid size from its body data; otherwise the supplied override is applied.
    ``grid_size_overrides`` can be used to manually set different grid sizes
    for specific components by journal identifier or display name.

    Returns:
        A dictionary keyed by component journal identifier with the
        corresponding ``ComponentBodyAnalysis`` results.
    """
    root_component = work_part.ComponentAssembly.RootComponent
    if root_component is None:
        return {}

    session = NXOpen.Session.GetSession()
    analyses: Dict[str, ComponentBodyAnalysis] = {}
    for component in _walk_components(root_component):
        if component.IsBlanked:
            continue
        resolved_grid_size = _resolve_component_grid_size(
            component, grid_size, grid_size_overrides
        )
        analyses[component.JournalIdentifier] = analyze_component_bodies(
            session, component, resolved_grid_size
        )

    return analyses


def _format_vector(values: Tuple[float, float, float]) -> str:
    return "({0:.3f}, {1:.3f}, {2:.3f})".format(values[0], values[1], values[2])


def _sample_matrix_index(shape: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Return a stable sample cell on the first X slice and a nearby Y/Z cell."""
    return (
        0,
        min(SAMPLE_MATRIX_FALLBACK_INDEX, shape[1] - 1),
        min(SAMPLE_MATRIX_FALLBACK_INDEX, shape[2] - 1),
    )


def main() -> None:
    session = NXOpen.Session.GetSession()
    listing_window = session.ListingWindow
    listing_window.Open()

    work_part = session.Parts.Work
    if work_part is None:
        listing_window.WriteLine("No Work Part is currently open.")
        return

    if work_part.ComponentAssembly.RootComponent is None:
        listing_window.WriteLine(
            "The current Work Part is not an assembly or has no root component."
        )
        return

    analyses = build_component_spatial_matrices(
        work_part, grid_size_overrides=COMPONENT_GRID_SIZE_OVERRIDES
    )

    partLoadStatus = session.Parts.SetWorkComponent(NXOpen.Assemblies.Component.Null, NXOpen.PartCollection.RefsetOption.Entire,
                                                   NXOpen.PartCollection.WorkComponentOption.Visible)
    part = session.parts.Work
    partLoadStatus.Dispose()
    
    listing_window.WriteLine(
        "Generated component body spatial matrices: {0}".format(len(analyses))
    )

    for analysis in analyses.values():
        listing_window.WriteLine("")
        listing_window.WriteLine(
            "Component: {0} | Prototype: {1} | Bodies: {2} | Grid: {3}".format(
                analysis.component_name,
                analysis.prototype_part_name,
                len(analysis.bodies),
                analysis.matrix.shape,
            )
        )
        listing_window.WriteLine(
            "Component BBox min={0}, max={1}".format(
                _format_vector(analysis.component_bbox_min),
                _format_vector(analysis.component_bbox_max),
            )
        )

        for body_info in analysis.bodies:
            listing_window.WriteLine(
                "  Body: {0} | Area={1:.6f} | Mass={2:.6f} | Centroid={3}".format(
                    body_info.body_journal_identifier,
                    body_info.area,
                    body_info.mass,
                    _format_vector(body_info.centroid),
                )
            )
            listing_window.WriteLine(
                "    BBox center={0} | size={1} | matrix-range={2} -> {3}".format(
                    _format_vector(body_info.bbox_center),
                    _format_vector(body_info.bbox_size),
                    body_info.matrix_range_min,
                    body_info.matrix_range_max,
                )
            )

        sample_index = _sample_matrix_index(analysis.matrix.shape)
        sample_bodies = analysis.matrix[sample_index]
        listing_window.WriteLine(
            "  matrix{0} body count: {1}".format(sample_index, len(sample_bodies))
        )
        for body_info in sample_bodies:
            listing_window.WriteLine(
                "    -> {0}".format(body_info.body_journal_identifier)
            )


def get_unload_option(_: str) -> NXOpen.Session.LibraryUnloadOption:
    return NXOpen.Session.LibraryUnloadOption.Immediately


if __name__ == "__main__":
    main()
