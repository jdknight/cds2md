# CDS2MD

[![pip Version](https://badgen.net/pypi/v/cds2md?label=PyPI)](https://pypi.python.org/pypi/cds2md)
[![Build Status](https://github.com/jdknight/cds2md/actions/workflows/build.yml/badge.svg)](https://github.com/jdknight/cds2md/actions/workflows/build.yml)

## Overview

This utility can be used to convert Confluence® Data Center pages to Markdown.
Atlassian's Confluence Data Center is [scheduled for end-of-life in 2029][eol].
This tool can be used in an attempt migrate data from Confluence Data Center
instances to another location.

## Requirements

* [Python][python] 3.11+

## Installation

This tool can be installed using [pip][pip] or [pipx][pipx]:

```shell
pipx install cds2md
 (or)
pip install -U cds2md
 (or)
python -m pip install -U cds2md
```

# Usage

This tool can be invoked from a command line using:

```none
cds2md --help
 (or)
python -m cds2md --help
```

A minimal example run is as follows:

```
export CDS2MD_CONFLUENCE_TOKEN=TOKEN
export CDS2MD_CONFLUENCE_SPACE_KEY=MYSPACE
export CDS2MD_CONFLUENCE_URL=https://wiki.example.com/
cds2md
```

This will fetch page information from a Confluence space and store this data
into a local cache folder (`.cds2md-cache/`). Once all pages are fetched,
content will be converted to Markdown and placed in the output directory
(`output/`).

# Options

The following is a list of available options:

```
positional arguments:
  {all,connection-check,fetch,process}
                        action to perform (default: all)

options:
  -h, --help            show this help message and exit
  --ca-certificate CA_CERTIFICATE
                        ca certificate to use when communicating with Confluence
  --cache CACHE         path to store fetch cached data
  --confluence-space-key CONFLUENCE_SPACE_KEY
                        space to query for pages
  --confluence-token CONFLUENCE_TOKEN
                        token used to query the Confluence instance
  --confluence-token-file CONFLUENCE_TOKEN_FILE
                        file which holds a Confluence token to use
  --confluence-token-stdin
                        pass in the token via the standard input stream
  --confluence-url CONFLUENCE_URL
                        url of the Confluence data center instance to interact
                        with
  --debug               enabling debugging logs
  --development         configure to operate in a development state
  --header, -H HEADER   http headers to include in requests
  --ignore-tls          ignore all TLS checks when communicating with Confluence
  --flat                ignore any Confluence-detected hierarchy structure
  --output OUTPUT       path to output markdown content into
  --timeout TIMEOUT     timeout for connection REST requests to Confluence
  --tweak-admonition-type {default,docusaurus,github,gitlab,myst,plain}
                        admonition formatting to use (default: default)
  --tweak-html-images   force all images to be generated as html-based images
  --tweak-html-tables   force all tables to be generated as html-based tables
  --version             show program's version number and exit
  --wrap WRAP           hint to the number of characters to wrap to
```

----

The CDS2MD project is unaffiliated with Atlassian.\
Atlassian is a registered trademark of Atlassian Pty Ltd.\
Confluence is a registered trademark of Atlassian Pty Ltd.


[eol]: https://www.atlassian.com/licensing/data-center-end-of-life
[python]: https://www.python.org/
