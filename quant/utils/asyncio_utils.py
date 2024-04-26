# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import warnings
from asyncio import AbstractEventLoop, get_event_loop_policy, new_event_loop, set_event_loop
from contextlib import suppress


def get_loop() -> AbstractEventLoop:
    with suppress(RuntimeError):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            loop = get_event_loop_policy().get_event_loop()

        if not loop.is_closed():
            return loop

    loop = new_event_loop()
    set_event_loop(loop)
    return loop


def create_loop() -> AbstractEventLoop:
    loop = new_event_loop()
    set_event_loop(loop)

    return loop


def kill_loop() -> None:
    loop = get_loop()

    if loop.is_closed():
        return

    loop.close()
    set_event_loop(None)
    loop.stop()
