import ast
import textwrap
from typing import Set

import pytest

from flake8_unused_fixtures import Plugin


def _results(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    # line-1 as a side effect of using multiline strings as a test data
    return {f"{line-1}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivial_problem():
    assert _results("") == set()


@pytest.mark.parametrize("keyword", ("def", "async def"))
def test_no_fixtures(keyword):
    test_code = textwrap.dedent(
        f"""
        {keyword} test_1():
            assert 1 == 1
        """
    )
    assert _results(test_code) == set()


@pytest.mark.parametrize("keyword", ("def", "async def"))
def test_used_fixture(keyword):
    test_code = textwrap.dedent(
        f"""
        @pytest.fixture
        def fxt():
            return 1
        {keyword} test_1(fxt):
            a = fxt + 1
            assert a == 2
        """
    )
    assert _results(test_code) == set()


@pytest.mark.parametrize("keyword", ("def", "async def"))
def test_used_fixture_complex(keyword):
    test_code = textwrap.dedent(
        f"""
        @pytest.fixture
        {keyword} fxt():
            return 1
        {keyword} test_1(fxt):
            a = fxt + 1
            fxt
            assert fxt == 1
            assert a == 2
        """
    )
    assert _results(test_code) == set()


@pytest.mark.parametrize("keyword, line", [("def", 11), ("async def", 17)])
def test_unused_fixture(keyword, line):
    test_code = textwrap.dedent(
        f"""
        @pytest.fixture
        {keyword} fxt():
            return 1
        {keyword} test_1(fxt):
            assert 1 == 1
        """
    )
    assert _results(test_code) == {f"4:{line} FUF100 fixture <fxt> not used"}


@pytest.mark.parametrize("keyword", ("def", "async def"))
def test_unused_fixture_not_in_test(keyword):
    test_code = textwrap.dedent(
        f"""
        @pytest.fixture
        {keyword} fxt():
            return 1
        {keyword} foo(fxt):
            return 1
        """
    )
    assert _results(test_code) == set()


@pytest.mark.parametrize("keyword, line", [("def", 11), ("async def", 17)])
def test_many_fixtures(keyword, line):
    test_code = textwrap.dedent(
        f"""
        @pytest.fixture
        {keyword} fxt():
            return 1
        @pytest.fixture
        {keyword} fxt2():
            return 1
        {keyword} test_1(fxt):
            assert 1 == 1
        """
    )
    assert _results(test_code) == {f"7:{line} FUF100 fixture <fxt2> not used"}


@pytest.mark.parametrize(
    "keyword, line_1, line_2", [("def", 11, 16), ("async def", 17, 22)]
)
def test_many_fixtures_all_unused(keyword, line_1, line_2):
    test_code = textwrap.dedent(
        f"""
        @pytest.fixture
        {keyword} fxt():
            return 1
        @pytest.fixture
        {keyword} fxt2():
            return 1
        {keyword} test_1(fxt, fxt2):
            assert 1 == 1
        """
    )
    assert _results(test_code) == {
        f"7:{line_1} FUF100 fixture <fxt> not used",
        f"7:{line_2} FUF100 fixture <fxt2> not used",
    }


@pytest.mark.parametrize("keyword", ("def", "async def"))
def test_used_fixture_in_class(keyword):
    test_code = textwrap.dedent(
        f"""
        @pytest.fixture
        {keyword} fxt():
            return 1
        class TestCase:
            {keyword} test_1(self, fxt):
                assert fxt == 1
        """
    )
    assert _results(test_code) == set()


@pytest.mark.parametrize("keyword, line", [("def", 21), ("async def", 27)])
def test_unused_fixture_in_class(keyword, line):
    test_code = textwrap.dedent(
        f"""
        @pytest.fixture
        {keyword} fxt():
            return 1
        class TestCase:
            {keyword} test_1(self, fxt):
                assert 1 == 1
        """
    )
    assert _results(test_code) == {f"5:{line} FUF100 fixture <fxt> not used"}


@pytest.mark.parametrize("keyword, line", [("def", 11), ("async def", 17)])
def test_unused_fixture_as_other_fixture_substring(keyword, line):
    test_code = textwrap.dedent(
        f"""
        @pytest.fixture
        {keyword} fxt():
            return 1
        @pytest.fixture
        {keyword} fxt2():
            return 1
        {keyword} test_1(fxt, fxt2):
            assert fxt2 == 1
        """
    )
    assert _results(test_code) == {f"7:{line} FUF100 fixture <fxt> not used"}
