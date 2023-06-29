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
import pathlib
import shutil
import subprocess
import sys
import tempfile

from catkin_pkg.package import parse_package

sys.path.append(os.path.dirname(__file__))

from rosidl_adapter.msg import convert_msg_to_idl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir")
    parser.add_argument("output_dir")
    args = parser.parse_args(sys.argv[1:])

    package_dir = pathlib.Path(args.package_dir).absolute()
    interface_files = package_dir.glob("**/*.msg")
    pkg = parse_package(package_dir)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir) / pathlib.Path(pkg.name)

        for interface_file in interface_files:
            convert_msg_to_idl(
                package_dir,
                pkg.name,
                interface_file.relative_to(package_dir),
                tmp_dir,
            )

        subprocess.run(
            [
                "fastddsgen",
                "-ppDisable",
                "-typeros2",
                "-d",
                tmp_dir,
                *tmp_dir.glob("*.idl"),
            ]
        )

        generated = filter(lambda x: x.suffix in [".cxx", ".h"], tmp_dir.iterdir())
        output_dir = pathlib.Path(args.output_dir) / pathlib.Path(pkg.name)
        output_dir.mkdir(parents=True, exist_ok=True)
        for file in generated:
            shutil.copy2(file, output_dir)
