# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcTaskList(Cds2mdTranslatorTestCase):
    def test_translator_ac_task_list(self) -> None:
        file = DATA_FOLDER / 'ac_task_list.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            - [ ] one
            - [x] two
            - [ ] **three**
        ''')

        self.assertEqual(expected, body)
