#!/usr/bin/env python3
#
# This file is part of Lithograph, a distraction free writing tool.
#
# Copyright (c) 2022 Mike Sheldon <mike@mikeasoft.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys
import pandoc
from pandoc.types import *
from pathlib import Path
from rich.markdown import Markdown
from textual import events
from textual.app import App
from textual.widgets import Placeholder, ScrollView, DirectoryTree
from litho_header import LithoHeader
from litho_footer import LithoFooter

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

        document = None
        if len(sys.argv) > 1:
            document = sys.argv[1]

        self.outline = Placeholder(name="Outline")
        self.open_tree = ScrollView(DirectoryTree(home))
        self.save_as_tree = ScrollView(DirectoryTree(home))
        self.footer = LithoFooter()

        await self.view.dock(LithoHeader(style="white on dark_blue", tall=False, clock=False), edge="top")
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.outline, edge="left", size=30, name="outline")
        await self.view.dock(self.open_tree, edge="left", size=50, name="open")
        await self.view.dock(self.save_as_tree, edge="left", size=50, name="save_as")

        self.outline.visible = False
        self.save_as_tree.visible = False

        if document is not None:
            self.open_tree.visible = False

        # Dock the body in the remaining space
        await self.view.dock(body, edge="right")

        async def get_markdown(filename: str) -> None:
            """Convert file to markdown and display"""
            pd = pandoc.read(file=filename)
            self.app.sub_title = self.get_first_header_title(pd, filename)
            md = Markdown(pandoc.write(pd, format="markdown"))
            await body.update(md)

        if document is not None:
            # Load user specified document
            await self.call_later(get_markdown, document)
        else:
            # Load our welcome document at start up
            await self.call_later(get_markdown, "Welcome.md")


if __name__ == "__main__":
    Lithograph.run(title="Lithograph", log="lithograph.log")
