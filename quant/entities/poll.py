from enum import Enum
from typing import List, Dict
from datetime import datetime

import attrs

from quant.entities.emoji import Emoji, PartialEmoji
from quant.utils.parser import string_to_emoji


class PollMediaType(int, Enum):
    DEFAULT = 1


@attrs.define(kw_only=True, hash=True)
class PollMedia:
    text: str | None = attrs.field(default=None)
    emoji: str | Emoji | PartialEmoji | None = attrs.field(default=None)


@attrs.define(kw_only=True, hash=True)
class PollAnswer:
    answer_id: int = attrs.field()
    poll_media: PollMedia = attrs.field()


@attrs.define(kw_only=True, hash=True)
class Poll:
    question: str = attrs.field()
    answers: List[PollAnswer] = attrs.field()
    expiry: float = attrs.field()
    allow_multiselect: bool = attrs.field()
    layout_type: PollMediaType = attrs.field()


@attrs.define(kw_only=True, hash=True)
class _PollAnswerCount:
    id: int = attrs.field()
    count: int = attrs.field()
    me_voted: bool = attrs.field()


@attrs.define(kw_only=True, hash=True)
class PollResults:
    is_finalized: bool = attrs.field()
    answer_counts: _PollAnswerCount = attrs.field()


@attrs.define(kw_only=True, hash=True)
class Answer:
    text: str = attrs.field(default=None)
    emoji: str | Emoji | PartialEmoji = attrs.field(default=None)


def poll(
    question: str,
    answers: List[Answer],
    allow_multiselect: bool = False,
    expiry: datetime | None = None
) -> Poll:  # I don't know why custom emojis don't work
    if expiry is not None:
        expiry = expiry.timestamp()

    done_answers = []

    for answer_id, answer in enumerate(answers, start=1):
        if isinstance(answer.emoji, str):
            answer.emoji = string_to_emoji(emoji=answer.emoji)

        done_answers.append(PollAnswer(
            answer_id=answer_id,
            poll_media=PollMedia(
                text=answer.text,
                emoji=answer.emoji
            )
        ))

    return Poll(
        question=question,
        answers=done_answers,
        expiry=expiry,
        allow_multiselect=allow_multiselect,
        layout_type=PollMediaType.DEFAULT
    )
