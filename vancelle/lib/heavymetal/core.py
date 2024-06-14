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
import typing

import markupsafe
import sentry_sdk
import structlog

from .types import Heavymetal, HeavymetalAttrs, HeavymetalProtocol, HeavymetalTuple

# https://html.spec.whatwg.org/#void-elements
VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

logger = structlog.get_logger(logger_name=__name__)


def _attributes(attrs: HeavymetalAttrs) -> str:
    if not attrs:
        return ""

    return " " + " ".join(
        f"{html.escape(k)}" if v is True else f'{html.escape(k)}="{html.escape(v)}"'
        for k, v in attrs.items()
        if v is not False and v is not None
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Trace:
    original_node: Heavymetal | None
    node: HeavymetalTuple | str

    def __str__(self) -> str:
        if isinstance(self.node, str):
            string = f"{self.node!r}"
        else:
            tag, attrs, _ = self.node

            if tag is None:
                string = "<!-- fragment -->"
            else:
                string = f"<{tag}{_attributes(attrs)} />"

        if self.original_node is not None:
            string += f" from {self.original_node!r}"

        return string


@dataclasses.dataclass(frozen=True)
class HeavymetalException(Exception):
    message: str
    parents: typing.Sequence[Trace] = ()
    node: HeavymetalTuple | None = None
    value: typing.Any = None

    @sentry_sdk.trace
    def __str__(self) -> str:
        message = self.message

        if self.parents:
            parents = [str(trace) for trace in self.parents]
            message += "\n\n" + "\n".join(f"{'  ' * indent}{parent}" for indent, parent in enumerate(parents))

        if self.value is not None:
            message += "\n\n" + repr(self.value)

        return message


class HeavymetalSyntaxError(HeavymetalException):
    pass


class HeavymetalHtmlError(HeavymetalException):
    pass


def expand(original_node: Heavymetal, *, traces: typing.Sequence[Trace] = ()) -> HeavymetalTuple | str:
    if isinstance(original_node, HeavymetalProtocol):
        node = original_node.heavymetal()
        trace = Trace(original_node=original_node, node=node)
    elif callable(original_node):
        node = original_node()
        trace = Trace(original_node=original_node, node=node)
    elif original_node is None:
        node = (None, {}, ())
        trace = Trace(original_node=None, node=node)
    elif isinstance(original_node, str):
        return original_node
    else:
        node = original_node
        trace = Trace(original_node=None, node=node)

    # This is where hotmetal tripped me up a lot.
    if not isinstance(node, tuple) or not len(node) == 3:
        raise HeavymetalSyntaxError(f"Expected a tuple with three elements, got {node!r}", traces, value=node)

    node: HeavymetalTuple
    tag, attrs, children = node
    children = tuple(expand(c, traces=(*traces, trace)) for c in children)
    return (tag, attrs, children)


def render_simple(node: HeavymetalTuple | str, *, traces: typing.Sequence[Trace] = ()) -> str:
    if isinstance(node, markupsafe.Markup):
        return node

    if isinstance(node, str):
        return html.escape(node)

    # This is where hotmetal tripped me up a lot.
    if not isinstance(node, tuple) or not len(node) == 3:
        raise HeavymetalSyntaxError(f"Expected a tuple with three elements, got {node!r}", traces, value=node)

    node: HeavymetalTuple
    tag, attrs, children = node
    traces = (*traces, Trace(original_node=None, node=node))

    # This might not always be a tuple, but it should be an ordered sequence.
    # That might be too restrictive — should this allow a generator/iterable?
    if isinstance(children, typing.Iterable) and not isinstance(children, typing.Sequence):
        children = tuple(children)

    if not isinstance(children, typing.Iterable):
        raise HeavymetalSyntaxError("Expected a list or sequence for the children= parameter", traces, node, children)

    # We can safely do this check as no child element should ever be a dict.
    if (
        isinstance(children, tuple)
        and len(children) == 3
        and isinstance(children[0], (str, type(None)))
        and isinstance(children[1], dict)
        and isinstance(children[2], list)
    ):
        raise HeavymetalSyntaxError("Another heavymetal tuple was passed to the children= parameter", traces, node, children)

    if tag == "":
        raise HeavymetalSyntaxError("Tag is an empty string", traces, node)

    # Fragments are not included in their output, but their children are.
    if tag is None:
        if attrs:
            raise HeavymetalSyntaxError("Fragments cannot have attributes", traces, node)
        nested = "".join(render_simple(child, traces=traces) for child in children)
        return "{}".format(nested)

    try:
        attributes = _attributes(attrs)
    except ValueError as error:
        raise HeavymetalException("Invalid attribute", traces, node) from error

    # Void elements like <br /> (https://html.spec.whatwg.org/#void-elements)
    #
    # Don't treat childless elements as self-closing - that's not valid in HTML5.
    # https://html.spec.whatwg.org/multipage/syntax.html#start-tags
    # https://github.com/validator/validator/wiki/Markup-%C2%BB-Void-elements
    if tag.lower() in VOID_ELEMENTS:
        if children:
            raise HeavymetalHtmlError("Void element cannot have children", traces, node)
        return "<{tag}{attributes} />".format(tag=html.escape(tag), attributes=attributes)

    nested = "".join(render_simple(child, traces=traces) for child in children)
    return "<{tag}{attributes}>{nested}</{tag}>".format(tag=html.escape(tag), attributes=attributes, nested=nested)


@sentry_sdk.trace()
def render(node: Heavymetal) -> str:
    return render_simple(expand(node))
