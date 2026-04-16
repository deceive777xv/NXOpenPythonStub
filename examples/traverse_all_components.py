from typing import List, Optional, Tuple

import NXOpen
import NXOpen.Assemblies


def _part_name(part: Optional[NXOpen.BasePart]) -> str:
    if part is None:
        return "<unknown part>"
    return part.Leaf


def _walk_components(
    component: NXOpen.Assemblies.Component, level: int = 0
) -> List[Tuple[int, NXOpen.Assemblies.Component]]:
    items: List[Tuple[int, NXOpen.Assemblies.Component]] = [(level, component)]
    for child in component.GetChildren():
        items.extend(_walk_components(child, level + 1))
    return items


def main() -> None:
    session = NXOpen.Session.GetSession()
    listing_window = session.ListingWindow
    listing_window.Open()

    work_part = session.Parts.Work
    if work_part is None:
        listing_window.WriteLine("No Work Part is currently open.")
        return

    root_component = work_part.ComponentAssembly.RootComponent
    if root_component is None:
        listing_window.WriteLine(
            f"Part '{work_part.Leaf}' is not an assembly or has no root component."
        )
        return

    listing_window.WriteLine(f"Work Part: {work_part.Leaf}")
    listing_window.WriteLine("Traversing all components...")

    components = _walk_components(root_component)
    for level, component in components:
        indent = "  " * level
        listing_window.WriteLine(
            f"{indent}- {component.DisplayName} | "
            f"JournalIdentifier={component.JournalIdentifier} | "
            f"OwningPart={_part_name(component.OwningPart)}"
        )

    listing_window.WriteLine(f"Total components: {len(components)}")


def get_unload_option(_: str) -> NXOpen.Session.LibraryUnloadOption:
    return NXOpen.Session.LibraryUnloadOption.Immediately


if __name__ == "__main__":
    main()
