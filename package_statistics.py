"""
A CLI tool to download Debian packages according to the specified architecture.

Assumptions:
    1. The user is looking for both udeb and non-udeb packages.
    2. The user only ever downloads packages from the default mirror.

Out of scope:
    1. Udeb files: Discerning between udeb and non-udeb files in the program logic.
    2. Custom URL: Testing for usability on other mirrors with differing file names and endings.
    3. Download location: Downloads are saved to a custom location on local drive.
    4. Top n: User decides how many top packages they want to be displayed.
"""
# Adding the shebang so the user doesn't have to manually type python beforehand.
# Also indicates compatibility only with Python 3
# See also: https://stackoverflow.com/questions/6908143/should-i-put-shebang-in-python-scripts-and-what-form-should-it-take
#!/usr/bin/env python3

import argparse
from urllib.error import HTTPError
import urllib.request
import os


def get_all_content_list(url_mirror: str) -> list:
    """
    Returns a list of all content files available on the mirror

        Params:
            url_mirror: The url of where the content files will be found

        Returns:
            list: A list of dictionaries used for further parsing. Example structure below

                [
                    {
                        "file_name": "Contents-arm64.gz,
                        "file_url": "http://ftp.uk.debian.org/debian/dists/stable/main/Contents-arm64.gz"
                        "arch": "arm64"
                        "file_number": 123420
                    }

                ]
    """
    try:
        with urllib.request.urlopen(url_mirror) as response:
            html = response.read()
            payload = html.decode()
    except HTTPError as http_error:  # This will catch 4xx and 5xx http responses
        print(http_error)
        print(
            "There was an issue with the request and nothing was downloaded. The program will now exit."
        )
    except Exception:
        print(
            "There was an unexpected issue and nothing was downloaded. The program will now exit."
        )  # This will catch any other possible errors not caught by the http error

    # This list will hold a dictionary per relevant file/package
    contents = []
    for line in payload.split("\r\n"):
        # Only these lines have number of files associated with them
        if '<a href="Contents' in line:
            file_name = line[line.find("Contents") : line.find(".gz") + 3]
            # In case a custom mirror (out of scope) misses the '/' it will be added automatically
            file_url = (
                url_mirror + file_name
                if url_mirror[-1] == "/"
                else url_mirror + "/" + file_name
            )
            arch = file_name[file_name.rfind("-") + 1 : file_name.rfind(".gz")]
            # Since associated file number will always be the last info in the line this works
            # Must be int type to sort by this value later on
            file_number = int(line[line.rfind(" ") + 1 :])
            contents.append(
                {
                    "file_name": file_name,
                    "file_url": file_url,
                    "arch": arch,
                    "file_number": file_number,
                }
            )
    return contents


def get_filtered_content_urls(arch: str, all_files: list) -> list:
    """
    Returns a list of URLs for user-chosen architecture

        Params:
            arch: The architecture to filter for
            all_files: A list for all available file(-names, -urls, architectures)

        Returns:
            list: The list of files where unwanted architectures are filtered out. Example structure

                ['http://ftp.uk.debian.org/debian/dists/stable/main/Contents-arm64.gz',
                'http://ftp.uk.debian.org/debian/dists/stable/main/Contents-udeb-arm64.gz']
    """
    # All URLs are filtered for those that contain the desired architecture
    urls = []
    for file in all_files:
        url = file["file_url"]
        if file["arch"] == arch:
            urls.append(url)
    return urls


def download_files(url_list: list, verbose: bool = False) -> None:
    """
    Takes a list of valid URL string(s), download the corresponding package(s) to the current
    working dir and returns nothing. Prints file names and file location upon successful download.

        Params:
            url_list: List of at lease one URL string pointing directly at the package's download link
            verbose: Bool value from optional CLI argument indicating download verbosity

        Returns:
            None
    """
    # The try except blocks are set up to mainly catch errors caused by faulty URLs.
    # If one URL is faulty, the other one(s) are probably too since downloads relate
    # to one specific architecture. In the unlikely event that one of multiple faulty
    # URLs is working, the corresponding package will be downloaded only if it is at
    # first position in the input URL list.
    try:
        work_dir = os.getcwd()

        for url in url_list:
            file_name = url[url.find("Contents") : url.find(".gz") + 3]
            if verbose:
                print(f"Downloading {file_name}. Hold tight...")
            urllib.request.urlretrieve(url, file_name)
        if verbose:
            # If the input list contains only one item print file name and save location
            # Else for each item in the list...
            # figure out its name including the ending...
            # and concatenate each of those items seperated by a ', ' and print names + loc
            print(
                f"{file_name} saved to {work_dir}"
                if len(url_list) == 1
                else f"{', '.join([url[url.find('Contents'):url.find('.gz')+3] for url in url_list])} saved to {work_dir}\n"
            )
    except HTTPError as http_error:  # This will catch 4xx and 5xx http responses
        print(http_error)
        print(
            "There was an issue with the request and nothing was downloaded. The program will now exit."
        )
    except Exception:
        print(
            "There was an unexpected issue and nothing was downloaded. The program will now exit."
        )  # This will catch any other possible errors not caught by the http error


def print_top_ten(all_files_list: list) -> None:
    """
    Takes a list of all found packages on the mirror and prints the top ten packages
    ordered by their respective files associated.

        Param:
            all_files_list: List of dicts each containing file name,  url, architecture and number of files

        Returns:
            None
    """
    # TODO: Make this function work with custom number of top packages
    # Using a lambda function that sorts the list of dictionaries by each dict's file_number value
    sorted_list = sorted(all_files_list, key=lambda x: x["file_number"], reverse=True)

    for i, item in enumerate(sorted_list, start=1):
        # Reserve 25 characters for the file_name for pretty formatting
        print(f"{i:4}. {item['file_name']:25}{item['file_number']}")
        if i == 10:
            break


def cli_parser():
    """Main function for CLI which parses user input into usable arguments"""
    # TODO: add a flag for seperating udeb files
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "arch",
        help=(
            "The architecture of the compressed Contents file to download: "
            "'amd64', 'arm64', 'armel', 'armhf', 'i386', 'mips64el', 'mipsel'"
            "'ppc64el', 's390x', 'source', 'all'"
        ),
        type=str,
    )
    # Out of scope: User is able to change the URL to look for packages.
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        default="http://ftp.uk.debian.org/debian/dists/stable/main/",
        help="The mirror where the content files can be found. Default is set to http://ftp.uk.debian.org/debian/dists/stable/main/",
    )
    # A little extra because argparse is fun! If specified, shows what files are being downloaded and where they are saved to.
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity for downloads",
    )
    args = parser.parse_args()
    return args.arch, args.url, args.verbose


def main():
    """The entry function to call all other functions in this module"""
    arch, url_mirror, verbose = cli_parser()
    arch = arch.lower()
    all_files_list = get_all_content_list(url_mirror)
    filtered_urls = get_filtered_content_urls(arch, all_files_list)
    download_files(filtered_urls, verbose)
    print_top_ten(all_files_list)


# Put the main function in here to prevent automatic execution of script when importing the module
if __name__ == "__main__":
    main()
