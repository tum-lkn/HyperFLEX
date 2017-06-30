#! /usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'Patrick Kalmbach, patrick.kalmbach@tum.de'

from setuptools import setup, find_packages


setup(
    name="hyperflexcore",
    version="0.9",
    description="Distributed Hypervisor for Software-Defined Networks",
    license="BSD",
    keywords="Virtualization, SDN",
    packages=find_packages(exclude=['tests*', 'docu*', 'misc*']),
    data_files=[(
        os.path.join(os.path.expanduser, '.config', 'hyperflex'),
        ['hyperflexcore/config.cfg']
        )],
    include_package_data=True,
)
