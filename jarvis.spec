# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Define data files to include
added_files = [
    ('Frontend/Graphics/*', 'Frontend/Graphics'),
    ('Data/*.json', 'Data'),
    ('.env', '.'),
    ('README.md', '.'),
    ('IMPROVEMENTS.md', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'pygame',
        'speech_recognition',
        'PIL',
        'PyQt5',
        'requests',
        'dotenv',
        'cohere',
        'AppOpener',
        'pywhatkit',
        'bs4',
        'rich',
        'keyboard',
        'googlesearch-python',
        'selenium',
        'mtranslate',
        'edge-tts',
        'webdriver-manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],  # Add runtime hook
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Jarvis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application without console
    icon='Frontend/Graphics/Jarvis.ico',  # Add icon if available
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
) 