# Copyright (c) 2016 Civic Knowledge. This file is licensed under the terms of the
# Revised BSD License, included in this distribution as LICENSE

from __future__ import print_function

import sys
from itertools import islice

from tabulate import tabulate

from rowgenerators import enumerate_contents, SourceSpec, SourceError
from rowgenerators import RowGenerator
from tableintuit import RowIntuiter
from itertools import islice
from rowgenerators import TextEncodingError

#Change the row cache name
from rowgenerators.util import  get_cache


def prt(*args):
    print(*args)

def warn( *args):
    print('WARN:',*args)

def err(*args):
    import sys
    print("ERROR:", *args)
    sys.exit(1)

def run_row_intuit(path, cache):

    for encoding in ('ascii', 'utf8', 'latin1'):
        try:
            rows = list(islice(RowGenerator(url=path, encoding=encoding, cache=cache), 5000))
            return encoding, RowIntuiter().run(rows)
        except TextEncodingError:
            pass

    raise Exception('Failed to convert with any encoding')

def rowgen():
    import argparse

    parser = argparse.ArgumentParser(
        prog='rowgen',
        description='Return CSV rows of data from a rowgenerator URL')

    parser.add_argument('-H', '--head', default=False, action='store_true',
                        help='Display only the first 20 lines, in tabular format')

    parser.add_argument('-e', '--encoding',
                        help='Force the encoding')

    parser.add_argument('-f', '--format',
                        help="Force the file format. Typical values are 'csv', 'xls', 'xlsx' ")

    parser.add_argument('-u', '--urlfiletype',
                        help="Force the type of the file downloaded from the url. Equivalent to changing the file extension ")

    parser.add_argument('-s', '--start',
                        help='Line number where data starts')

    parser.add_argument('-d', '--headers', default=None, action='store_true',
                        help="Comma seperated list of header line numebrs")

    parser.add_argument('-E', '--enumerate', default=None, action='store_true',
                        help="Download the URL and enumerate it's contents as URLs")

    parser.add_argument('-i', '--intuit', default=None, action='store_true',
                        help="Intuit headers, start lines, etc")

    parser.add_argument('-I', '--info', default=None, action='store_true',
                        help="Print information about the url")

    parser.add_argument('url')

    cache = get_cache()

    args = parser.parse_args(sys.argv[1:])

    ss = SourceSpec(url=args.url, target_format=args.format, encoding=args.encoding, resource_format=args.urlfiletype)

    contents = list(enumerate_contents(ss, cache_fs=cache))

    if args.info:
        prt(tabulate(ss.dict.items()))
        sys.exit(0)

    if args.enumerate:
        for s in contents:
            print(s.rebuild_url())

    elif args.intuit:
        for s in contents:

            try:
                encoding, ri = run_row_intuit(s.rebuild_url(),cache=cache)

                prt("{} headers={} start={} encoding={}".format(
                        s.rebuild_url(),
                        ','.join(str(e) for e in ri.header_lines),
                        ri.start_line,
                        encoding))
            except SourceError as e:
                warn("{}: {}".format(s.rebuild_url(), e))

    elif len(contents) == 1:
        s = contents.pop(0)

        rg = s.get_generator(cache=cache)

        print(tabulate(islice(rg,20)))

    elif len(contents) > 1 and not args.enumerate:
        warn("URL has multiple content files; enumerating instead")
        for s in contents:
            print(s.rebuild_url())

