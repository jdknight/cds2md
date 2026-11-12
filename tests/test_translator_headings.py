# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorHeadings(Cds2mdTranslatorTestCase):
    def test_translator_headings(self) -> None:
        file = DATA_FOLDER / 'headings.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            # heading 1

            ## heading 2

            ### heading 3

            #### heading 4

            ##### heading 5

            ###### heading 6
        ''')

        self.assertIn(expected, body)
