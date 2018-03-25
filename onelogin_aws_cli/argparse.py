"""
CLI Argument Parser
"""

import argparse

import pkg_resources


class OneLoginAWSArgumentParser(argparse.ArgumentParser):
    """Argument Parser separated into daemon and cli tool"""

    def __init__(self):
        super().__init__(description='Login to AWS with OneLogin')

        self.add_argument(
            '-C', '--config-name', default='default', dest='config_name',
            help='Switch configuration name within config file'
        )

        self.add_argument(
            '--profile', default='', help='Specify profile name of credential'
        )

        self.add_argument(
            '-u', '--username', default='', help='Specify OneLogin username'
        )

        version = pkg_resources.get_distribution(__package__).version
        self.add_argument(
            '-v', '--version', action='version',
            version="%(prog)s " + version
        )

    def add_cli_options(self):
        """Add Argument Parser options only used in the CLI entrypoint"""

        renew_seconds_group = self.add_mutually_exclusive_group()

        renew_seconds_group.add_argument(
            '-r', '--renew-seconds', type=int,
            help='Auto-renew credentials after this many seconds'
        )

        renew_seconds_group.add_argument(
            # Help is suppressed as this is replaced by the POSIX friendlier
            # version above. This is here for legacy compliance and will
            # be deprecated.
            '--renewSeconds', type=int, help=argparse.SUPPRESS,
            dest='renew_seconds_legacy'
        )

        self.add_argument(
            '-c', '--configure', dest='configure', action='store_true',
            help='Configure OneLogin and AWS settings'
        )

        # The `--client` option is a precursor to the daemon process in
        # https://github.com/physera/onelogin-aws-cli/issues/36
        # self.add_argument("--client", dest="client_mode",
        #                   action='store_true')

        return self
