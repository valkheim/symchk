# symchk

Download PDB files from the Microsoft Symbol Server.

## Installation

You can use symchk as a package or as a simple script and is best used with [poetry][1]:

```console
$ ls
pyproject.toml README.md symchk tests

$ poetry install
Creating virtualenv symchk-_Dg9LuZz-py3.8 in /home/user/.cache/pypoetry/virtualenvs
Updating dependencies
Resolving dependencies... (1.8s)

Writing lock file

Package operations: 16 installs, 0 updates, 0 removals

  • Installing backports.entry-points-selectable (1.1.0)
  • Installing distlib (0.3.2)
  • Installing filelock (3.0.12)
  • Installing future (0.18.2)
  • Installing platformdirs (2.3.0)
  • Installing six (1.16.0)
  • Installing cfgv (3.3.1)
  • Installing construct (2.9.52)
  • Installing identify (2.2.13)
  • Installing nodeenv (1.6.0)
  • Installing pefile (2021.9.3)
  • Installing pyyaml (5.4.1)
  • Installing toml (0.10.2)
  • Installing virtualenv (20.7.2)
  • Installing pdbparse (1.5)
  • Installing pre-commit (2.15.0)

$ poetry run symchk
usage: symchk [-o OUTPUT_DIRECTORY] {from-pe,from-dir,from-metadata} ...

positional arguments:
  {from-pe,from-dir,from-metadata}
                        Download a PDB file

optional arguments:
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Output directory (Symbols cache directory)
```

## Getting started

Download from an executable file path:

```console
$ poetry run symchk from-pe --file /tmp/ntdll.dll

$ ls
poetry.lock  pyproject.toml  README.md  symcache  symchk  symchk.log

$ cat symchk.log
2021-09-07 10:33:52,212 INFO:root:Handle XP PE
2021-09-07 10:33:52,212 INFO:root:Trying http://msdl.microsoft.com/download/symbols/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pd_
2021-09-07 10:33:52,626 ERROR:root:Cannot fetch http://msdl.microsoft.com/download/symbols/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pd_: HTTP error 404
2021-09-07 10:33:52,627 INFO:root:Trying http://msdl.microsoft.com/download/symbols/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pdb
2021-09-07 10:33:54,389 INFO:root:Saved symbols to symcache/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pdb

$ ls symcache -R
symcache:
wntdll.pdb

symcache/wntdll.pdb:
7EDD56F06D47FF1247F446FD1B111F2C1

symcache/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1:
wntdll.pdb
```

Download recursively from a directory:

```console
$ ls -R /tmp
/tmp:
edge  notepad.exe  ntdll.dll

/tmp/edge:
EdgeManager.dll

$ poetry run symchk from-dir --dir /tmp/

$ cat symchk.log
2021-09-07 10:36:04,430 INFO:root:Handle XP PE
2021-09-07 10:36:04,431 INFO:root:Trying http://msdl.microsoft.com/download/symbols/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pd_
2021-09-07 10:36:04,431 INFO:root:Handle XP PE
2021-09-07 10:36:04,433 INFO:root:Trying http://msdl.microsoft.com/download/symbols/edgemanager.pdb/48B3E29DA3C423D299E1616AC39AC0351/edgemanager.pd_
2021-09-07 10:36:04,433 INFO:root:Handle XP PE
2021-09-07 10:36:04,434 INFO:root:Trying http://msdl.microsoft.com/download/symbols/notepad.pdb/6539CE998C7CAFD73A8E13A54542E1121/notepad.pd_
2021-09-07 10:36:04,790 ERROR:root:Cannot fetch http://msdl.microsoft.com/download/symbols/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pd_: HTTP error 404
2021-09-07 10:36:04,790 INFO:root:Trying http://msdl.microsoft.com/download/symbols/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pdb
2021-09-07 10:36:04,919 ERROR:root:Cannot fetch http://msdl.microsoft.com/download/symbols/edgemanager.pdb/48B3E29DA3C423D299E1616AC39AC0351/edgemanager.pd_: HTTP error 404
2021-09-07 10:36:04,919 INFO:root:Trying http://msdl.microsoft.com/download/symbols/edgemanager.pdb/48B3E29DA3C423D299E1616AC39AC0351/edgemanager.pdb
2021-09-07 10:36:05,049 ERROR:root:Cannot fetch http://msdl.microsoft.com/download/symbols/notepad.pdb/6539CE998C7CAFD73A8E13A54542E1121/notepad.pd_: HTTP error 404
2021-09-07 10:36:05,050 INFO:root:Trying http://msdl.microsoft.com/download/symbols/notepad.pdb/6539CE998C7CAFD73A8E13A54542E1121/notepad.pdb
2021-09-07 10:36:07,415 INFO:root:Saved symbols to symcache/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pdb
2021-09-07 10:36:12,328 INFO:root:Saved symbols to symcache/edgemanager.pdb/48B3E29DA3C423D299E1616AC39AC0351/edgemanager.pdb
2021-09-07 10:36:13,901 INFO:root:Saved symbols to symcache/notepad.pdb/6539CE998C7CAFD73A8E13A54542E1121/notepad.pdb

$ ls -R symcache/
symcache/:
edgemanager.pdb  notepad.pdb  wntdll.pdb

symcache/edgemanager.pdb:
48B3E29DA3C423D299E1616AC39AC0351

symcache/edgemanager.pdb/48B3E29DA3C423D299E1616AC39AC0351:
edgemanager.pdb

symcache/notepad.pdb:
6539CE998C7CAFD73A8E13A54542E1121

symcache/notepad.pdb/6539CE998C7CAFD73A8E13A54542E1121:
notepad.pdb

symcache/wntdll.pdb:
7EDD56F06D47FF1247F446FD1B111F2C1

symcache/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1:
wntdll.pdb
```

Download PDB metadata (GUID + Age combo and PDB file name)

```console
$ poetry run symchk from-metadata --guid 7EDD56F06D47FF1247F446FD1B111F2C1 --pdb wntdll.pdb

$ cat symchk.log
2021-09-07 10:37:52,664 INFO:root:Trying http://msdl.microsoft.com/download/symbols/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pd_
2021-09-07 10:37:53,040 ERROR:root:Cannot fetch http://msdl.microsoft.com/download/symbols/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pd_: HTTP error 404
2021-09-07 10:37:53,040 INFO:root:Trying http://msdl.microsoft.com/download/symbols/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pdb
2021-09-07 10:37:55,253 INFO:root:Saved symbols to symcache/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1/wntdll.pdb

$ ls -R symcache/
symcache/:
wntdll.pdb

symcache/wntdll.pdb:
7EDD56F06D47FF1247F446FD1B111F2C1

symcache/wntdll.pdb/7EDD56F06D47FF1247F446FD1B111F2C1:
wntdll.pdb
```

You can use the `-o` option to select an output directory.

## Dependencies

* [pdbparse][2]
* [cabextract][3]

## See also

* https://blog.google/threat-analysis-group/active-north-korean-campaign-targeting-security-researchers/

[1]: https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions
[2]: https://github.com/moyix/pdbparse
[3]: http://www.cabextract.org.uk/
