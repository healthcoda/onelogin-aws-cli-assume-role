"""
Static User Configuration models
"""
import configparser

from onelogin_aws_cli.userquery import user_choice


class ConfigurationFile(configparser.ConfigParser):
    """
    Represents a configuration ini file on disk
    """

    def __init__(self, config_file):
        super().__init__(default_section='defaults')

        self['defaults'] = dict(save_password=False)

        self.file = config_file

        self.read_file(self.file)

    @property
    def is_initialised(self) -> bool:
        """
        True if there is at least one section
        """
        return len(
            self.sections()
        ) > 0

    def initialise(self, config_name='default'):
        """
        Prompt the user for configurations, and save them to the
        onelogin-aws-cli config file
        """
        print("Configure Onelogin and AWS\n\n")
        config_section = self.section(config_name)

        config_section['base_uri'] = user_choice(
            "Pick a Onelogin API server:", [
                "https://api.us.onelogin.com/",
                "https://api.eu.onelogin.com/"
            ]
        )

        print("\nOnelogin API credentials. These can be found at:\n"
              "https://admin.us.onelogin.com/api_credentials")
        config_section['client_id'] = input("Onelogin API Client ID: ")
        config_section['client_secret'] = input("Onelogin API Client Secret: ")
        print("\nOnelogin AWS App ID. This can be found at:\n"
              "https://admin.us.onelogin.com/apps")
        config_section['aws_app_id'] = input("Onelogin App ID for AWS: ")
        print("\nOnelogin subdomain is 'company' for login domain of "
              "'comany.onelogin.com'")
        config_section['subdomain'] = input("Onelogin subdomain: ")

        self.save()

    def save(self):
        """
        Save this config to disk
        """
        self.write(self.file)
        print("Configuration written to '{}'".format(self.file))

    def section(self, section_name: str):
        """
        Return a Section object representing a single section within the
        onelogin config file.

        :param section_name: Name of the section in the config file
        :return:
        """
        if not self.has_section(section_name):
            self.add_section(section_name)
        return Section(section_name, self)


class Section(object):
    """
    Represents a single section in an ini file
    """

    def __init__(self, section_name: str, config: ConfigurationFile):
        self.config = config
        self.section_name = section_name

    @property
    def can_save_password(self) -> bool:
        """
        If the user has specified that the password can be saved to the system
        keychain
        :return:
        """
        return self.config.getboolean(self.section_name, "save_password")

    def __setitem__(self, key, value):
        self.config.set(self.section_name, key, value)

    def __getitem__(self, item):
        return self.config.get(self.section_name, item)

    def __contains__(self, item):
        return self.config.has_option(self.section_name, item)
