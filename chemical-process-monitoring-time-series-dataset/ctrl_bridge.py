"""
ctrl_bridge.py -- link this dataset project to the Controller-Toolbox project.

WHY THIS FILE EXISTS
--------------------
Controller-Toolbox's Python bindings are a compiled extension module:

    Controller-Toolbox/build/bindings/ctrl_toolbox.cp312-win_amd64.pyd

The `cp312` tag means CPython 3.12 ONLY. A .pyd is ABI-locked to its minor
version, so it cannot be imported from this project's `data_science` conda env
(Python 3.14) -- the import fails outright, it does not degrade gracefully.

    RUN BOTH NOTEBOOKS ON THE `soft_robotics` KERNEL (Python 3.12).

`soft_robotics` already provides numpy and pandas. If Jupyter is missing:

    conda install -n soft_robotics jupyter ipykernel matplotlib seaborn
    conda run -n soft_robotics python -m ipykernel install --user \
        --name soft_robotics --display-name "Python (soft_robotics)"

If you would rather build the bindings for 3.14, `pyproject.toml` uses
scikit-build-core, so `pip install .` from the Controller-Toolbox root would try
-- but its classifiers stop at 3.12 and pybind11 v2.13.6 predates 3.14, so
expect that to fail. Matching the kernel is the cheaper path.

USAGE
-----
    from ctrl_bridge import ctrl        # imports and returns ctrl_toolbox
    # or
    import ctrl_bridge; import ctrl_toolbox as ctrl
"""
from __future__ import annotations

import os
import sys

# Set CTRL_TOOLBOX_ROOT in the environment to override this default.
DEFAULT_CTRL_ROOT = r"C:\Users\dangs\Desktop\project\Controller-Toolbox"


def _candidate_roots():
    env = os.environ.get("CTRL_TOOLBOX_ROOT")
    if env:
        yield env
    yield DEFAULT_CTRL_ROOT
    # Sibling of this project, in case the tree moves.
    here = os.path.dirname(os.path.abspath(__file__))
    for up in (2, 3):
        parent = here
        for _ in range(up):
            parent = os.path.dirname(parent)
        yield os.path.join(parent, "Controller-Toolbox")


def find_ctrl_root() -> str:
    tried = []
    for root in _candidate_roots():
        tried.append(root)
        if os.path.isfile(os.path.join(root, "_setup_bindings.py")):
            return root
    raise FileNotFoundError(
        "Could not locate the Controller-Toolbox repo root (no _setup_bindings.py).\n"
        "Tried:\n  " + "\n  ".join(tried) + "\n"
        "Set CTRL_TOOLBOX_ROOT to the repo root and re-run."
    )


def load():
    """Put ctrl_toolbox on sys.path and import it. Returns the module."""
    root = find_ctrl_root()

    if root not in sys.path:
        sys.path.insert(0, root)

    # Controller-Toolbox ships _setup_bindings.py, which inserts build/bindings
    # into sys.path and registers the MinGW DLL directory on Windows.
    import _setup_bindings  # noqa: F401

    # _setup_bindings only registers C:\msys64\mingw64\bin, but this repo's
    # documented toolchain is UCRT64. Harmless when the .pyd is statically
    # linked (it should be), but add it so a non-static build still resolves.
    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        for extra in (r"C:\msys64\ucrt64\bin",):
            if os.path.isdir(extra):
                try:
                    os.add_dll_directory(extra)
                except OSError:
                    pass

    try:
        import ctrl_toolbox as _ctrl
    except ImportError as exc:
        build_dir = os.path.join(root, "build", "bindings")
        found = sorted(
            f for f in os.listdir(build_dir) if f.startswith("ctrl_toolbox")
        ) if os.path.isdir(build_dir) else []
        raise ImportError(
            f"import ctrl_toolbox failed: {exc}\n\n"
            f"Repo root      : {root}\n"
            f"Build dir      : {build_dir}\n"
            f"Modules found  : {found or '(none -- bindings not built)'}\n"
            f"This kernel    : Python {sys.version.split()[0]} "
            f"(needs cp{sys.version_info.major}{sys.version_info.minor})\n\n"
            "If the tag above does not match this kernel, switch to the\n"
            "soft_robotics kernel (Python 3.12). If no module was found, build it:\n"
            "  cmake -S . -B build -DCMAKE_BUILD_TYPE=Release "
            "-DCTRL_BUILD_PYTHON_BINDINGS=ON\n"
            "  cmake --build build --target ctrl_toolbox"
        ) from exc

    return _ctrl


def describe() -> str:
    """One-line environment summary, handy at the top of a notebook."""
    import numpy as np
    return (
        f"python {sys.version.split()[0]}  |  numpy {np.__version__}  |  "
        f"ctrl_toolbox from {os.path.dirname(ctrl.__file__)}"
    )


ctrl = load()

__all__ = ["ctrl", "load", "find_ctrl_root", "describe"]
