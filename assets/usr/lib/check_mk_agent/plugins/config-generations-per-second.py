#!/usr/bin/env python3

# (c) Copyright 2025 Y0d0g MiMiMi <github@stippmilch.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# Version 2 along with this program. If not, see
# <https://www.gnu.org/licenses/old-licenses/gpl-2.0.html>.
# SPDX-License-Identifier: GPL-2.0

try:
    from pprintpp import pprint as pp
except ImportError:
    from pprint import pprint as pp

import json
import glob
import os

# dict for output
output = {}

# this will contain a list of services
output["services"] = {}

for basepath in glob.glob("/opt/omd/sites/*"):
    site = os.path.basename(basepath)
    filepath = f"/opt/omd/sites/{site}/var/check_mk/wato/config-generation.mk"

    if os.path.isfile(filepath):
        with open(filepath, "r") as file:
            rate = file.read().strip()

        output["services"][f"Config generation {site}"] = {
                "summary": f"Config generation {site}",
                "details": f"Config generation {site}",
                "metrics": {"rate": f"{rate}c"},
        }


print("<<<universaljson:sep(0)>>>")
print(json.dumps(output))
