# Python CLI Package Downloader by Philipp Roth


## Summary
<details>
  <summary>Click to expand</summary>
 

This is a python command line tool that takes the architecture (amd64, arm64, mips etc.) as an argument and downloads the compressed Contents file associated with it from the following Debian mirror:
http://ftp.uk.debian.org/debian/dists/stable/main/

The program parses the file and output the statistics of the top 10 packages that have the most files associated with them. 

An example output:

 
```
./package_statistics.py amd64

 

<package name 1>         <number of files>
<package name 2>         <number of files>
......

<package name 10>         <number of files>
```



</details>

-------
## Assumptions & Scope

  
This application was developed on Python 3.8 and therefore should be used on at least this Python version. While there are no third party applications involved, some of the imported modules may not function as expected with older versions of Python.

It is assumed that the user is interested in both the udeb and non-udeb packages associated with each architecture. Therefore, both packages are downloaded. Since udeb packages take up kilobytes of space and bandwidth, this should not be an issue.

The user is only interested in downloading from the mirror http://ftp.uk.debian.org/debian/dists/stable/main/. Even though it is possible to define a custom URL in the CLI tool, the respective logic was not implemented as it is out of scope.

The application logic is based off the assumption that the **package naming conventions change rarely**.

The user is okay with the packages being **downloaded to the same directory as the application** itself. While it would be nice to have the ability to specify the download location, it is out of scope.

The user is okay with always being provided with **exactly the top 10 packages** according to files associated. While it would be nice to have the ability to specify the exact number of packages displayed, it is out of scope.


## Development

Before starting to think about how to approach this task, I needed to research how to create a Python Command Line Tool. Thankfully, there is an [amazing tutorial](https://docs.python.org/3/howto/argparse.html#id1) for the module `argparse` that teaches exactly what I needed step by step.

Once I felt confident that I grasped the basic functionality of this module, I went on to think about the bigger problem at hand and how to break it down into smaller problems. 

My first idea was to think about what is the minimum input needed into the command line to achieve the desired output. The task description provides one input with two desired outputs: 
  
  
*INPUT*: The user must provide a specific architecture into the command line

*OUTPUTS*: Download the architecture's respective packages and print the top 10 packages by associated files. 

I realized that to achieve the latter, I would need to parse the entire website content and apply some logic to it. Since I am familiar with the module `urllib`, I knew that I could definitely apply it for this problem. With this, I looked at the response I would get from the website with the following code to get a better idea of what I am dealing with:
```
with urllib.request.urlopen(url_mirror) as response:
    html = response.read()
    payload = html.decode()
    print(payload)
```

With a response that looks something like this:
```
<html>
<head><title>Index of /debian/dists/stable/main/</title></head>
<body>
<h1>Index of /debian/dists/stable/main/</h1><hr><pre><a href="../">../</a>
<a href="binary-all/">binary-all/</a>       26-Mar-2022 10:20      -
<a href="binary-amd64/">binary-amd64/</a>   26-Mar-2022 10:20       -
...
<a href="installer-ppc64el/">installer-ppc64el/</a>     26-Mar-2022 09:28       -
<a href="Contents-s390x.gz">Contents-s390x.gz</a>       26-Mar-2022 09:47       8665164
<a href="Contents-source.gz">Contents-source.gz</a>     26-Mar-2022 09:49       72796087
<a href="Contents-udeb-all.gz">Contents-udeb-all.gz</a>     15-Jun-2021 01:58       13516
</pre><hr></body>
</html>

```

According to the task description, only the lines containing the word "Contents" are relevant seeing as these are the only ones with a number for files attached.



I then started to think about breaking down the overall problem into smaller problems. I iterated over a flowchart to visualize and get a better grasp on every step needed:

![My flowchart](/Flowchart.png)

Each function is depicted as a rectangle. Ideally, each function should be responsible for one specific task. However, since the functions are not yet overly complicated and I wanted to keep the program as lean as possible, I decided to keep some functionalities bundled within a single function. In other cases it would be helpful to create helper functions, especially when logic is being reused.

For example, the function `get_all_content_list()` retrieves the html response and parses that response at the same time. Its input comes from the CLI parser, whereas its output is directly used by the next function.

In this fashion I created every step of the way to the desired output while also creating unit tests for these functions. Additionally, I added try except blocks to catch errors that are not caused by logic errors in the program, e.g. when a faulty URL is entered or the mirror is down.

In the fashion of remaining lean, I decided to simply keep all functions within the same module as they are related to each other anyway.

Lastly, development was done with VS Code using pylint and black for auto-formatting.

## Tests

I wrote unit tests using `unittest` for every class in the main module, except the CLI parser. `setUp()` was used to create instance variables that would be reusable by every test method. Since I am lacking the knowledge in mocking, I decided to create my own 'mock' variables of expected output and assert that my function's output would be as expected.

The function that would download files does not return anything, so I decided to assert that files exist within the same directory instead.

For the function that only prints the top 10 packages I asserted that it would indeed not return anything.

In total there are 4 test methods, ideally resulting in the following output:
```
...   
1. Contents-all.gz          123420
2. Contents-arm64.gz        10
.
----------------------------------------------------------------------
Ran 4 tests in 1.227s

OK
```
...where each dot represents a test and the text inbetween being the print output from the previously mentioned function.

## Application Usage

Simply run the script from the CLI of your choice. For example, on Windows you could navigate to the directory of the script and run for example `py package_statistics.py amd64 -v` to get the following output:

```
Downloading Contents-arm64.gz. Hold tight...
Downloading Contents-udeb-arm64.gz. Hold tight...
Contents-arm64.gz, Contents-udeb-arm64.gz saved to C:\Users\phili\Downloads\Canonical_Assessment

   1. Contents-source.gz       72796087
   2. Contents-all.gz          30917003
   3. Contents-amd64.gz        10221420
   4. Contents-i386.gz         10158244
   5. Contents-arm64.gz        9785927
   6. Contents-ppc64el.gz      9306540
   7. Contents-armhf.gz        9260210
   8. Contents-mipsel.gz       9137180
   9. Contents-mips64el.gz     8999253
  10. Contents-s390x.gz        8665164
```

Furthermore, the application provides a help description with the command `package_statistics.py amd64 -h`:

```
usage: package_statistics.py [-h] [-u URL] [-v] arch
positional arguments:
  arch               The architecture of the compressed Contents file to download: 'amd64', 'arm64', 'armel', 'armhf', 'i386', 'mips64el', 'mipsel''ppc64el', 's390x', 'source', 'all'

optional arguments:
  -h, --help         show this help message and exit
  -u URL, --url URL  The mirror where the content files can be found. Default is set to http://ftp.uk.debian.org/debian/dists/stable/main/
  -v, --verbose      Increase output verbosity for downloads
```


