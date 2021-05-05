import unittest
from unittest.mock import patch
from WebAnalyser import WebAnalyser


class TestWebAnalyser(unittest.TestCase):

    def test_get_html(self):
        analyser = WebAnalyser()
        analyser.get_html("https://lipsum.com/")
        self.assertIsNotNone(analyser.soup, "HTML should not be None")

    def test_longest_paths(self):
        analyser = WebAnalyser()
        analyser.get_html("https://lipsum.com/")
        analyser.recursive_children(analyser.soup)
        self.assertTrue(analyser.longest_paths, "Could not find any tags")

    def test_longest_path_len(self):
        analyser = WebAnalyser()
        analyser.get_html("https://lipsum.com/")
        analyser.recursive_children(analyser.soup)
        self.assertEqual(max(analyser.longest_paths, key=int), 16, "Incorrect path length")

    def test_main(self):
        analyser = WebAnalyser()
        with patch('builtins.print') as mock_print:
            with patch('builtins.input', return_value="https://lipsum.com/") as mock_input:
                analyser.main()
                self.assertTrue(analyser.tags, "Could not find any tags")
                self.assertEqual(analyser.most_common_tag, "a", "Should be a")
                self.assertIsInstance(analyser.path_to_popular_tag, tuple, "WebAnalyser.path_to_popular_tag Should be tuple")


if __name__ == '__main__':
    unittest.main()
