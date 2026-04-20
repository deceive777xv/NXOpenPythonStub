from __future__ import annotations

import os
from typing import Optional, cast

import NXOpen
import NXOpen.Assemblies
import NXOpen.BlockStyler


DLX_FILE = os.path.join(
    os.path.dirname(__file__), "select_component_and_body_journal_identifier.dlx"
)
BODY_SELECT_BLOCK_NAME = "body_select"


def _prototype_body(body: NXOpen.Body) -> NXOpen.Body:
    prototype = cast(NXOpen.Body, body.Prototype)
    if prototype == NXOpen.NXObject.Null:
        return body
    return prototype


def _body_from_selection(
    selected_objects: list[NXOpen.TaggedObject],
) -> Optional[NXOpen.Body]:
    if not selected_objects:
        return None

    candidate = selected_objects[0]
    if isinstance(candidate, NXOpen.Body):
        return candidate

    return None


def _resolve_component_body_identifier(
    body: NXOpen.Body,
) -> tuple[Optional[NXOpen.Assemblies.Component], NXOpen.Body, Optional[NXOpen.Body]]:
    component = body.OwningComponent
    prototype_body = _prototype_body(body)

    if component is None or component == NXOpen.NXObject.Null:
        return None, prototype_body, None

    body_occurrence = cast(NXOpen.Body, component.FindOccurrence(prototype_body))
    if body_occurrence == NXOpen.NXObject.Null:
        return component, prototype_body, None

    return component, prototype_body, body_occurrence


class BodyIdentifierDialog:
    def __init__(self) -> None:
        self._session = NXOpen.Session.GetSession()
        self._ui = NXOpen.UI.GetUI()
        self._dialog = self._ui.CreateDialog(DLX_FILE)
        self._body_select: Optional[NXOpen.BlockStyler.SelectObject] = None

        self._dialog.AddInitializeHandler(self.initialize_cb)
        self._dialog.AddApplyHandler(self.apply_cb)
        self._dialog.AddOkHandler(self.ok_cb)

    def show(self) -> int:
        return int(self._dialog.Show())

    def dispose(self) -> None:
        if self._dialog is not None:
            self._dialog.FreeResource()

    def initialize_cb(self) -> None:
        top_block = self._dialog.TopBlock
        self._body_select = cast(
            NXOpen.BlockStyler.SelectObject, top_block.FindBlock(BODY_SELECT_BLOCK_NAME)
        )
        self._body_select.ResetFilter()
        self._body_select.AddFilter(NXOpen.BlockStyler.SelectObject.FilterType.SolidBodies)
        self._body_select.AddFilter(NXOpen.BlockStyler.SelectObject.FilterType.SheetBodies)

    def apply_cb(self) -> int:
        listing_window = self._session.ListingWindow
        listing_window.Open()

        if self._body_select is None:
            listing_window.WriteLine("SelectObject block was not initialized.")
            return 0

        body = _body_from_selection(self._body_select.GetSelectedObjects())
        if body is None:
            listing_window.WriteLine("Please select one body occurrence in the assembly.")
            return 0

        component, prototype_body, body_occurrence = _resolve_component_body_identifier(
            body
        )
        listing_window.WriteLine("Selected body occurrence JournalIdentifier:")
        listing_window.WriteLine("  {0}".format(body.JournalIdentifier))

        if component is None:
            listing_window.WriteLine(
                "The selected body is not owned by an assembly component."
            )
            listing_window.WriteLine(
                "Prototype/work-part body JournalIdentifier: {0}".format(
                    prototype_body.JournalIdentifier
                )
            )
            return 0

        listing_window.WriteLine("Owning component: {0}".format(component.DisplayName))
        listing_window.WriteLine(
            "Owning component JournalIdentifier: {0}".format(
                component.JournalIdentifier
            )
        )
        listing_window.WriteLine(
            "Body JournalIdentifier inside that component: {0}".format(
                prototype_body.JournalIdentifier
            )
        )

        if body_occurrence is not None:
            listing_window.WriteLine(
                "Recovered occurrence matches selected body: {0}".format(
                    body_occurrence.Tag == body.Tag
                )
            )

        listing_window.WriteLine(
            "Use the pair (component.JournalIdentifier, prototype_body.JournalIdentifier) "
            "to identify the body occurrence."
        )
        return 0

    def ok_cb(self) -> int:
        return self.apply_cb()


def main() -> None:
    dialog = BodyIdentifierDialog()
    try:
        dialog.show()
    finally:
        dialog.dispose()


def get_unload_option(arg: str) -> NXOpen.Session.LibraryUnloadOption:
    return NXOpen.Session.LibraryUnloadOption.Immediately


if __name__ == "__main__":
    main()
