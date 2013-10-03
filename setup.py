"""MSMBuilder3: WIP

Description
"""

DOCLINES = __doc__.split("\n")

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

##########################
VERSION = "3.0.0"
ISRELEASED = False
__version__ = VERSION
##########################

setup(name='msmbuilder3',
      author_email='rmcgibbo@gmail.com',
      description=DOCLINES[0],
      long_description="\n".join(DOCLINES[2:]),
      version=__version__,
      license='GPLv3+',
      platforms=["Linux", "Mac OS-X", "Unix"],
      packages=['msmbuilder3'],
      package_dir={'msmbuilder3': 'msmbuilder'},
      install_requires=['mdtraj'],
      #scripts=['scripts/mdconvert', 'scripts/mdinspect'],
)
