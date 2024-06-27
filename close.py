#! /usr/bin/python3
# vim: file encoding=utf-8 et sw=4

# Copyright (C) 2009 Jacek Konieczny <jajcus@jajcus.net>
# Copyright (C) 2009 Andrzej Zaborowski <balrogg@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


"""
Closes a changeset, given id.
"""

__version__ = "$Revision: 21 $"

import sys
import traceback

from osmapi import HTTPError, OSM_API

try:
    version = 2
    if len(sys.argv) != 2:
        sys.stderr.write("Synopsis:\n")
        sys.stderr.write("    %s <changeset-id>\n" % sys.argv[0])
        sys.exit(1)

    api = OSM_API()
    api.changeset = int(sys.argv[1])
    api.close_changeset()
except HTTPError as err:
    sys.stderr.write(err.args[1])
    sys.exit(1)
except Exception as err:
    sys.stderr.write(str(err) + "\n")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
