"""
Download debugging symbols from the Microsoft Symbol Server.
Can use as an input an executable file OR a GUID+Age and filename.
Use cases:

    Find PDB from PE files:
    $ symchk from-pe -f /mnt/ntdll.dll

    Find PDB from directory tree of PE files:
    $ symchk from-dir -d /mnt

    Find PDB from GUID + PDB name
    $ symchk from-infos -g 7EDD56F06D47FF1247F446FD1B111F2C1 -s wntdll.pdb

This script may require `cabextract`.
"""

import argparse

from symchk import (
    download_from_dir,
    download_from_metadata,
    download_from_pe,
    init_logger,
)


def get_arguments() -> argparse.Namespace:
    init_logger()
    parser = argparse.ArgumentParser(prog="symchk", add_help=False)
    parser.set_defaults(func=lambda args: parser.print_help())
    parser.add_argument(
        "-o",
        "--output-directory",
        type=str,
        required=False,
        default="symcache",
        help="Output directory (Symbols cache directory)",
    )

    subparsers = parser.add_subparsers(help="Download a PDB file")

    parser_download_from_pe = subparsers.add_parser(
        "from-pe",
        description="Download a PDB from an executable file",
        parents=[parser],
    )
    parser_download_from_pe.set_defaults(func=download_from_pe)
    parser_download_from_pe.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="Executable file path for which your require symbols",
    )

    parser_download_from_dir = subparsers.add_parser(
        "from-dir",
        description="Download PDBs from a directory tree",
        parents=[parser],
    )
    parser_download_from_dir.set_defaults(func=download_from_dir)
    parser_download_from_dir.add_argument(
        "-d",
        "--dir",
        required=True,
        help="Directory path to explore recursively",
    )

    parser_download_from_metadata = subparsers.add_parser(
        "from-metadata",
        description="Download a PDB from metadata (guid + age, pdb filename)",
        parents=[parser],
    )
    parser_download_from_metadata.set_defaults(func=download_from_metadata)
    parser_download_from_metadata.add_argument(
        "-p", "--pdb", type=str, required=True, help="PDB file name (e.g. wntdll.pdb)"
    )
    parser_download_from_metadata.add_argument(
        "-g", "--guid", type=str, required=True, help="GUID + Age combo"
    )

    return parser.parse_args()


def main() -> None:
    args = get_arguments()
    args.func(args)


if __name__ == "__main__":
    main()
