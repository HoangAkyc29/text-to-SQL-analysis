# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — Data Access App (Flet desktop, onedir)."""
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None
ROOT = Path(SPECPATH).resolve()

datas = []
datas += collect_data_files("flet")
try:
    datas += collect_data_files("flet_desktop")
except Exception:
    pass

# Bundled Flet desktop client (flet.exe + DLLs) — no first-run download.
flet_view = ROOT / "packaging" / "flet_view"
if flet_view.is_dir() and (flet_view / "flet.exe").is_file():
    datas.append((str(flet_view), "flet_view"))
else:
    raise SystemExit(
        "Missing packaging/flet_view/flet.exe — copy from %USERPROFILE%\\.flet\\client\\...\\flet"
    )

a = Analysis(
    [str(ROOT / "run_desktop.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "app",
        "app.main",
        "app.paths",
        "app.config",
        "app.single_instance",
        "app.theme",
        "app.db",
        "app.db.connection",
        "app.db.errors",
        "app.db.dual_query",
        "app.db.cutoff",
        "app.db.session_clock",
        "app.db.query_log",
        "app.domain",
        "app.domain.columns",
        "app.domain.loyalty_customers",
        "app.domain.customer",
        "app.domain.customer_orders",
        "app.domain.product",
        "app.domain.product_orders",
        "app.domain.bill_expand",
        "app.domain.customer_filters",
        "app.domain.search_opts",
        "app.domain.frame_sort",
        "app.export",
        "app.export.excel",
        "app.export.rich_report",
        "app.export.splitters",
        "app.export.txt_report",
        "app.ui",
        "app.ui.shell",
        "app.ui.jobs",
        "app.ui.widgets",
        "app.ui.form_kit",
        "app.ui.validate",
        "app.ui.output_path",
        "app.ui.clipboard_ids",
        "app.ui.tooltips",
        "app.ui.pages.loyalty_page",
        "app.ui.pages.customer_page",
        "app.ui.pages.customer_orders_page",
        "app.ui.pages.product_page",
        "app.ui.pages.product_orders_page",
        "app.ui.pages.settings_page",
        "app.text.tcvn3",
        "pyodbc",
        "pandas",
        "openpyxl",
        "dotenv",
        "flet",
        "flet_desktop",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "tkinter",
        "matplotlib",
        "scipy",
        "IPython",
        "notebook",
        "flet.testing",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DataAccessApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="DataAccessApp",
)
