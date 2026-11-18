"""Generic mock helper to mock any method and return any data type in tests."""

import json
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

from tests.helper.resource_utils import read_as_bytes, read_as_json

_UNSET = object()
TARGET_EXTRACTOR_GENERATE_CONTENT = (
    "src.services.extractor._client.models.generate_content"
)
_GENERATE_CONTENT_TARGET = TARGET_EXTRACTOR_GENERATE_CONTENT


def _build_mock_response(
    *,
    text: str | None = None,
    content: bytes | None = None,
    data: Any = None,
    json_path: str | None = None,
    attrs: dict[str, Any] | None = None,
    **extra_attrs: Any,
) -> MagicMock:
    """Build a mock response object with standard attributes like .text and .content."""
    response = MagicMock()

    if json_path is not None:
        response.text = json.dumps(read_as_json(json_path))
    elif data is not None:
        response.text = json.dumps(data) if not isinstance(data, str) else data
    else:
        response.text = text

    if content is not None:
        response.content = content

    combined_attrs = {}
    if attrs:
        combined_attrs.update(attrs)
    combined_attrs.update(extra_attrs)

    for key, value in combined_attrs.items():
        setattr(response, key, value)

    return response


@contextmanager
def mock_method(
    target: str | Any,
    method_name: str | None = None,
    *,
    return_value: Any = _UNSET,
    data: Any = None,
    json_path: str | None = None,
    file_path: str | None = None,
    text: str | None = None,
    as_response: bool = False,
    side_effect: Any = None,
    exception: Exception | type[Exception] | None = None,
    attrs: dict[str, Any] | None = None,
    **extra_attrs: Any,
):
    """Generic mock helper to mock any method and return any data type.

    Usage examples:
        # Mock any function with arbitrary return value:
        with mock_method("package.module.func", return_value=42): ...

        # Mock method with fixture data loaded from JSON:
        with mock_method("service.get_data", json_path="json/fixture.json"): ...

        # Mock method with fixture bytes loaded from file:
        with mock_method("service.read", file_path="images/sample.png"): ...

        # Mock method as an API response object with .text:
        with mock_method("client.call", as_response=True, data={"status": "ok"}): ...

        # Mock method to raise an exception:
        with mock_method("service.call", exception=RuntimeError("failed")): ...

        # Mock an object instance method directly:
        with mock_method(my_service, "process", return_value="done"): ...
    """
    if exception is not None:
        side_effect = exception

    final_return_value = return_value

    if as_response:
        final_return_value = _build_mock_response(
            text=text,
            content=read_as_bytes(file_path) if file_path else None,
            data=data,
            json_path=json_path,
            attrs=attrs,
            **extra_attrs,
        )
    else:
        if json_path is not None:
            final_return_value = read_as_json(json_path)
        elif file_path is not None:
            final_return_value = read_as_bytes(file_path)
        elif data is not None:
            final_return_value = data
        elif text is not None:
            final_return_value = text

    patch_kwargs: dict[str, Any] = {}
    if side_effect is not None:
        patch_kwargs["side_effect"] = side_effect
    if final_return_value is not _UNSET:
        patch_kwargs["return_value"] = final_return_value

    if method_name is not None and not isinstance(target, str):
        patcher = patch.object(target, method_name, **patch_kwargs)
    else:
        patcher = patch(target, **patch_kwargs)

    mock_obj = patcher.start()
    try:
        if not as_response:
            combined_attrs = {}
            if attrs:
                combined_attrs.update(attrs)
            combined_attrs.update(extra_attrs)
            for key, val in combined_attrs.items():
                setattr(mock_obj, key, val)
        yield mock_obj
    finally:
        patcher.stop()


@contextmanager
def mock_attribute(
    target: Any,
    attribute_name: str | None = None,
    value: Any = None,
):
    """Context manager to temporarily override an attribute or setting."""
    if attribute_name is None:
        patcher = patch(target, value)
    else:
        patcher = patch.object(target, attribute_name, value)

    patched = patcher.start()
    try:
        yield patched
    finally:
        patcher.stop()


def mock_generate_content(
    json_path: str | None = None,
    *,
    data: Any = None,
    text: str | None = None,
    return_value: Any = _UNSET,
    side_effect: Any = None,
    exception: Exception | type[Exception] | None = None,
    attrs: dict[str, Any] | None = None,
    **extra_attrs: Any,
):
    """Patch the extractor's Gemini generate_content call."""
    return mock_method(
        TARGET_EXTRACTOR_GENERATE_CONTENT,
        return_value=return_value,
        data=data,
        json_path=json_path,
        text=text,
        as_response=True,
        side_effect=side_effect,
        exception=exception,
        attrs=attrs,
        **extra_attrs,
    )


def mock_empty_generate_content():
    """Patch the extractor's Gemini call to return an empty string response."""
    return mock_generate_content(text="")


def mock_none_generate_content():
    """Patch the extractor's Gemini call to return a None response."""
    return mock_generate_content(text=None)


def mock_extractor_exception(exception: Exception | type[Exception]):
    """Patch the extractor's Gemini call to raise an exception."""
    return mock_generate_content(exception=exception)


class MockHelper:
    """Generic mock helper class namespace."""

    TARGET_EXTRACTOR_GENERATE_CONTENT = TARGET_EXTRACTOR_GENERATE_CONTENT

    mock_method = staticmethod(mock_method)
    mock_attribute = staticmethod(mock_attribute)
    mock_generate_content = staticmethod(mock_generate_content)
    mock_empty_generate_content = staticmethod(mock_empty_generate_content)
    mock_none_generate_content = staticmethod(mock_none_generate_content)
    mock_extractor_exception = staticmethod(mock_extractor_exception)
