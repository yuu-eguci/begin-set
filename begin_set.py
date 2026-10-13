#!/usr/bin/env python3

'''begin_set

俺式アプリ準備セット。
    1. カレント移して
    2. カレント以下のディレクトリを取得して
    3. 全部インポートパスに登録しますよ。

使い方はこう!
    import begin_set
    begin_set.exec_all(__file__)

でどうぞ! これを直接実行してもちゃんとテスト動作でうごくよ。
'''

import os
import sys
import warnings
from pprint import pprint


def cd_(file_path):
    '''カレントディレクトリを file_path の場所に移す。'''

    if not isinstance(file_path, str | os.PathLike) or not os.path.exists(file_path):
        raise ValueError(f'No such file: {file_path}')

    os.chdir(
        os.path.dirname(
            sys.executable if hasattr(sys, 'frozen') else os.path.abspath(file_path)
        )
    )


def _is_inside(path, top):
    try:
        return os.path.commonpath([path, top]) == top
    except ValueError:  # Windows でドライブが違うとき
        return False


def get_directory_tree(top_dir, rmpycache=True):
    '''トップディレクトリ以下全ディレクトリのリストを入手します。
    デフォルトでは__pycache__は除きます。
    . で始まるディレクトリと、読めないディレクトリの中身も除きます。
    シンボリックリンクはトップ以下を指すものだけ、同じ実体は 1 回だけ入れます。'''

    tree = [os.path.abspath(top_dir)]
    top_real = os.path.realpath(tree[0])
    seen = {top_real}
    for directory in tree:
        try:
            names = sorted(os.listdir(directory))
        except OSError:
            continue
        for name in names:
            path = os.path.join(directory, name)
            if (
                name.startswith('.')
                or (rmpycache and name == '__pycache__')
                or not os.path.isdir(path)
            ):
                continue
            real = os.path.realpath(path)
            if real in seen or not _is_inside(real, top_real):
                continue
            seen.add(real)
            tree.append(path)
    return tree


def _warn_stdlib_shadows(directory, stacklevel):
    try:
        names = sorted(os.listdir(directory))
    except OSError:
        return
    for name in names:
        module = name.removesuffix('.py')
        if module not in sys.stdlib_module_names:
            continue
        path = os.path.join(directory, name)
        if name.endswith('.py') or os.path.isfile(os.path.join(path, '__init__.py')):
            warnings.warn(
                f'{path} が標準ライブラリの {module} と同じ名前です',
                stacklevel=stacklevel + 1,
            )


def remake_import_path(directory_tree, stacklevel=2):
    '''インポートパスの先頭に追加する。もうあるパスは先頭に移す。
    標準ライブラリと同じ名前のモジュールがあれば警告する。
    stacklevel は warnings.warn と同じ意味で、警告に出す呼び出し元を決める。'''

    for directory in directory_tree:
        _warn_stdlib_shadows(directory, stacklevel)

    added = set(directory_tree)
    sys.path[:] = directory_tree + [p for p in sys.path if p not in added]


def exec_all(file_name):
    '''このモジュールをフル実行します。引数には__file__を渡せばいいと思います。'''

    start_dir = os.getcwd()
    cd_(file_name)
    top_dir = os.path.join(start_dir, os.path.dirname(file_name))
    remake_import_path(get_directory_tree(top_dir, True), stacklevel=3)


if __name__ == '__main__':
    print(f'__file__: {__file__}' + '\n')

    cd_(__file__)
    print('cd_実行後の os.getcwd():')
    print(os.getcwd() + '\n')

    print('get_directory_tree(os.path.dirname(__file__), True):')
    pprint(get_directory_tree(os.path.dirname(__file__), True))
    print()

    print('remake_import_path(directory_tree)後のsys.path:')
    remake_import_path(get_directory_tree(os.path.dirname(__file__), True))
    pprint(sys.path)
