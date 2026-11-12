# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import Namespace
from cds2md.defs import AdmonitionType
from cds2md.opts import DEFAULT_CONNECTION_TIMEOUT
from cds2md.opts import DEFAULT_WRAP
from cds2md.opts import process_options
from io import StringIO
from pathlib import Path
from tests import Cds2mdTestCase
from unittest.mock import patch
import os
import sys


class TestOptions(Cds2mdTestCase):
    def setUp(self) -> None:
        # default arguments for tests; provides the minimal/required set
        # for unit tests to pass, which can be adjusted for specific checks
        self.args = {
            '--confluence-space-key': 'DEFAULT_TEST_SPACE',
            '--confluence-token': 'dummy-token',
            '--confluence-url': 'http://wiki.example.com/rest/api',
        }

    def test_opts_ca_certificate_exists_cli(self) -> None:
        with self.temp_dir() as wd, self.working_dir(wd):
            # create a dummy "certificate"
            crt_file = Path('dummy.crt')
            with crt_file.open('wb'):
                pass

            self.args['--ca-certificate'] = crt_file

            opts = self._process_options()
            self.assertEqual(opts.ca_certificate, crt_file)

    def test_opts_ca_certificate_exists_env(self) -> None:
        with self.temp_dir() as wd, self.working_dir(wd):
            # create a dummy "certificate"
            crt_file = Path('dummy.crt')
            with crt_file.open('wb'):
                pass

            os.environ['CDS2MD_CA_CERTIFICATE'] = str(crt_file)

            opts = self._process_options()
            self.assertEqual(opts.ca_certificate, crt_file)

    def test_opts_ca_certificate_invalid_cli(self) -> None:
        with self.temp_dir() as tmpdir:
            self.args['--ca-certificate'] = tmpdir

            with self.assertRaises(SystemExit):
                self._process_options()

    def test_opts_ca_certificate_invalid_env(self) -> None:
        with self.temp_dir() as tmpdir:
            os.environ['CDS2MD_CA_CERTIFICATE'] = str(tmpdir)

            with self.assertRaises(SystemExit):
                self._process_options()

    def test_opts_ca_certificate_missing_cli(self) -> None:
        self.args['--ca-certificate'] = 'invalid-ca-certificate-file.crt'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_ca_certificate_missing_env(self) -> None:
        os.environ['CDS2MD_CA_CERTIFICATE'] = 'invalid-ca-certificate-file.crt'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_cache_invalid(self) -> None:
        with self.temp_dir() as wd, self.working_dir(wd):
            misc_file = Path('misc-file')
            with misc_file.open('wb'):
                pass

            self.args['--cache'] = misc_file

            with self.assertRaises(SystemExit):
                self._process_options()

    def test_opts_cache_valid(self) -> None:
        with self.temp_dir() as tmpdir:
            self.args['--cache'] = tmpdir

            opts = self._process_options()
            self.assertEqual(opts.cache.resolve(), Path(tmpdir).resolve())

    def test_opts_confluence_space_key_empty_cli(self) -> None:
        self.args['--confluence-space-key'] = ''

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_space_key_empty_env(self) -> None:
        del self.args['--confluence-space-key']
        os.environ['CDS2MD_CONFLUENCE_SPACE_KEY'] = ''

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_space_key_missing(self) -> None:
        del self.args['--confluence-space-key']

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_space_key_valid_cli(self) -> None:
        self.args['--confluence-space-key'] = 'TEST1'

        opts = self._process_options()
        self.assertEqual(opts.confluence_space_key, 'TEST1')

    def test_opts_confluence_space_key_valid_env(self) -> None:
        del self.args['--confluence-space-key']
        os.environ['CDS2MD_CONFLUENCE_SPACE_KEY'] = 'TEST2'

        opts = self._process_options()
        self.assertEqual(opts.confluence_space_key, 'TEST2')

    def test_opts_confluence_token_direct_empty_cli(self) -> None:
        self.args['--confluence-token'] = ''

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_token_direct_empty_env(self) -> None:
        del self.args['--confluence-token']
        os.environ['CDS2MD_CONFLUENCE_TOKEN'] = ''

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_token_direct_missing(self) -> None:
        del self.args['--confluence-token']

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_token_direct_valid_cli(self) -> None:
        self.args['--confluence-token'] = 'TOKEN-CLI'

        opts = self._process_options()
        self.assertEqual(opts.confluence_token, 'TOKEN-CLI')

    def test_opts_confluence_token_direct_valid_env(self) -> None:
        del self.args['--confluence-token']
        os.environ['CDS2MD_CONFLUENCE_TOKEN'] = 'TOKEN-ENV'

        opts = self._process_options()
        self.assertEqual(opts.confluence_token, 'TOKEN-ENV')

    def test_opts_confluence_token_file_empty(self) -> None:
        with self.temp_dir() as wd, self.working_dir(wd):
            token_file = Path('token')
            with token_file.open('wb'):
                pass

            del self.args['--confluence-token']
            self.args['--confluence-token-file'] = token_file

            with self.assertRaises(SystemExit):
                self._process_options()

    def test_opts_confluence_token_file_invalid_arg(self) -> None:
        del self.args['--confluence-token']
        self.args['--confluence-token-file'] = ''

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_token_file_invalid_file(self) -> None:
        with self.temp_dir() as tmpdir:
            del self.args['--confluence-token']
            self.args['--confluence-token-file'] = tmpdir

            with self.assertRaises(SystemExit):
                self._process_options()

    def test_opts_confluence_token_file_missing(self) -> None:
        del self.args['--confluence-token']
        self.args['--confluence-token-file'] = 'token-file-does-not-exist'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_token_file_valid(self) -> None:
        with self.temp_dir() as wd, self.working_dir(wd):
            token_file = Path('token')
            token_file.write_text('my-file-test-token\n')

            del self.args['--confluence-token']
            self.args['--confluence-token-file'] = token_file

            opts = self._process_options()
            self.assertEqual(opts.confluence_token, 'my-file-test-token')

    def test_opts_confluence_token_stdin_empty(self) -> None:
        del self.args['--confluence-token']
        self.args['--confluence-token-stdin'] = None

        mock_input = StringIO('\n')
        with patch('sys.stdin', mock_input), self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_token_stdin_valid(self) -> None:
        del self.args['--confluence-token']
        self.args['--confluence-token-stdin'] = None

        mock_input = StringIO('my-stdin-test-token\n')
        with patch('sys.stdin', mock_input):
            opts = self._process_options()
            self.assertEqual(opts.confluence_token, 'my-stdin-test-token')

    def test_opts_confluence_url_empty_cli(self) -> None:
        self.args['--confluence-url'] = ''

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_url_empty_env(self) -> None:
        del self.args['--confluence-url']
        os.environ['CDS2MD_CONFLUENCE_URL'] = ''

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_url_invalid_hostname_cli(self) -> None:
        self.args['--confluence-url'] = 'http://'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_url_invalid_hostname_env(self) -> None:
        del self.args['--confluence-url']
        os.environ['CDS2MD_CONFLUENCE_URL'] = 'http://'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_url_invalid_scheme_cli(self) -> None:
        self.args['--confluence-url'] = 'example.com'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_url_invalid_scheme_env(self) -> None:
        del self.args['--confluence-url']
        os.environ['CDS2MD_CONFLUENCE_URL'] = 'example.com'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_url_invalid_value_cli(self) -> None:
        self.args['--confluence-url'] = 'http://[2001:db8::1/'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_url_invalid_value_env(self) -> None:
        del self.args['--confluence-url']
        os.environ['CDS2MD_CONFLUENCE_URL'] = 'http://[2001:db8::1/'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_url_missing(self) -> None:
        del self.args['--confluence-url']

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_confluence_url_valid_http_cli(self) -> None:
        self.args['--confluence-url'] = 'http://example.org/cli-http'

        opts = self._process_options()
        self.assertEqual(opts.confluence_url, 'http://example.org/cli-http')

    def test_opts_confluence_url_valid_http_env(self) -> None:
        del self.args['--confluence-url']
        os.environ['CDS2MD_CONFLUENCE_URL'] = 'http://example.org/env-http'

        opts = self._process_options()
        self.assertEqual(opts.confluence_url, 'http://example.org/env-http')

    def test_opts_confluence_url_valid_https_cli(self) -> None:
        self.args['--confluence-url'] = 'http://example.org/cli-https'

        opts = self._process_options()
        self.assertEqual(opts.confluence_url, 'http://example.org/cli-https')

    def test_opts_confluence_url_valid_https_env(self) -> None:
        del self.args['--confluence-url']
        os.environ['CDS2MD_CONFLUENCE_URL'] = 'http://example.org/env-https'

        opts = self._process_options()
        self.assertEqual(opts.confluence_url, 'http://example.org/env-https')

    def test_opts_debug_valid(self) -> None:
        self.args['--debug'] = None
        opts = self._process_options()
        self.assertTrue(opts.debug)

    def test_opts_development_valid(self) -> None:
        self.args['--development'] = None
        opts = self._process_options()
        self.assertTrue(opts.development)

    def test_opts_flat_valid(self) -> None:
        self.args['--flat'] = None
        opts = self._process_options()
        self.assertTrue(opts.flat)

    def test_opts_header_valid_invalid_no_key(self) -> None:
        self.args['--header'] = ': value'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_header_valid_invalid_value(self) -> None:
        self.args['--header'] = 'invalid'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_header_valid_multiple(self) -> None:
        self.args['--header'] = ['KEY1:VAL2', ' KEY4: VAL3 ']
        opts = self._process_options()
        self.assertIn('KEY1', opts.headers)
        self.assertIn('KEY4', opts.headers)
        self.assertEqual(opts.headers['KEY1'], 'VAL2')
        self.assertEqual(opts.headers['KEY4'], 'VAL3')

    def test_opts_header_valid_single(self) -> None:
        self.args['--header'] = ['KEY: VAL']
        opts = self._process_options()
        self.assertIn('KEY', opts.headers)
        self.assertEqual(opts.headers['KEY'], 'VAL')

    def test_opts_help_accepted(self) -> None:
        self.args['--help'] = None

        with self.assertRaises(SystemExit) as cm:
            self._process_options()

        self.assertEqual(cm.exception.code, 0)

    def test_opts_ignore_tls_valid(self) -> None:
        self.args['--ignore-tls'] = None
        opts = self._process_options()
        self.assertTrue(opts.ignore_tls)

    def test_opts_invalid(self) -> None:
        self.args.clear()

        with patch.object(sys, 'argv', ['cds2md']):
            with self.assertRaises(SystemExit) as cm:
                self._process_options()

        self.assertEqual(cm.exception.code, 1)

    def test_opts_output_invalid(self) -> None:
        with self.temp_dir() as wd, self.working_dir(wd):
            misc_file = Path('misc-file')
            with misc_file.open('wb'):
                pass

            self.args['--output'] = misc_file

            with self.assertRaises(SystemExit):
                self._process_options()

    def test_opts_output_valid(self) -> None:
        with self.temp_dir() as tmpdir:
            self.args['--output'] = tmpdir

            opts = self._process_options()
            self.assertEqual(opts.output.resolve(), Path(tmpdir).resolve())

    def test_opts_timeout_invalid_int_cli(self) -> None:
        self.args['--timeout'] = 'invalid'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_tweak_admonition_type_default(self) -> None:
        self.args['--tweak-admonition-type'] = 'default'
        opts = self._process_options()
        self.assertEqual(opts.tweak_admonition_type, AdmonitionType.DEFAULT)

    def test_opts_tweak_admonition_type_docusaurus(self) -> None:
        self.args['--tweak-admonition-type'] = 'docusaurus'
        opts = self._process_options()
        self.assertEqual(opts.tweak_admonition_type, AdmonitionType.DOCUSAURUS)

    def test_opts_tweak_admonition_type_github(self) -> None:
        self.args['--tweak-admonition-type'] = 'github'
        opts = self._process_options()
        self.assertEqual(
            opts.tweak_admonition_type, AdmonitionType.GITHUB)

    def test_opts_tweak_admonition_type_gitlab(self) -> None:
        self.args['--tweak-admonition-type'] = 'gitlab'
        opts = self._process_options()
        self.assertEqual(
            opts.tweak_admonition_type, AdmonitionType.GITLAB)

    def test_opts_tweak_admonition_type_myst(self) -> None:
        self.args['--tweak-admonition-type'] = 'myst'
        opts = self._process_options()
        self.assertEqual(opts.tweak_admonition_type, AdmonitionType.MYST)

    def test_opts_tweak_admonition_type_plain(self) -> None:
        self.args['--tweak-admonition-type'] = 'plain'
        opts = self._process_options()
        self.assertEqual(opts.tweak_admonition_type, AdmonitionType.PLAIN)

    def test_opts_tweak_html_images_valid(self) -> None:
        self.args['--tweak-html-images'] = None
        opts = self._process_options()
        self.assertTrue(opts.tweak_html_images)

    def test_opts_tweak_html_tables_valid(self) -> None:
        self.args['--tweak-html-tables'] = None
        opts = self._process_options()
        self.assertTrue(opts.tweak_html_tables)

    def test_opts_timeout_invalid_int_env(self) -> None:
        os.environ['CDS2MD_TIMEOUT'] = 'invalid'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_timeout_invalid_range_cli(self) -> None:
        self.args['--timeout'] = '-3'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_timeout_invalid_range_env(self) -> None:
        os.environ['CDS2MD_TIMEOUT'] = '-4'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_timeout_valid_default(self) -> None:
        opts = self._process_options()
        self.assertEqual(opts.timeout, DEFAULT_CONNECTION_TIMEOUT)

    def test_opts_timeout_valid_set_cli(self) -> None:
        self.args['--timeout'] = 123
        opts = self._process_options()
        self.assertEqual(opts.timeout, 123)

    def test_opts_timeout_valid_set_env(self) -> None:
        os.environ['CDS2MD_TIMEOUT'] = '456'
        opts = self._process_options()
        self.assertEqual(opts.timeout, 456)

    def test_opts_wrap_invalid_int(self) -> None:
        self.args['--wrap'] = 'invalid'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_wrap_invalid_range(self) -> None:
        self.args['--wrap'] = '-3'

        with self.assertRaises(SystemExit):
            self._process_options()

    def test_opts_wrap_valid_default(self) -> None:
        opts = self._process_options()
        self.assertEqual(opts.wrap, DEFAULT_WRAP)

    def test_opts_wrap_valid_set_disable(self) -> None:
        self.args['--wrap'] = 0
        opts = self._process_options()
        self.assertEqual(opts.wrap, 0)

    def test_opts_wrap_valid_set_value(self) -> None:
        self.args['--wrap'] = 789
        opts = self._process_options()
        self.assertEqual(opts.wrap, 789)

    def test_opts_unknown_value(self) -> None:
        self.args['--unknown-argument'] = None

        with self.assertRaises(SystemExit) as cm:
            self._process_options()

        self.assertEqual(cm.exception.code, 2)

    def test_opts_valid(self) -> None:
        opts = self._process_options()
        self.assertEqual(opts.confluence_space_key, 'DEFAULT_TEST_SPACE')

    def test_opts_version_accepted(self) -> None:
        self.args['--version'] = None

        with self.assertRaises(SystemExit) as cm:
            self._process_options()

        self.assertEqual(cm.exception.code, 0)

    def _process_options(self) -> Namespace:
        args = []
        for key, value in self.args.items():
            if value is None:
                args.append(key)
            elif isinstance(value, list):
                for entry in value:
                    args.extend([key, str(entry)])
            else:
                args.extend([key, str(value)])

        return process_options(args)
