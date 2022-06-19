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
from rich.console import RenderableType
from textual import events
from textual.app import App
from textual.widget import Widget
from textual.widgets import Placeholder, FileClick, Header, Footer, Static
from textual.widgets.text_input import TextArea
from litho_header import LithoHeader
from litho_footer import LithoFooter
from litho_directory_tree import LithoDirectoryTree

ACCEPTED_EXTENSIONS = "^(.*\.(txt|docx|odt|md|htm|html|epub|json|latex|tex|xml|opml|rst|log)|[^\.]*)$"


class Lithograph(App, css_path="lithograph.css"):

    dark = True

    def on_load(self, event: events.Load) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        self.bind("b", "toggle_class('#outline', '-active')", "Toggle outline")
        self.bind("c", "toggle_clock", "Toggle clock")
        self.bind("f", "toggle_fullscreen", "Toggle Fullscreen")
        self.bind("o", "toggle_class('#open', '-active')", "Open...")
        self.bind("s", "save", "Save")
        self.bind("a", "toggle_class('#saveas', '-active')", "Save As...")
        self.bind("q", "quit", "Quit")

    def get_first_header_title(self, doc, default=""):
        try:
            blocks = doc[1]
            header = blocks[0]
            title_inlines = header[2]
            return pandoc.write(title_inlines)
        except:
            return default

    async def action_toggle_clock(self) -> None:
        self.header.clock = not self.header.clock

    async def action_toggle_fullscreen(self) -> None:
        if self.header.visible:
            self.header.stored_visibility = self.header.visible
            self.footer.stored_visibility = self.footer.visible
            self.outline.stored_visibility = self.outline.visible
            self.open_tree.stored_visibility = self.open_tree.visible
            self.save_as_tree.stored_visibility = self.save_as_tree.visible
            self.header.visible = False
            self.footer.visible = False
            self.outline.visible = False
            self.open_tree.visible = False
            self.save_as_tree.visible = False
        else:
            self.header.visible = self.header.stored_visibility
            self.footer.visible = self.footer.stored_visibility
            self.outline.visible = self.outline.stored_visibility
            self.open_tree.visible = self.open_tree.stored_visibility
            self.save_as_tree.visible = self.save_as_tree.stored_visibility

    async def handle_file_click(self, message: FileClick) -> None:
        """A message sent by the directory tree when a file is clicked."""
        if message.sender.name == "open_tree":
            await self.load_document(message.path)

    async def on_mount(self, event: events.Mount) -> None:
        """Create and dock the widgets."""

        self.body = Static()

        home = str(Path.home())

        document = None
        if len(sys.argv) > 1:
            document = sys.argv[1]

        self.outline = Placeholder(name="Outline", classes="outline")
        self.open_tree = LithoDirectoryTree(home, name="open_tree", classes="open", file_filter=ACCEPTED_EXTENSIONS)
        self.save_as_tree = LithoDirectoryTree(home, name="save_as", classes="saveas", file_filter=ACCEPTED_EXTENSIONS)
        self.header = LithoHeader(style="white on dark_blue", tall=False, clock=False)
        self.footer = LithoFooter()

        self.mount(
                header=self.header,
                content=self.body,
                footer=self.footer,
                outline=self.outline,
                open=self.open_tree,
                saveas=self.save_as_tree
        )

        if document is None:
            self.open_tree.toggle_class("-active")

        if document is not None:
            # Load user specified document
            await self.load_document(document)
        else:
            # Load our welcome document at start up
            await self.load_document("Welcome.md")

    async def load_document(self, filename: str) -> None:
        """Convert file to markdown and display"""
        try:
            pd = pandoc.read(file=filename)
            self.app.sub_title = self.get_first_header_title(pd, filename)
            md = Markdown(pandoc.write(pd, format="markdown"))
            self.body.update(md)
        except:
            self.body.update("Sorry, unable to load file.")



if __name__ == "__main__":
    app = Lithograph()
    app.run()
