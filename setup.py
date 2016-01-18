from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='vdiff',
    version='2.1.1',
    author='Ken Kundert',
    author_email='vdiff@nurdletech.com',
    description='Efficiently manage the differences between two files using vim.',
    long_description=readme,
    url='https://github.com/kenkundert/vdiff',
    license='GPLv3+',
    packages=[
        'vdiff',
    ],
    entry_points = {
        'console_scripts': ['vdiff=vdiff.main:main'],
    },
    install_requires=[
        'docopt',
        'inform',
        'shlib',
    ],
    keywords=[
        'vim',
        'diff',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
)

# vim: set sw=4 sts=4 et:
