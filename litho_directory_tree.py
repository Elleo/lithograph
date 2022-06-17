import re
from os import scandir
from textual.widgets import TreeNode, DirectoryTree
from textual.widgets._directory_tree import DirEntry

class LithoDirectoryTree(DirectoryTree):

    file_filter = ".*"
    _id = None
    _name = "dirtree"
    _classes = ""

    def __init__(self, path: str, name: str = None, classes: str = None, file_filter: str = ".*") -> None:
        self.file_filter=file_filter
        self._name = name
        self._classes = classes
        super().__init__(path, name)

    async def load_directory(self, node: TreeNode[DirEntry]):
        path = node.data.path
        directory = sorted(
            list(scandir(path)), key=lambda entry: (not entry.is_dir(), entry.name)
        )
        for entry in directory:
            if entry.is_dir() or re.match(self.file_filter, entry.path) is not None:
                await node.add(entry.name, DirEntry(entry.path, entry.is_dir()))
        node.loaded = True
        await node.expand()
        self.refresh(layout=True)
