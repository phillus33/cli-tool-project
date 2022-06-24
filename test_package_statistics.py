"""
Test class for the main functions
"""

import unittest
import os.path
from package_statistics import (
    download_files,
    get_all_content_list,
    get_filtered_content_urls,
    print_top_ten,
)


class TestPackageStatistics(unittest.TestCase):
    """This class is used to test all functions within package_statistics"""

    def setUp(self) -> None:
        """Create variables for use in all test methods."""
        self.url_mirror = "http://ftp.uk.debian.org/debian/dists/stable/main/"
        self.arch = "arm64"
        self.arch_mirror = (
            "http://ftp.uk.debian.org/debian/dists/stable/main/Contents-arm64.gz"
        )
        self.files_list = [
            {
                "file_name": "Contents-all.gz",
                "file_url": "http://ftp.uk.debian.org/debian/dists/stable/main/Contents-all.gz",
                "arch": "all",
                "file_number": 123420,
            },
            {
                "file_name": "Contents-arm64.gz",
                "file_url": "http://ftp.uk.debian.org/debian/dists/stable/main/Contents-arm64.gz",
                "arch": "arm64",
                "file_number": 10,
            },
        ]
        self.files_urls = [
            "http://ftp.uk.debian.org/debian/dists/stable/main/Contents-arm64.gz",
            "http://ftp.uk.debian.org/debian/dists/stable/main/Contents-udeb-arm64.gz",
        ]

    def test_getting_content(self):
        """This method tests the function get_all_content_list()"""
        result = get_all_content_list(self.url_mirror)

        self.assertTrue(isinstance(result, list), "The function did not return a list.")

        self.assertTrue(
            len(result) > 0,
            "The function returned an empty list even though it should find something.",
        )

        self.assertIsNotNone(
            result,
            "Test result is None when it should return a list. No content found.",
        )

    def test_getting_url(self):
        """This method tests the function get_filtered_content_urls()"""
        # Since this method is dependent on the output of another function, I have added a static
        # list as an argument to test the function's logic.This is to avoid cases where the url
        # breaks or indexing changes on the mirror. I'm sure there's a smarter way to do it with
        # Mocks, but I couldn't wrap my head around how it works... for now :^)

        result = get_filtered_content_urls(self.arch, self.files_list)

        self.assertTrue(type(result) == list, "The function did not return a list.")

        self.assertTrue(
            len(result) > 0,
            "The function returned an empty list even though it should find something.",
        )

        self.assertEqual(
            [self.arch_mirror], result, "Test result is not the same as expected."
        )

    def test_download_files(self):
        """This method tests the function download_files()"""
        # This test method checks whether a file with the exact corresponding name has been downloaded and
        # saved in the current working directory by the download_files function.
        # However, it only really works if the corresponding file wasn't downloaded prior.
        download_files(self.files_urls)

        self.assertTrue(
            os.path.exists("Contents-arm64.gz"),
            "The file does not exist or the file name was changed.",
        )

    def test_print_top_ten(self):
        """This method tests the function download_files()"""
        # For transparency I have included a basic test for the None output of the function.
        # Another approach would be redirecting the stdout and asserting it is equal to the expected string (out of scope).
        result = print_top_ten(self.files_list)

        self.assertIsNone(
            result,
            "The return value should be None as it is a console print, but it is not.",
        )


if __name__ == "__main__":
    unittest.main()
