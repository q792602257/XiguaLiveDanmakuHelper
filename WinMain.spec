# -*- mode: python -*-

block_cipher = None


a = Analysis(['WinMain.py'],
             pathex=['E:\\XiGuaLiveDanmakuHelper',r'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\10.0.18362.0\\ucrt\\DLLs\\x86'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=["xml", "_tkinter", "pydoc", "lib2to3"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='西瓜直播礼物助手',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          runtime_tmpdir=None,
          console=True, 
          icon='./ico.ico' )
