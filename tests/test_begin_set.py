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


def test_cd_accepts_pathlike(app, tmp_path):
    os.chdir(tmp_path)
    begin_set.cd_(app / 'main.py')
    assert os.getcwd() == str(app)


def test_get_directory_tree_skips_hidden_dirs(app):
    (app / '.git' / 'objects').mkdir(parents=True)
    (app / '.venv').mkdir()
    tree = begin_set.get_directory_tree(str(app))
    assert not any(
        part.startswith('.')
        for p in tree
        for part in os.path.relpath(p, app).split(os.sep)
        if part != '.'
    )


def test_get_directory_tree_is_sorted(app, monkeypatch):
    for name in ['b', 'a', 'c']:
        (app / name).mkdir()
    listdir = os.listdir
    monkeypatch.setattr(os, 'listdir', lambda d: sorted(listdir(d), reverse=True))
    tree = begin_set.get_directory_tree(str(app))
    assert tree == [
        str(app),
        str(app / 'a'),
        str(app / 'b'),
        str(app / 'c'),
        str(app / 'pkg'),
        str(app / 'pkg' / 'sub'),
    ]


@pytest.mark.skipif(not hasattr(os, 'symlink'), reason='no symlink')
def test_get_directory_tree_visits_each_real_dir_once(app):
    try:
        (app / 'pkg' / 'loop').symlink_to(app, target_is_directory=True)
    except OSError:
        pytest.skip('symlink not permitted')
    tree = begin_set.get_directory_tree(str(app))
    assert sorted(tree) == sorted(
        [str(app), str(app / 'pkg'), str(app / 'pkg' / 'sub')]
    )


@pytest.mark.skipif(os.name == 'nt' or os.geteuid() == 0, reason='chmod has no effect')
def test_get_directory_tree_skips_unreadable_dir(app):
    locked = app / 'locked'
    locked.mkdir()
    locked.chmod(0)
    try:
        tree = begin_set.get_directory_tree(str(app))
    finally:
        locked.chmod(0o755)
    assert str(app / 'pkg' / 'sub') in tree
    assert str(locked) in tree


@pytest.mark.skipif(not hasattr(os, 'symlink'), reason='no symlink')
def test_get_directory_tree_skips_symlink_to_outside(app, tmp_path):
    (tmp_path / 'outside' / 'deep').mkdir(parents=True)
    try:
        (app / 'out').symlink_to(tmp_path / 'outside', target_is_directory=True)
    except OSError:
        pytest.skip('symlink not permitted')
    tree = begin_set.get_directory_tree(str(app))
    assert not any(p.startswith(str(app / 'out')) for p in tree)


def test_remake_import_path_updates_in_place_without_duplicates(app):
    original = sys.path
    begin_set.remake_import_path([str(app), str(app / 'pkg')])
    begin_set.remake_import_path([str(app), str(app / 'pkg')])
    assert sys.path is original
    assert sys.path[:2] == [str(app), str(app / 'pkg')]
    assert sys.path.count(str(app)) == 1


def test_exec_all_accepts_relative_path(app, tmp_path):
    os.chdir(tmp_path)
    begin_set.exec_all(os.path.join('app', 'main.py'))
    assert os.getcwd() == str(app)
    assert str(app / 'pkg' / 'sub') in sys.path


def test_remake_import_path_warns_on_stdlib_shadow(app):
    (app / 'pkg' / 'json.py').write_text('')
    (app / 'pkg' / 'sub' / 'logging').mkdir()
    (app / 'pkg' / 'sub' / 'logging' / '__init__.py').write_text('')
    with pytest.warns(UserWarning) as record:
        begin_set.remake_import_path(begin_set.get_directory_tree(str(app)))
    messages = ' '.join(str(w.message) for w in record)
    assert 'json' in messages
    assert 'logging' in messages


def test_remake_import_path_does_not_warn_without_shadow(app, recwarn):
    (app / 'pkg' / 'email_utils.py').write_text('')
    (app / 'pkg' / 'os').mkdir()  # __init__.py が無いので標準ライブラリに負ける
    begin_set.remake_import_path(begin_set.get_directory_tree(str(app)))
    assert not [w for w in recwarn if issubclass(w.category, UserWarning)]


def test_shadow_warning_points_at_caller(app, tmp_path):
    (app / 'pkg' / 'json.py').write_text('')
    with pytest.warns(UserWarning) as direct:
        begin_set.remake_import_path(begin_set.get_directory_tree(str(app)))
    os.chdir(tmp_path)
    with pytest.warns(UserWarning) as via_exec_all:
        begin_set.exec_all(str(app / 'main.py'))
    assert direct[0].filename == __file__
    assert via_exec_all[0].filename == __file__
