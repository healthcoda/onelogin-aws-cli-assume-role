"""
Collections of entrypoints
"""
import signal
import sys
from threading import Event

from onelogin_aws_cli import DEFAULT_CONFIG_PATH, OneloginAWS
from onelogin_aws_cli.argparse import OneLoginAWSArgumentParser
from onelogin_aws_cli.configuration import ConfigurationFile
from onelogin_aws_cli.daemon.server import Server
from onelogin_aws_cli.model import SignalRepr


def _get_interrupt_handler(process_type, interrupted: Event = None,
                           interrupt_process=None):
    def _handler(signal_num: int, *args):
        print("Received {sig}.".format(sig=SignalRepr(signal_num)))
        print("Shutting down {process} process...".format(
            process=process_type
        ))

        if interrupted is not None:
            interrupted.set()

        if interrupt_process is not None:
            interrupt_process(signal_num, *args)

    return _handler


def _load_config(parser, config_file: ConfigurationFile, interactive=True,
                 args=sys.argv[1:]):
    cli_args = parser.parse_args(args)

    with open(DEFAULT_CONFIG_PATH, 'a+') as fp:
        fp.seek(0, 0)
        config_file.file = fp
        config_file.load()

    if interactive:
        if cli_args.configure or not config_file.is_initialised:
            config_file.initialise(cli_args.config_name)

    config_section = config_file.section(cli_args.config_name)

    if config_section is None:
        sys.exit(
            "Configuration '{}' not defined. "
            "Please run 'onelogin-aws-login -c'".format(
                cli_args.config_name
            )
        )

    return config_section, cli_args


def daemon(args=sys.argv[1:]):
    """
    Entrypoint for `onelogin-aws-daemon`
    :param args:
    """

    cfg = ConfigurationFile()
    parser = OneLoginAWSArgumentParser()
    config_section, _ = _load_config(parser, cfg, False, args)

    server = Server(config_section)
    _interrupt_handler = _get_interrupt_handler(
        "Daemon", interrupt_process=server.interrupt
    )

    # Handle sigterms
    # This must be done here, as signals can't be caught down the stack
    for sig_type in list(SignalRepr):
        signal.signal(sig_type.value, _interrupt_handler)

    server.run()


def login(args=sys.argv[1:]):
    """
    Entrypoint for `onelogin-aws-login`
    :param args:
    """

    cfg = ConfigurationFile()
    parser = OneLoginAWSArgumentParser().add_cli_options()
    config_section, args = _load_config(parser, cfg, True, args)

    # Handle legacy `--renewSeconds` option while it is depecated
    if args.renew_seconds:
        renew_seconds = args.renew_seconds
    elif args.renew_seconds_legacy:
        print("WARNING: --renewSeconds is depecated in favour of " +
              "--renew-seconds and be removed in a future version.")
        renew_seconds = args.renew_seconds_legacy
    else:
        renew_seconds = None

    api = OneloginAWS(config_section, args)
    api.save_credentials()

    if renew_seconds:

        interrupted = Event()
        _interrupt_handler = _get_interrupt_handler(
            "Credentials refresh", interrupted=interrupted
        )

        # Handle sigterms
        # This must be done here, as signals can't be caught down the stack
        for sig_type in list(SignalRepr):
            signal.signal(sig_type.value, _interrupt_handler)

        interrupted.clear()
        while not interrupted.is_set():
            interrupted.wait(renew_seconds)

            # @TODO We should check if the credentials are going to expire
            # in the immediate future, rather than constantly hitting
            # the AWS API.
            api.save_credentials()
