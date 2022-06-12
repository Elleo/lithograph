from __future__ import annotations

from rich.text import Text
import rich.repr

from textual.widgets import Footer

@rich.repr.auto
class LithoFooter(Footer):

    def make_key_text(self) -> Text:
        """Create text containing all the keys."""
        text = Text(
            style="white on dark_bue",
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (f" {key_display} ", "reverse" if hovered else "default on default"),
                f" {binding.description} ",
                meta={"@click": f"app.press('{binding.key}')", "key": binding.key},
            )
            text.append_text(key_text)
        return text
