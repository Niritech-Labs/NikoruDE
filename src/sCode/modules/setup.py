# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
from setuptools import setup, Extension
import pybind11
import os

include_dirs = [
    pybind11.get_include(),
    "/usr/include",
    "/usr/include/libdrm",
    "/usr/include/x86_64-linux-gnu",  # Для некоторых систем
    "/usr/include/i386-linux-gnu"    # Для 32-битных систем
]

# Удаляем дубликаты и несуществующие пути
include_dirs = list(set(filter(os.path.exists, include_dirs)))


DRMUtils = Extension(
    'DRMUtils',
    sources=['/home/desk/Desktop/NiraLinux-project/NikoruDE/main/src/sCode/modules/DRMRes.cpp'],
    libraries=['drm'],
    extra_compile_args=['-std=c++11','-Wall','-Wextra'],
    include_dirs=include_dirs,
)

setup(
    name='DRMUtils',
    version='0.1',
    description='DRM/KMS resolution control module',
    ext_modules=[DRMUtils],
)