import os
import yaml
import trafaret
import unittest

from trafaret_config import ConfigError

from griphook.config.config import Config, BASE_DIR

from unittest import mock


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.CONFIG_FILE_PATH = os.path.join(BASE_DIR, "config.yml")

        self.test_template = trafaret.Dict({
            "api": trafaret.String(),
            "cli": trafaret.String(),
            "tasks": trafaret.String(),
            "db": trafaret.Dict({
                "DATABASE_URL": trafaret.String(),
                "EXPIRES_TIME": trafaret.Int(),
            }),

        })
        self.test_data = {
            "api": "value",
            "cli": "value",
            "tasks": "value",
            "db": {
                "DATABASE_URL": "URL",
                "EXPIRES_TIME": 1,
            },
        }

        self.current_config_data = {
            "api": {
                "GRAPHITE_URL": "url_here"
            },
            "db": {
                "DATABASE_URL": "url here"
            },
            "tasks": {
                "DATA_SOURCE_DATA_EXPIRES": 1,
                "CELERY_BROKER_URL": "test",
                "TRYING_SETUP_PARSER_INTERVAL": 1,
                "PARSE_METRIC_EXPIRES": 1,
                "DATA_GRANULATION": 1,
            },
        }

    def tearDown(self):
        os.remove(self.CONFIG_FILE_PATH)

    def write_yml_config(self, data):
        with open(self.CONFIG_FILE_PATH, "w") as file:
            yaml.dump(data, file, default_flow_style=False)

    def test_correct_config(self):
        data = self.test_data
        self.write_yml_config(data)

        options = Config(self.test_template).options
        self.assertEqual(options, data)

    def test_wrong_config_data(self):
        data = {
            "api": "value",
            "cli": "value",
            "tasks": 1,
            "db": {
                "DATABASE_URL": "URL",
                "EXPIRES_TIME": 1,
            },
        }
        self.write_yml_config(data)

        with self.assertRaises(SystemExit):
            with self.assertRaises(ConfigError):
                Config(self.test_template)

    def test_current_config(self):
        data = self.current_config_data

        self.write_yml_config(data)

        options = Config().options
        self.assertEqual(options, data)

    def test_overwriting_options_from_env_of_current_template(self):
        data = self.current_config_data

        self.write_yml_config(data)
        data["tasks"]["CELERY_BROKER_URL"] = "new_value"

        os.environ["GH_CELERY_BROKER_URL"] = "new_value"
        config = Config()

        self.assertEqual(config.options, data)

    @mock.patch.dict(os.environ, {'GH_EXPIRES_TIME': 'str'})
    def test_overwriting_by_env_variable_with_wrong_type(self):
        data = self.test_data
        self.write_yml_config(data)

        with self.assertRaises(SystemExit):
            with self.assertRaises(trafaret.DataError):
                Config(self.test_template)


if __name__ == "__main__":
    unittest.main()
