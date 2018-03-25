import contextlib
from unittest import TestCase
from unittest.mock import patch

from io import StringIO

from onelogin_aws_cli.userquery import user_choice, user_role_prompt


class TestUser_choice(TestCase):

    def test_user_choice(self):
        mock_stdout = StringIO()

        with patch('builtins.input', side_effect=['2']):
            with contextlib.redirect_stdout(mock_stdout):
                result = user_choice('one', ['hallo', 'world', 'foobar'])

        output = mock_stdout.getvalue()
        assert result == "world"
        assert "Invalid option" not in output

    def test_user_choice_bad(self):
        mock_stdout = StringIO()

        with patch('builtins.input', side_effect=['bar', '2']):
            with contextlib.redirect_stdout(mock_stdout):
                result = user_choice('one', ['hallo', 'world', 'foo'])

        output = mock_stdout.getvalue()
        assert result == "world"
        assert "Invalid option" in output

    def test_user_role_prompt(self):
        mock_stdout = StringIO()

        with patch('builtins.input', side_effect=['2']):
            with contextlib.redirect_stdout(mock_stdout):
                selected_role = user_role_prompt([
                    ('mock_role1', 'mock_principal_1'),
                    ('mock_role2', 'mock_principal_2'),
                    ('mock_role3', 'mock_principal_3')
                ])

        self.assertEqual(('mock_role2', 'mock_principal_2'), selected_role)
        self.assertEqual("""[1] mock_role1
[2] mock_role2
[3] mock_role3
""", mock_stdout.getvalue())
