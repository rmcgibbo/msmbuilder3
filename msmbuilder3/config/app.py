"""Base class for MSMBuilder commands
"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function
# stdlib imports
import os
import logging
import itertools

# ipython imports
from IPython.config.application import Application
from IPython.config.configurable import SingletonConfigurable
from IPython.utils.traitlets import Bool, Enum, Unicode
from IPython.utils.text import indent, dedent, wrap_paragraphs, marquee
from IPython.config.loader import ConfigFileNotFound

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------


class ConfigurationError(Exception):
    pass


class MSMBuilderApp(Application):
    #######################################################################
    # BEGIN options that need to be overridden in every subclass (subapp)
    #######################################################################
    name = None
    path = None
    short_description = None
    long_description = None
    reference = None
    subcommands = None
    #######################################################################
    # END options that need to be overridden in every subclass (subapp)
    #######################################################################

    option_description = u''

    display_banner = Bool(False, config=False,
        help="Whether to display a banner upon starting MSMBuilder.")

    # Make log settings NOT configurable, so that we don't clog up the --help-all
    # with useless information
    log_level = 10
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    log_format = '[%(name)s]%(highlevel)s %(message)s'
    def _config_changed(self, name, old, new):
        SingletonConfigurable._config_changed(self, name, old, new)

    input = Unicode('input', help='Input data source (file). Path to one or more timeseries or trajectory files.', config=True)
    output = Unicode('output', help='Output data source (file). The form of the output depends on the subcommand invoked.', config=True)

    def __init__(self, *args, **kwargs):
        super(MSMBuilderApp, self).__init__(*args, **kwargs)

        # Hack to get all of the configurables defined in the subclass
        # show up in the alias table
        self.aliases = {}
        for key in self.__class__.class_traits(config=True):
            if not hasattr(MSMBuilderApp, key):
                self.aliases[key] = '%s.%s' % (self.__class__.__name__, key)
        
        self.aliases['input'] = 'MSMBuilderApp.input'
        self.aliases['output'] = 'MSMBuilderApp.output'

    def print_description(self):
        "Print the application description"
        lines = ['']
        lines.append(wrap_paragraphs(self.short_description)[0])
        lines.append('='*min(79, len(lines[-1])))
        lines.append('')

        if self.long_description:
            for l in wrap_paragraphs(self.long_description):
                lines.append(l)
                lines.append('')

        if self.reference:
            lines.append('Reference\n---------')
            for l in wrap_paragraphs(self.reference):
                lines.append(l)
                lines.append('')

        print(os.linesep.join(lines))

    def initialize(self, argv=None):
        """Do the first steps to configure the application, including
        finding and loading the configuration file"""
        # load the config file before parsing argv so that
        # the command line options override the config file options
        super(MSMBuilderApp, self).initialize(argv)
        for subconfig in self.config.values():
            if 'input' in subconfig:
                self.config['MSMBuilderApp'].input = subconfig.input
            if 'output' in subconfig:
                self.config['MSMBuilderApp'].output = subconfig.output

    def print_subcommands(self):
        """Print the list of subcommands under this application"""

        if not self.subcommands:
            return

        lines = ["Subcommands"]
        lines.append('-'*len(lines[0]))
        for subc, (cls, help) in self.subcommands.iteritems():
            lines.append(subc)
            if help:
                lines.append(indent(dedent(help.strip())))
        lines.append('')

        print(os.linesep.join(lines))

    def print_help(self, classes=False):
        """Print the help for each Configurable class in self.classes.

        If classes=False (the default), only flags and aliases are printed.
        """
        self.print_description()
        self.print_subcommands()
        self.print_options()

        if classes:
            for cls in self.classes:
                if isinstance(self, cls):
                    # Skip reshowing options for my class
                    continue
                cls.class_print_help(ignore_from=MSMBuilderApp)
                print()
        else:
            print("To see all available configurables, use `--help-all`")
            print()

        self.print_examples()

    @classmethod
    def class_print_help(cls, ignore_from=None):
        print(cls.class_get_help(ignore_from=ignore_from))

    @classmethod
    def class_get_help(cls, inst=None, ignore_from=None):
        """Get the help string for this class in ReST format.
        
        If `inst` is given, it's current trait values will be used in place of
        class defaults.
        
        If `ignore_from` is given, it should be a superclass of cls. Any traits
        on cls that are inherited from ignore_from will be skipped.
        """
        assert inst is None or isinstance(inst, cls)
        final_help = []
        final_help.append(u'%s options' % cls.__name__)
        final_help.append(len(final_help[0])*u'-')
        for k, v in sorted(cls.class_traits(config=True).iteritems()):
            if ignore_from is not None:
                if hasattr(ignore_from, k):
                    continue
            help = cls.class_get_trait_help(v, inst)
            final_help.append(help)
        return '\n'.join(final_help)

    def print_options(self):
        #import IPython as ip
        #ip.embed()

        if not self.flags and not self.aliases:
            return
        lines = ['%s options' % self.__class__.name]
        lines.append('-'*len(lines[0]))
        print(os.linesep.join(lines))
        self.print_flag_help()
        self.print_alias_help()
        print()

    def error(self, msg='Error', extra=None):
        if extra is None:
            self.log.error(msg)
        else:
            self.log.error(msg, extra)
        self.exit(1)


class RootApplication(MSMBuilderApp):
    name = 'msmb'
    path = 'base.MSMBuilderApp'
    short_description = ('MSMBuilder: Software for building Markov '
                         'State Models for Biomolecular Dynamics')
    long_description = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi sed nibh ut orci
suscipit scelerisque. Sed ligula augue, blandit ac eleifend eleifend, dapibus
ac sapien. Duis eu tortor ac erat porta vulputate. Phasellus ac nisl quis magna
eleifend tempor feugiat vehicula odio. Praesent porta, nunc vel eleifend
elementum, sem justo dapibus massa, sed ultrices sapien felis nec urna.
Praesent et congue orci. Quisque diam turpis, volutpat vitae viverra at,
sodales eget orci. Etiam et condimentum lectus. Nullam mollis egestas lobortis.
Donec lorem odio, ullamcorper at imperdiet ut, commodo a neque. Suspendisse
tristique  ligula nec tellus viverra rhoncus. Vivamus viverra, sapien at
elementum congue, quam nibh egestas nulla, vitae convallis diam est at."""

    def start(self):
        """Start the application's main loop.

        This will be overridden in subclasses"""
        if self.subapp is not None:
            return self.subapp.start()
        else:
            # if they don't choose a subcommand, display the help message
            self.parse_command_line('--help')
    
    def initialize(self, argv=None):
        super(RootApplication, self).initialize(argv)
        if self.display_banner:
            print('DRAWING MSMBUILDER BANNER')
            print('PLEASE CITE US?')

#-----------------------------------------------------------------------------
# Utility functions
#-----------------------------------------------------------------------------

def collect_subcommands():
    """Collect all of the subclasses of `MSMBuilderApp` that have been
    imported

    Returns
    -------
    subcommands : dict
        The keys in the dict are the `name` field of the subclass, and the
        values are the `path` field and the `short_description`.

    Examples
    --------
    >>> from msmb.commands import *
    >>> application.subcommands = collect_subcommands()
    """
    subcommands = {}
    for subclass in MSMBuilderApp.__subclasses__():
        if subclass.name in subcommands:
            msg = ('subcommand %s is not unique. you need to override'
                   ' it in your new subclass' % subclass.name)
            raise ConfigurationError(msg)
        if subclass != RootApplication:
            subcommands[subclass.name] = (subclass.path,
                                          subclass.short_description)
    return subcommands

