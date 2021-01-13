#
# Copyright (c) 2021 Carsten Igel.
#
# This file is part of celery-stubs
# (see https://github.com/carstencodes/celery-stubs).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#

import sys
import os

file_path = os.path.abspath(os.path.dirname(__file__))
dir_path = os.path.dirname(file_path)
src_path = os.path.join(dir_path, "src")

src_path = os.path.realpath(src_path)

sys.path.insert(0, src_path)
print(sys.path)
