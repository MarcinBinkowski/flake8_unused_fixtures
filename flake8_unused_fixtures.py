import ast
import sys
from typing import Any, Generator, List, Tuple, Type, Union

import pkg_resources

if sys.version_info >= (3, 9):
    from ast import unparse
else:
    from astunparse import unparse

MSG = "FUF100 fixture <{}> not used"


class Plugin:
    name = __name__
    version = pkg_resources.get_distribution(__name__).version

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)
        for row, col, fixture in visitor.problems:
            yield row, col, MSG.format(fixture), type(self)


class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.problems: List[Tuple[int, int, str]] = []

    def _check_for_unused_fixtures(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ):
        if node.name.startswith("test_") or node.name.endswith("_test"):

            skip_fixtures = ["self", "cls"]
            body_as_str = unparse(node.body)
            for fixture in node.args.args:
                if fixture.arg not in skip_fixtures and fixture.arg not in body_as_str:
                    self.problems.append(
                        (fixture.lineno, fixture.col_offset, fixture.arg)
                    )

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_for_unused_fixtures(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_for_unused_fixtures(node)
        self.generic_visit(node)
