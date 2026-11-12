# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorOl(Cds2mdTranslatorTestCase):
    def test_translator_ol(self) -> None:
        file = DATA_FOLDER / 'ol.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = '''\
1. one
1. two
1. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed risus augue,
   vulputate eu metus nec, ultricies sagittis nibh. Praesent eget ex sit amet
   magna efficitur bibendum id sed enim. Pellentesque id purus ac diam iaculis
   sollicitudin at in purus. Pellentesque ornare libero vitae odio ornare
   lacinia. Pellentesque odio nibh, vulputate sed nisi eget, egestas congue leo.
   Sed in ipsum commodo, hendrerit purus scelerisque, ullamcorper tellus. Mauris
   vel porta magna. Sed vel nulla aliquet, fringilla erat quis, tincidunt neque.
   Sed pellentesque erat est, id dictum magna consequat sit amet. Ut sed lectus
   sem. Sed sollicitudin dignissim viverra.
   1. three
   1. four
   1. Fusce sed sem fringilla, luctus tortor vitae, facilisis neque. Quisque
      consectetur tincidunt diam, ut faucibus tellus hendrerit non. Fusce quis
      consectetur turpis. Mauris varius arcu quis pulvinar vulputate. Quisque id
      sapien vehicula, tincidunt metus rutrum, tincidunt ligula. Nunc a nibh
      libero. Aenean neque mauris, eleifend sed commodo id, placerat sed neque.
      Mauris cursus felis enim, id rutrum justo lacinia id. Praesent pretium mi
      a tempor rutrum. Aliquam luctus, arcu vitae fringilla aliquet, purus metus
      laoreet urna, eu finibus enim metus et tortor. Morbi pharetra turpis sed
      quam dapibus tempor. Proin in lorem elementum, vulputate odio non, euismod
      arcu.'''

        self.assertIn(expected, body)
