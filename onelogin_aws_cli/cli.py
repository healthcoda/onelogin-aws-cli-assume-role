"""
Collections of entrypoints
"""
import argparse
import signal
import sys
from threading import Event

import pkg_resources

from onelogin_aws_cli import DEFAULT_CONFIG_PATH, OneloginAWS
from onelogin_aws_cli.configuration import ConfigurationFile
from onelogin_aws_cli.model import SignalRepr


def login(args=sys.argv[1:]):
    """
    Entrypoint for `onelogin-aws-login`
    :param args:
    """
    version = pkg_resources.get_distribution('pip').version

    parser = argparse.ArgumentParser(description="Login to AWS with Onelogin")
    parser.add_argument("-c", "--configure", dest="configure",
                        action="store_true",
                        help="Configure Onelogin and AWS settings")
    parser.add_argument("-C", "--config_name", default="default",
                        help="Switch configuration name within config file")
    parser.add_argument("--profile", default="",
                        help="Specify profile name of credential")
    parser.add_argument("-u", "--username", default="",
                        help="Specify OneLogin username")
    parser.add_argument("-r", "--renewSeconds", type=int,
                        help="Auto-renew credentials after this many seconds")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + version)

    args = parser.parse_args(args)

    with open(DEFAULT_CONFIG_PATH, 'a+') as fp:
        fp.seek(0, 0)
        configFile = ConfigurationFile(fp)

    if args.configure or not configFile.is_initialised:
        configFile.initialise()

    config_section = configFile.section(args.config_name)

    if config_section is None:
        sys.exit("Configuration '{}' not defined. "
                 "Please run 'onelogin-aws-login -c'".format(args.config_name))

    api = OneloginAWS(config_section, args)
    api.save_credentials()

    if args.renewSeconds:

        interrupted = Event()

        def _interrupt_handler(signal_num: int, *args):
            interrupted.set()
            print("Received {sig}.".format(sig=SignalRepr(signal_num)))
            print("Shutting down Credentials refresh process...")

        # Handle sigterms
        # This must be done here, as signals can't be caught down the stack
        for sig_type in list(SignalRepr):
            signal.signal(sig_type.value, _interrupt_handler)

            # @TODO We should check if the credentials are going to expire
            # in the immediate future, rather than constantly hitting
            # the AWS API.

        interrupted.clear()
        while not interrupted.is_set():
            interrupted.wait(args.renewSeconds)
            api.save_credentials()
