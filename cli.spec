# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['lib/cli/cli.py'],
             pathex=['/home/user/Projects/python/substorm-nlp'],
             binaries=[],
             datas=[],
             hiddenimports=['google-api-python-client', 'apiclient', 'pkg_resources.py2_warn','googleapiclient', 'lib.automate.modules', 'lib.automate.modules.send', 'lib.automate.modules.schedule', 'lib.automate.modules.remove_schedule','lib.automate.modules.update_schedule', 'lib.automate.modules.reminder'],
             hookspath=['./hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='cli',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='cli')
