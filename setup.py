from codecs import open

from setuptools import setup

with open("README.rst", encoding="utf-8") as f:
    readme = f.read()

setup(
    name = "vdiff",
    version = "2.6.0",
    author = "Ken Kundert",
    author_email = "vdiff@nurdletech.com",
    description = "Efficiently manage the differences between two files using vim.",
    long_description = readme,
    long_description_content_type = 'text/x-rst',
    url = "http://nurdletech.com/linux-utilities/vdiff",
    download_url = "https://github.com/kenkundert/vdiff/tarball/master",
    packages = ["vdiff"],
    entry_points = {"console_scripts": ["vdiff=vdiff.main:main"]},
    install_requires = [
        "docopt",
        "inform>=1.2",
        "shlib>=0.8",
        "appdirs",  # optional, needed for user configuration
    ],
    zip_safe = True,
    license = "GPLv3+",
    keywords = ["vim", "diff"],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
)

# vim: set sw=4 sts=4 et:
