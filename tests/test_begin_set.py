import os
import sys

import pytest

import begin_set


@pytest.fixture(autouse=True)
def restore_state(monkeypatch):
    '''テストごとにカレントと sys.path を元に戻す。'''
    monkeypatch.chdir(os.getcwd())
    monkeypatch.setattr(sys, 'path', sys.path[:])


@pytest.fixture
def app(tmp_path):
    '''app/main.py, app/pkg/sub/modsub.py, app/__pycache__ を持つ小さな作業場。'''
    root = tmp_path / 'app'
    (root / 'pkg' / 'sub').mkdir(parents=True)
    (root / '__pycache__').mkdir()
    (root / 'pkg' / 'sub' / 'modsub.py').write_text('X = "sub"\n')
    (root / 'main.py').write_text('')
    return root


def test_cd_moves_to_file_directory(app, tmp_path):
    os.chdir(tmp_path)
    begin_set.cd_(str(app / 'main.py'))
    assert os.getcwd() == str(app)


def test_cd_rejects_missing_file(tmp_path):
    with pytest.raises(ValueError):
        begin_set.cd_(str(tmp_path / 'nope.py'))


def test_get_directory_tree_lists_subdirs_without_pycache(app):
    tree = begin_set.get_directory_tree(str(app))
    assert sorted(tree) == sorted(
        [str(app), str(app / 'pkg'), str(app / 'pkg' / 'sub')]
    )


def test_get_directory_tree_keeps_pycache_when_asked(app):
    tree = begin_set.get_directory_tree(str(app), rmpycache=False)
    assert str(app / '__pycache__') in tree


def test_remake_import_path_prepends(app):
    begin_set.remake_import_path([str(app)])
    assert sys.path[0] == str(app)


def test_exec_all_makes_deep_module_importable(app, tmp_path):
    os.chdir(tmp_path)
    sys.modules.pop('modsub', None)
    begin_set.exec_all(str(app / 'main.py'))
    import modsub

    assert modsub.X == 'sub'
    assert os.getcwd() == str(app)
    sys.modules.pop('modsub', None)
