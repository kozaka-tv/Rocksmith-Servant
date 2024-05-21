import unittest
from unittest.mock import patch
from utils.cmd_line_parser import parse_args

class TestCmdLineParser(unittest.TestCase):

    @patch('sys.argv', ['run.py'])
    def test_defaults(self):
        config, database = parse_args()
        self.assertEqual(config, 'config/config.ini')
        self.assertEqual(database, 'servant.db')

    @patch('sys.argv', ['run.py', '-c', 'custom_config.ini'])
    def test_custom_config(self):
        config, database = parse_args()
        self.assertEqual(config, 'custom_config.ini')
        self.assertEqual(database, 'servant.db')

    @patch('sys.argv', ['run.py', '-db', 'custom_servant.db'])
    def test_custom_database(self):
        config, database = parse_args()
        self.assertEqual(config, 'config/config.ini')
        self.assertEqual(database, 'custom_servant.db')

    @patch('sys.argv', ['run.py', '-c', 'custom_config.ini', '-db', 'custom_servant.db'])
    def test_custom_config_and_database(self):
        config, database = parse_args()
        self.assertEqual(config, 'custom_config.ini')
        self.assertEqual(database, 'custom_servant.db')

    @patch('sys.argv', ['run.py', '-c', 'custom_config.txt'])
    def test_invalid_config_extension(self):
        with self.assertRaises(ValueError) as cm:
            parse_args()
        self.assertEqual(str(cm.exception), "The configuration file must have a '.ini' extension.")

    @patch('sys.argv', ['run.py', '-db', 'custom_servant.txt'])
    def test_invalid_database_extension(self):
        with self.assertRaises(ValueError) as cm:
            parse_args()
        self.assertEqual(str(cm.exception), "The database file must have a '.db' extension.")

if __name__ == '__main__':
    unittest.main()
