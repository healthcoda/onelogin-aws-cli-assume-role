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

        self.file = config_file

        self.read_file(self.file)

    def initialise(self):
        """
        Prompt the user for configurations, and save them to the
        onelogin-aws-cli config file
        """
        print("Configure Onelogin and AWS\n\n")
        default = self.section("default")

        default['base_uri'] = user_choice("Pick a Onelogin API server:", [
            "https://api.us.onelogin.com/",
            "https://api.eu.onelogin.com/"
        ])

        print("\nOnelogin API credentials. These can be found at:\n"
              "https://admin.us.onelogin.com/api_credentials")
        default['client_id'] = input("Onelogin API Client ID: ")
        default['client_secret'] = input("Onelogin API Client Secret: ")
        print("\nOnelogin AWS App ID. This can be found at:\n"
              "https://admin.us.onelogin.com/apps")
        default['aws_app_id'] = input("Onelogin App ID for AWS: ")
        print("\nOnelogin subdomain is 'company' for login domain of "
              "'comany.onelogin.com'")
        default['subdomain'] = input("Onelogin subdomain: ")

        self.save()

    def save(self):
        """
        Save this config to disk
        """
        self.write(self.file)
        print("Configuration written to '{}'".format(self.file))

    def section(self, section_name):
        """
        Return a single config file section to disk
        :param section_name:
        :return:
        """
        if not self.has_section(section_name):
            self.add_section(section_name)
        return Section(section_name, self)


class Section(object):
    """
    Represents a single section in an ini file
    """

    def __init__(self, section_name, config: ConfigurationFile):
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