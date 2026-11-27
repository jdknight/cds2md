# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from cds2md.translator import Translator


class Environment:
    def __init__(self) -> None:
        """
        an environment for a cds2md run
        """
        self.translator_cls = Translator

    def set_translator(self, translator: type[Translator]) -> None:
        """
        configure the translator to use for a processing event

        Allows the environment to be configured with an alternative translator
        class. Useful for scenarios where user wants to override certain
        translations themselves.

        Args:
            translator: the translator type
        """

        self.translator_cls = translator
