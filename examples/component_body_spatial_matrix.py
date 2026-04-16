from dataclasses import dataclass
from typing import Dict, List, Tuple, cast

import NXOpen
import NXOpen.Assemblies


GRID_SIZE = (3, 3, 3)
MEASURE_ACCURACY = 0.99
EPSILON = 1.0e-9


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
    return [
        unit_collection.GetBase("Area"),
        unit_collection.GetBase("Volume"),
        unit_collection.GetBase("Mass"),
        unit_collection.GetBase("Length"),
    ]


def _direction_vectors() -> List[Tuple[str, NXOpen.Vector3d]]:
    return [
        ("+X", NXOpen.Vector3d(1.0, 0.0, 0.0)),
        ("-X", NXOpen.Vector3d(-1.0, 0.0, 0.0)),
        ("+Y", NXOpen.Vector3d(0.0, 1.0, 0.0)),
        ("-Y", NXOpen.Vector3d(0.0, -1.0, 0.0)),
        ("+Z", NXOpen.Vector3d(0.0, 0.0, 1.0)),
        ("-Z", NXOpen.Vector3d(0.0, 0.0, -1.0)),
    ]


def _create_extreme_directions(part: NXOpen.Part) -> Dict[str, NXOpen.Direction]:
    origin = NXOpen.Point3d(0.0, 0.0, 0.0)
    return {
        name: part.Directions.CreateDirection(
            origin, vector, NXOpen.SmartObject.UpdateOption.WithinModeling
        )
        for name, vector in _direction_vectors()
    }


def _collector_for_body(part: NXOpen.Part, body: NXOpen.Body) -> NXOpen.ScCollector:
    collector = part.ScCollectors.CreateCollector()
    body_rule = part.ScRuleFactory.CreateRuleBodyDumb([body], True)
    collector.ReplaceRules([body_rule], False)
    return collector


def _body_bbox(
    session: NXOpen.Session,
    part: NXOpen.Part,
    body: NXOpen.Body,
    directions: Dict[str, NXOpen.Direction],
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    collector = _collector_for_body(part, body)
    try:
        x_max = session.Measurement.GetExtremePointProperties(collector, [directions["+X"]])
        x_min = session.Measurement.GetExtremePointProperties(collector, [directions["-X"]])
        y_max = session.Measurement.GetExtremePointProperties(collector, [directions["+Y"]])
        y_min = session.Measurement.GetExtremePointProperties(collector, [directions["-Y"]])
        z_max = session.Measurement.GetExtremePointProperties(collector, [directions["+Z"]])
        z_min = session.Measurement.GetExtremePointProperties(collector, [directions["-Z"]])
    finally:
        collector.Destroy()

    bbox_min = (x_min.X, y_min.Y, z_min.Z)
    bbox_max = (x_max.X, y_max.Y, z_max.Z)
    return bbox_min, bbox_max


def _axis_cell_range(
    axis_min: float,
    axis_max: float,
    global_min: float,
    global_max: float,
    bucket_count: int,
) -> Tuple[int, int]:
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
    directions: Dict[str, NXOpen.Direction],
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

    bbox_min, bbox_max = _body_bbox(session, part, body, directions)
    bbox_center = (
        (bbox_min[0] + bbox_max[0]) / 2.0,
        (bbox_min[1] + bbox_max[1]) / 2.0,
        (bbox_min[2] + bbox_max[2]) / 2.0,
    )
    bbox_size = (
        bbox_max[0] - bbox_min[0],
        bbox_max[1] - bbox_min[1],
        bbox_max[2] - bbox_min[2],
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


def analyze_component_bodies(
    session: NXOpen.Session,
    component: NXOpen.Assemblies.Component,
    grid_size: Tuple[int, int, int] = GRID_SIZE,
) -> ComponentBodyAnalysis:
    prototype_part = _component_prototype_part(component)
    prototype_bodies = prototype_part.Bodies.ToArray()
    directions = _create_extreme_directions(prototype_part)

    body_infos = [
        _body_geometry(session, prototype_part, component, body, directions)
        for body in prototype_bodies
    ]

    if not body_infos:
        return ComponentBodyAnalysis(
            component_name=component.DisplayName,
            component_journal_identifier=component.JournalIdentifier,
            prototype_part_name=prototype_part.Leaf,
            component_bbox_min=(0.0, 0.0, 0.0),
            component_bbox_max=(0.0, 0.0, 0.0),
            matrix=SpatialBodyMatrix(grid_size, _empty_matrix(grid_size)),
            bodies=[],
        )

    component_bbox_min = (
        min(info.bbox_min[0] for info in body_infos),
        min(info.bbox_min[1] for info in body_infos),
        min(info.bbox_min[2] for info in body_infos),
    )
    component_bbox_max = (
        max(info.bbox_max[0] for info in body_infos),
        max(info.bbox_max[1] for info in body_infos),
        max(info.bbox_max[2] for info in body_infos),
    )

    matrix_cells = _empty_matrix(grid_size)
    for info in body_infos:
        x_range = _axis_cell_range(
            info.bbox_min[0], info.bbox_max[0], component_bbox_min[0], component_bbox_max[0], grid_size[0]
        )
        y_range = _axis_cell_range(
            info.bbox_min[1], info.bbox_max[1], component_bbox_min[1], component_bbox_max[1], grid_size[1]
        )
        z_range = _axis_cell_range(
            info.bbox_min[2], info.bbox_max[2], component_bbox_min[2], component_bbox_max[2], grid_size[2]
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
        matrix=SpatialBodyMatrix(grid_size, matrix_cells),
        bodies=body_infos,
    )


def build_component_spatial_matrices(
    work_part: NXOpen.Part,
    grid_size: Tuple[int, int, int] = GRID_SIZE,
) -> Dict[str, ComponentBodyAnalysis]:
    root_component = work_part.ComponentAssembly.RootComponent
    if root_component is None:
        return {}

    session = NXOpen.Session.GetSession()
    analyses: Dict[str, ComponentBodyAnalysis] = {}
    for component in _walk_components(root_component):
        analyses[component.JournalIdentifier] = analyze_component_bodies(
            session, component, grid_size
        )

    return analyses


def _format_vector(values: Tuple[float, float, float]) -> str:
    return "({0:.3f}, {1:.3f}, {2:.3f})".format(values[0], values[1], values[2])


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

    analyses = build_component_spatial_matrices(work_part, GRID_SIZE)
    listing_window.WriteLine(
        "Generated component body spatial matrices: {0}".format(len(analyses))
    )

    for analysis in analyses.values():
        listing_window.WriteLine("")
        listing_window.WriteLine(
            "Component: {0} | Prototype: {1} | Bodies: {2}".format(
                analysis.component_name,
                analysis.prototype_part_name,
                len(analysis.bodies),
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

        sample_bodies = analysis.matrix[0, 1, 1]
        listing_window.WriteLine(
            "  matrix[0, 1, 1] body count: {0}".format(len(sample_bodies))
        )
        for body_info in sample_bodies:
            listing_window.WriteLine(
                "    -> {0}".format(body_info.body_journal_identifier)
            )


def get_unload_option(_: str) -> NXOpen.Session.LibraryUnloadOption:
    return NXOpen.Session.LibraryUnloadOption.Immediately


if __name__ == "__main__":
    main()
