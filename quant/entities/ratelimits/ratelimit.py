"""
MIT License

Copyright (c) 2023 MagM1go

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from datetime import datetime

import attrs


@attrs.define(kw_only=True)
class RateLimitBucketReset:
    reset_time: datetime = attrs.field()
    reset_time_milliseconds: float = attrs.field()


@attrs.define(kw_only=True)
class RateLimit:
    max_retries: int = attrs.field()
    remaining_retries: int = attrs.field()
    retry_after: float = attrs.field()
    message: str = attrs.field()
    is_global: bool = attrs.field()
    bucket: str = attrs.field()
    code: int | None = attrs.field()
    scope: str | None = attrs.field()


@attrs.define(kw_only=True)
class Bucket:
    rate_limit: RateLimit | None = attrs.field()
    bucket_reset: RateLimitBucketReset = attrs.field()
