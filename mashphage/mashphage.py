#!/usr/bin/env python3

# mashphage: Clustering of Actinobacteriphages genomes
# Copyright (C) 2021 Anicet Ebou
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
from datetime import datetime
from distutils.spawn import find_executable
import dnaio
import os
from pathlib import Path
import shutil
import subprocess
import sys
from xopen import xopen

AUTHOR = "Anicet Ebou <anicet.ebou@gmail.com>"
URL = "https://github.com/Ebedthan/mashphage.git"
VERSION = "0.1.0"

# Define start time----------------------------------------------------------
startime = datetime.now()

# Define command-line arguments----------------------------------------------
parser = argparse.ArgumentParser(
    prog="mashphage",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    usage="mashphage [options] <genomes.fa.gz>",
    epilog=f"Version:   {VERSION}\nLicence:   GPL-3\n"
    + f"Homepage:  {URL}\nAuthor:    {AUTHOR}\nMade In Côte d'Ivoire.",
)

parser.add_argument(
    "genomes",
    help="input fasta file. Can be gz, bzp2 or xz compressed",
)
parser.add_argument(
    "-o",
    type=Path,
    metavar="FILE",
    default="mashphage.tsv",
    help="output results to FILE [mashphage.tsv]",
)
parser.add_argument(
    "-d",
    metavar="FILE",
    default=Path(
        Path(Path(__file__).resolve().parent).parent, "db", "mashphage.sbt.zip"
    )
    or os.environ["MASHPHDB"],
    help="path to genomic signature [db/mashphage.sbt.zip]",
)
parser.add_argument(
    "--force",
    action="store_true",
    help="force re-use of output file [false]",
)
parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
args = parser.parse_args()


def main():
    # Start program ---------------------------------------------------------
    msg(f"This is mashphage {VERSION}")
    msg(f"Written by {AUTHOR}")
    msg(f"Available at {URL}")
    msg(f"Localtime is {datetime.now().strftime('%H:%M:%S')}")

    # Handling db directory path specification-------------------------------
    if not Path(args.d).is_file:
        err(
            "Mashphage genome signature file not found in $PATH."
            + " Please set MASHPHDB environment variable to the path"
            + " where the file is stored."
            + " Visit https://github.com/Ebedthan/mashphage for more"
        )
        sys.exit(1)

    # Handling output directory creation
    if os.path.exists(args.o):
        if args.force:
            warn(f"Reusing output file {args.o}")
            os.remove(args.o)
        else:
            err(
                f"Your choosen output file '{args.o}' already exist!"
                + " Please change it using -o option or use --force"
                + " to reuse it. "
            )
            sys.exit(1)

    # Verify presence of mash -----------------------------------------------
    if find_executable("sourmash") is None:
        err(
            "sourmash was not found on your system. Please install it at"
            + " https://github.com/sourmash-bio/sourmash"
        )
        sys.exit(1)

    ofh = open(args.o, "a")
    ofh.write("sequence\tsimilarity\tpredicted_cluster\n")

    # Build input sequence index for query ----------------------------------
    os.mkdir("mashphage_tmp")
    with xopen(args.genomes, mode="rb") as f:
        fasta = dnaio.FastaReader(f)
        for record in fasta:
            with dnaio.open(
                Path("mashphage_tmp", f"{record.name.split()[0]}.fa"), mode="w"
            ) as tf:
                tf.write(record)

    pathlist = Path("mashphage_tmp").glob("*.fa")
    for path in pathlist:
        msg(f"Sketching the genome {path.name.split('.')[0]}")
        subprocess.run(
            [
                "sourmash",
                "sketch",
                "dna",
                str(path),
            ]
        )

        tmp_out = open("search.out", "w")

        msg("Searching for the signature in mashphage signatures")
        subprocess.run(
            [
                "sourmash",
                "search",
                "--containment",
                f"{path.name}.sig",
                str(args.d),
            ],
            stdout=tmp_out,
        )

        with open("search.out") as fp:
            result = fp.readlines()[-1].split()
            tab = "\t"
            ofh.write(f"{record.name}\t{tab.join(result)}\n")

        try:
            os.remove(f"{path.name}.sig")
            os.remove("search.out")
        except OSError:
            pass

    msg("Cluster prediction done succesfully")

    try:
        shutil.rmtree("mashphage_tmp")
        os.remove("temp.fa")
    except OSError:
        pass

    msg(f"Check {args.o} for results")
    msg(f"Walltime used (hh:mm:ss.ms): {elapsed_since(startime)}")
    msg("Thanks you, come again.")


# Functions -----------------------------------------------------------------
def elapsed_since(start):
    walltime = datetime.now() - start
    return walltime


def msg(text):
    """
    msg produces nice message and info output on terminal.

    :text: Message to print to STDOUT.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}][INFO] {text}")


def warn(text):
    print(f"[{datetime.now().strftime('%H:%M:%S')}][WARN] {text}")


def err(text):
    print(f"[ERROR] {text}", file=sys.stderr)


def exception_handler(
    exception_type, exception, traceback, debug_hook=sys.excepthook
):
    """
    exception_handler remove default debug info and traceback
    from python output on command line. Use program --debug
    option to re-enable default behaviour.
    """

    if args.debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print(f"{exception_type.__name__}, {exception}")


sys.excepthook = exception_handler

if __name__ == "__main__":
    main()
