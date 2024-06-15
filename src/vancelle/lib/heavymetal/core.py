"""
The _render function is directly adapted from a similar function in hotmetal [1],
which has the following copyright notice and license.

[1]: https://github.com/j4mie/hotmetal
[2]: https://github.com/j4mie/hotmetal/blob/main/LICENSE

> Copyright (c) 2022, Jamie Matthews
> All rights reserved.
>
> Redistribution and use in source and binary forms, with or without
> modification, are permitted provided that the following conditions are met:
>
> * Redistributions of source code must retain the above copyright notice, this
>   list of conditions and the following disclaimer.
>
> * Redistributions in binary form must reproduce the above copyright notice,
>   this list of conditions and the following disclaimer in the documentation
>   and/or other materials provided with the distribution.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
> AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
> IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
> DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
> FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
> DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
> SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
> CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
> OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
> OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import dataclasses
import html
import logging
import typing

import markupsafe
import sentry_sdk

from .types import (
    HeavymetalAnything,
    HeavymetalAttrs,
    HeavymetalProtocol,
    Heavymetal,
    _HeavymetalStatic,
)

logger = logging.getLogger(__name__)

# https://html.spec.whatwg.org/#void-elements
VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "source",
    "track",
    "wbr",
}


def _attributes(attrs: HeavymetalAttrs) -> str:
    if not attrs:
        return ""

    return " " + " ".join(
        f"{html.escape(k)}" if v is True else f'{html.escape(k)}="{html.escape(v)}"'
        for k, v in attrs.items()
        if v is not False and v is not None
    )


@dataclasses.dataclass(frozen=True)
class Trace:
    current: Heavymetal = dataclasses.field()
    original: typing.Optional[HeavymetalAnything] = dataclasses.field(default=None)

    def __str__(self) -> str:
        if isinstance(self.current, str):
            string = f"{self.current!r}"
        else:
            tag, attrs, _ = self.current

            if tag is None:
                string = "<!-- fragment -->"
            else:
                string = f"<{tag}{_attributes(attrs)} />"

        if self.original is not None:
            string += f" from {self.original!r}"

        return string


@dataclasses.dataclass(frozen=True)
class HeavymetalException(Exception):
    message: str
    traces: typing.Sequence[Trace]
    value: typing.Optional[Trace | typing.Any] = None

    @sentry_sdk.trace
    def __str__(self) -> str:
        message = self.message

        if self.traces:
            parents = [str(trace) for trace in self.traces]
            message += "\n\n" + "\n".join(f"{'  ' * indent}{parent}" for indent, parent in enumerate(parents))

        if self.value is not None:
            message += "\n\n" + str(self.value)

        return message


class HeavymetalSyntaxError(HeavymetalException):
    pass


class HeavymetalHtmlError(HeavymetalException):
    pass


def unpack_dynamic(original: HeavymetalAnything, /, *, traces: typing.Sequence[Trace] = ()) -> _HeavymetalStatic:
    """
    Unpack a 'dynamic' tree containing callable items into a 'static' tree containing tuples and strings.

    Types enforce a minor limitation on callables: the 'top' element they return must be static.
    """
    node: Heavymetal
    if isinstance(original, HeavymetalProtocol):
        node = original.heavymetal()
        trace = Trace(node, original)
    elif callable(original):
        node = original()
        trace = Trace(node, original)
    else:
        node = original
        trace = Trace(node)

    # Make sure to do this check _after_ resolving any callables, since they can return strings.
    if isinstance(node, str):
        return node

    # This is where hotmetal tripped me up a lot.
    if not isinstance(node, tuple) or not len(node) == 3:
        raise HeavymetalSyntaxError(f"Expected a tuple with three elements, got {node!r}", traces=traces, value=trace)

    tag, attrs, original_children = node
    children = tuple(unpack_dynamic(c, traces=(*traces, trace)) for c in original_children)
    return (tag, attrs, children)


def render_static(node: _HeavymetalStatic, *, traces: typing.Sequence[Trace] = ()) -> str:
    """Render a 'static' tree containing tuples and strings to an HTML string."""

    if isinstance(node, markupsafe.Markup):
        return node

    if isinstance(node, str):
        return html.escape(node)

    # This is where hotmetal tripped me up a lot.
    if not isinstance(node, tuple) or not len(node) == 3:
        raise HeavymetalSyntaxError("Expected a tuple with three elements", traces=traces, value=node)

    tag, attrs, children = node
    trace = Trace(node)
    traces = (*traces, trace)

    # This might not always be a tuple, but it should be an ordered sequence.
    # That might be too restrictive — should this allow a generator/iterable?
    if isinstance(children, typing.Iterable) and not isinstance(children, typing.Sequence):
        children = tuple(children)

    if not isinstance(children, typing.Iterable):
        raise HeavymetalSyntaxError("Expected a list or sequence for the children= parameter", traces, node)

    # We can safely do this check as no child element should ever be a dict.
    if (
        isinstance(children, tuple)
        and len(children) == 3
        and isinstance(children[0], (str, type(None)))
        and isinstance(children[1], typing.Mapping)
        and isinstance(children[2], typing.Sequence)
    ):
        raise HeavymetalSyntaxError("A Heavymetal tuple was passed to the children= parameter", traces, node)

    if tag == "":
        raise HeavymetalSyntaxError("Tag is an empty string", traces, trace)

    # Fragments are not included in their output, but their children are.
    if tag is None:
        if attrs:
            raise HeavymetalSyntaxError("Fragments cannot have attributes", traces, trace)
        nested = "".join(render_static(child, traces=traces) for child in children)
        return "{}".format(nested)

    try:
        attributes = _attributes(attrs)
    except ValueError as error:
        raise HeavymetalException("Invalid attribute", traces, trace) from error

    # Void elements like <br /> (https://html.spec.whatwg.org/#void-elements)
    #
    # Don't treat childless elements as self-closing - that's not valid in HTML5.
    # https://html.spec.whatwg.org/multipage/syntax.html#start-tags
    # https://github.com/validator/validator/wiki/Markup-%C2%BB-Void-elements
    if tag.lower() in VOID_ELEMENTS:
        if children:
            raise HeavymetalHtmlError("Void element cannot have children", traces, trace)
        return "<{tag}{attributes} />".format(tag=html.escape(tag), attributes=attributes)

    nested = "".join(render_static(child, traces=traces) for child in children)
    return "<{tag}{attributes}>{nested}</{tag}>".format(tag=html.escape(tag), attributes=attributes, nested=nested)


@sentry_sdk.trace()
def render(node: HeavymetalAnything, /) -> str:
    with sentry_sdk.start_span(op="task", description=unpack_dynamic.__qualname__):
        expanded = unpack_dynamic(node)

    with sentry_sdk.start_span(op="task", description=render_static.__qualname__):
        rendered = render_static(expanded)

    return rendered
