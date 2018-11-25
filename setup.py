#!/usr/bin/env python3

from pycq.version import title, description, url, author, author_email, license, version
from setuptools import setup, find_packages


def install_deps():
    with open('requirements.txt', 'r') as f:
        packages = f.readlines()
        new_pkgs = []
        links = []
        for resource in packages:
            if 'git+https' in resource:
                pkg = resource.split('#')[-1]
                links.append(resource.strip() + '-9876543210')
                new_pkgs.append(pkg.replace('egg=', '').rstrip())
            else:
                new_pkgs.append(resource.strip())
        return new_pkgs, links


pkgs, new_links = install_deps()

setup(
    name=title,
    description=description,
    long_description=url,
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    version=version,

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],

    keywords='cockroachdb postgresql distributed queue',
    py_modules=["pycq"],
    python_requires=">=3.6",
    packages=find_packages(),
    include_package_data=True,
    dependency_links=new_links,
    install_requires=pkgs,
)
