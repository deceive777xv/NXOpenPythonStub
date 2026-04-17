from typing import Optional, cast

import NXOpen
import NXOpen.Assemblies


# Set these values to the target component/body JournalIdentifier strings
# before running the script.
user_component_journal_identifier = ""
user_body_journal_identifier = ""


def _walk_components(
    component: NXOpen.Assemblies.Component,
) -> list[NXOpen.Assemblies.Component]:
    items = [component]
    for child in component.GetChildren():
        items.extend(_walk_components(child))
    return items


def _find_component(
    root_component: NXOpen.Assemblies.Component, journal_identifier: str
) -> Optional[NXOpen.Assemblies.Component]:
    for component in _walk_components(root_component):
        if component.JournalIdentifier == journal_identifier:
            return component
    return None


def _find_body_occurrence(
    component: NXOpen.Assemblies.Component, body_journal_identifier: str
) -> Optional[NXOpen.DisplayableObject]:
    prototype_part = cast(NXOpen.Part, component.Prototype)

    try:
        prototype_body = prototype_part.Bodies.FindObject(body_journal_identifier)
    except NXOpen.NXException:
        return None

    fallback_body = cast(NXOpen.DisplayableObject, prototype_body)

    try:
        body_occurrence = component.FindOccurrence(prototype_body)
    except NXOpen.NXException:
        return fallback_body

    if body_occurrence in (None, NXOpen.NXObject.Null):
        return fallback_body

    return cast(NXOpen.DisplayableObject, body_occurrence)


def main() -> None:
    session = NXOpen.Session.GetSession()
    listing_window = session.ListingWindow
    listing_window.Open()

    if not user_component_journal_identifier or not user_body_journal_identifier:
        listing_window.WriteLine(
            "Please set user_component_journal_identifier and "
            "user_body_journal_identifier at the top of the script before running."
        )
        return

    work_part = session.Parts.Work
    if work_part is None:
        listing_window.WriteLine("No Work Part is currently open.")
        return

    root_component = work_part.ComponentAssembly.RootComponent
    if root_component is None:
        listing_window.WriteLine(
            "The current Work Part is not an assembly or has no root component."
        )
        return

    component = _find_component(root_component, user_component_journal_identifier)
    if component is None:
        listing_window.WriteLine(
            "Component not found: {0}".format(user_component_journal_identifier)
        )
        return

    body = _find_body_occurrence(component, user_body_journal_identifier)
    if body is None:
        listing_window.WriteLine(
            "Body not found: {0} in component {1}".format(
                user_body_journal_identifier, user_component_journal_identifier
            )
        )
        return

    if body.IsBlanked:
        body.Unblank()

    body.Highlight()
    body.RedisplayObject()

    listing_window.WriteLine("Component: {0}".format(component.DisplayName))
    listing_window.WriteLine(
        "Component JournalIdentifier: {0}".format(component.JournalIdentifier)
    )
    listing_window.WriteLine("Body JournalIdentifier: {0}".format(user_body_journal_identifier))
    listing_window.WriteLine("The target body has been highlighted.")


def get_unload_option(arg: str) -> NXOpen.Session.LibraryUnloadOption:
    return NXOpen.Session.LibraryUnloadOption.Immediately


if __name__ == "__main__":
    main()
