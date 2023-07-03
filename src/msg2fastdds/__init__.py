#!/usr/bin/env python3

# Copyright 2023 Rin Iwai.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from catkin_pkg.package import parse_package

sys.path.append(os.path.dirname(__file__))

from rosidl_adapter.msg import convert_msg_to_idl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dirs", nargs="*")
    parser.add_argument("-o", "--outdir", required=True)
    args = parser.parse_args(sys.argv[1:])

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tmp_idl = tmp / "idl"
        tmp_cxx = tmp / "cxx"

        for pkg_dir in args.package_dirs:
            pkg_dir = Path(pkg_dir).absolute()
            pkg = parse_package(pkg_dir)
            for msg in pkg_dir.glob("**/*.msg"):
                convert_msg_to_idl(
                    pkg_dir,
                    pkg.name,
                    msg.relative_to(pkg_dir),
                    tmp_idl / pkg.name / msg.parent.relative_to(pkg_dir),
                )

        for idl in tmp_idl.glob("**/*.idl"):
            dest = tmp_cxx / idl.parent.relative_to(tmp_idl)
            dest.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "fastddsgen",
                    "-typeros2",
                    "-cs",
                    "-I",
                    tmp_idl,
                    "-d",
                    dest,
                    idl,
                ],
            )

        out_dir = Path(args.outdir)
        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(tmp_cxx, out_dir, dirs_exist_ok=True)
