#!/usr/bin/env python3
import sys
import pandoc
from pandoc.types import *
from pathlib import Path
from rich.markdown import Markdown
from textual import events
from textual.app import App
from textual.widgets import Header, Footer, Placeholder, ScrollView, DirectoryTree

class Lithograph(App):

    async def on_load(self, event: events.Load) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("b", "view.toggle('outline')", "Toggle outline")
        await self.bind("o", "view.toggle('open')", "Open...")
        await self.bind("s", "save", "Save")
        await self.bind("a", "view.toggle('save_as')", "Save As...")
        await self.bind("q", "quit", "Quit")
        await self.bind("escape", "quit", "Quit")

    def get_first_header_title(self, doc, default=""):
        try:
            blocks = doc[1]
            header = blocks[0]
            title_inlines = header[2]
            return pandoc.write(title_inlines)
        except:
            return default

    async def on_mount(self, event: events.Mount) -> None:
        """Create and dock the widgets."""

        # A scrollview to contain the markdown file
        body = ScrollView(gutter=1)

        home = str(Path.home())

        await self.view.dock(Header(style="white on dark_blue", tall=False, clock=False), edge="top")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(Placeholder(), edge="left", size=30, name="outline")
        await self.view.dock(ScrollView(DirectoryTree(home)), edge="left", size=50, name="open")
        await self.view.dock(ScrollView(DirectoryTree(home)), edge="left", size=50, name="save_as")

        # Dock the body in the remaining space
        await self.view.dock(body, edge="right")

        async def get_markdown(filename: str) -> None:
            """Convert file to markdown and display"""
            pd = pandoc.read(file=filename)
            self.app.sub_title = self.get_first_header_title(pd, "")
            md = Markdown(pandoc.write(pd, format="markdown"))
            await body.update(md)

        # Load our welcome document at start up
        await self.call_later(get_markdown, "Welcome.md")


if __name__ == "__main__":
    Lithograph.run(title="Lithograph", log="lithograph.log")
