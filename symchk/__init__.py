#!/usr/bin/env python3

import argparse
import itertools
import logging
import multiprocessing
import os
import urllib.request
from typing import Any, Optional, Tuple
from urllib.error import HTTPError

from pdbparse.peinfo import (
    get_dbg_fname,
    get_nb10,
    get_pe_debug_data,
    get_pe_guid,
    get_rsds,
)

import symchk.parallel

DEFAULT_SYMBOLS_SERVERS = [
    "http://msdl.microsoft.com/download/symbols",
    # "http://symbols.mozilla.org/",
    # "https://chromium-browser-symsrv.commondatastorage.googleapis.com",
    # "http://ctxsym.citrix.com/symbols",
]


@symchk.parallel.rate_limit(4)
def _download_file(target: str, outfile: str) -> None:
    urllib.request.urlretrieve(target, outfile)


def download_file(guid: str, fname: str, output_directory: str) -> Optional[str]:
    """
    Download the symbols specified by guid and filename. Note that 'guid'
    must be the GUID from the executable with the dashes removed *AND* the
    Age field appended. The resulting file will be saved to the
    output_directory argument, which default to the current directory.
    """

    # A normal GUID is 32 bytes. With the age field appended
    # the GUID argument should therefore be longer to be valid.
    # Exception: old-style PEs without a debug section use
    # TimeDateStamp+SizeOfImage
    if len(guid) == 32:
        logging.warning("GUID is too short to be valid. Did you append the Age field?")

    for sym_url in DEFAULT_SYMBOLS_SERVERS:
        for name in [fname[:-1] + "_", fname]:
            target = f"{sym_url}/{fname}/{guid}/{name}"
            logging.info(f"Trying {target}")
            base_dir = os.path.join(output_directory, fname, guid)
            if os.path.exists(base_dir):
                logging.info(f"Skipping: {base_dir} already exists")
                return None

            try:
                os.makedirs(base_dir)
            except NotADirectoryError:
                logging.error(f"Cannot create {base_dir}")
                continue

            try:
                outfile = os.path.join(base_dir, name)
                _download_file(target, outfile)
                logging.info(f"Saved symbols to {outfile}")
                return outfile

            except HTTPError as error:
                logging.error(f"Cannot fetch {target}: HTTP error {error.code}")
                if not os.listdir(base_dir):
                    os.rmdir(base_dir)

    return None


def handle_xp_pe(debug_data: bytes, output_directory: str) -> Optional[str]:
    # XP+
    logging.info("Handle XP PE")
    if debug_data[:4] == b"RSDS":
        guid, filename = get_rsds(debug_data)

    elif debug_data[:4] == b"NB10":
        guid, filename = get_nb10(debug_data)

    else:
        logging.error("CodeView section not NB10 or RSDS")
        return None

    guid = guid.upper()
    return download_file(guid, filename, output_directory)


def handle_compressed_win2k_pe(saved_file: str, output_directory: str) -> Optional[str]:
    # Extract it if it's compressed
    if saved_file.endswith("_"):
        os.system(f"cabextract {saved_file}")
        saved_file = saved_file.replace(".db_", ".dbg")

    from pdbparse.dbgold import DbgFile

    dbg_file = DbgFile.parse_stream(open(saved_file, "rb"))
    cv_entry = [
        dbg_entry
        for dbg_entry in dbg_file.IMAGE_DEBUG_DIRECTORY
        if dbg_entry.Type == "IMAGE_DEBUG_TYPE_CODEVIEW"
    ][0]
    if cv_entry.Data[:4] == b"NB09":
        logging.warning("Got NB09 CodeView")
        return None

    elif cv_entry.Data[:4] == b"NB10":
        guid, filename = get_nb10(cv_entry.Data)
        guid = guid.upper()
        return download_file(guid, filename, output_directory)

    else:
        logging.warning(
            "DBG file received from symbol server has unknown CodeView section"
        )

    return None


def handle_win2k_pe(
    debug_data: bytes, pe_file: str, output_directory: str
) -> Optional[str]:
    # Win2k
    # Get the .dbg file
    logging.info("Handle Win2k PE")
    guid = get_pe_guid(pe_file)
    guid = guid.upper()
    try:
        filename = get_dbg_fname(debug_data)

    except AttributeError:
        # pdbparse may fail to parse the symbol filename because of encoding
        # With the code below, we try to avoid such decoding errors
        import ntpath

        from pdbparse.dbgold import IMAGE_DEBUG_MISC

        dbgstruct = IMAGE_DEBUG_MISC.parse(debug_data)
        raw_filename = dbgstruct.Strings[0]
        filename = ntpath.basename(raw_filename)

    saved_file = download_file(guid, filename, output_directory)
    if saved_file is None:
        return None

    return handle_compressed_win2k_pe(saved_file, output_directory)


def init_logger() -> None:
    logging.basicConfig(
        filename="symchk.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    )


def _download_from_pe(filepath: str, output_directory: str) -> None:
    saved_file = None
    try:
        debug_data, debug_type = get_pe_debug_data(filepath)

    except Exception:  # pefile.PEFormatError: # DOS Header magic not found, pdbparse lib error
        return

    if debug_type == "IMAGE_DEBUG_TYPE_CODEVIEW":
        saved_file = handle_xp_pe(debug_data, output_directory)

    elif debug_type == "IMAGE_DEBUG_TYPE_MISC":
        saved_file = handle_win2k_pe(debug_data, filepath, output_directory)

    else:
        logging.error(f"Unknown debug type: {debug_type}")
        return

    if saved_file is not None and saved_file.endswith("_"):
        os.system(f"cabextract {saved_file}")


def download_from_pe(args: argparse.Namespace) -> None:
    _download_from_pe(args.file, args.output_directory)


def _download_from_pe_async(args: Tuple[str, str]) -> None:
    _download_from_pe(*args)


def download_from_dir(args: argparse.Namespace) -> None:
    processes = multiprocessing.cpu_count() - 1 or 1
    with multiprocessing.Pool(processes) as pool:
        walk = os.walk(args.dir)
        gen = itertools.chain.from_iterable(
            (
                ((os.path.join(root, file), args.output_directory) for file in files)
                for root, _, files in walk
            )
        )
        pool.map(_download_from_pe_async, gen)


def download_from_metadata(args: argparse.Namespace) -> Any:
    saved_file = download_file(args.guid, args.pdb, args.output_directory)
    if saved_file is None:
        return

    if saved_file.endswith("_"):
        os.system("cabextract %s" % saved_file)
