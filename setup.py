"""MSMBuilder3: WIP

Description
"""

DOCLINES = __doc__.split("\n")

import os
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

##########################
VERSION = "3.0.0"
ISRELEASED = False
__version__ = VERSION
##########################

def find_packages():
    packages = []
    for dir,subdirs,files in os.walk('msmbuilder3'):
        package = dir.replace(os.path.sep, '.')
        if '__init__.py' not in files:
            # not a package
            continue
        packages.append(package)
    return packages

build_doc = 'doc' in sys.argv
if build_doc:
    sys.argv.remove('doc')

setup(name='msmbuilder3',
      author_email='rmcgibbo@gmail.com',
      description=DOCLINES[0],
      long_description="\n".join(DOCLINES[2:]),
      version=__version__,
      zip_safe=False,
      license='GPLv3+',
      platforms=["Linux", "Mac OS-X", "Unix"],
      packages=find_packages(),
      install_requires=['mdtraj'],
      scripts=['msmb'],
)

if build_doc:
    os.chdir(os.path.join(os.path.dirname(__file__), 'doc'))
    os.system('make html')
