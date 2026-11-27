# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcLinkUser(Cds2mdTranslatorTestCase):
    def test_translator_ac_link_user(self) -> None:
        file = DATA_FOLDER / 'ac_link_user.storage'
        data = file.read_text()

        userid2name = {
            'e129db851d7fe2ddc505552f1b69e435': 'my-name',
        }

        body = self.translate(data, userid2name=userid2name)

        expected = cleandoc('''
            @my-name
        ''')

        self.assertIn(expected, body)
