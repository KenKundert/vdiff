from setuptools import setup
from textwrap import dedent

setup(
    name='vdiff',
    description=dedent("""\
        Opens two files in vimdiff.
        Maps various keys to make updating the files efficient.
    """),
    author="Ken Kundert",
    author_email='theNurd@nurdletech.com',
    scripts=['vdiff'],
    py_modules=['vdiff'],
    license='GPLv3'
)

# vim: set sw=4 sts=4 et: