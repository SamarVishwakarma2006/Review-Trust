"""Multipart callbacks retain bounded bytes only; no UploadFile, File or temporary files."""

import logging
import re

from python_multipart import MultipartParser
from python_multipart.exceptions import MultipartParseError
from python_multipart.multipart import parse_options_header

from app.analysis import check_deadline
from app.ingestion import ReviewInputError, decode_json, parse_csv
from app.schemas import MAX_BODY_BYTES

_QUIET_PARSER_LOGGER = logging.Logger("reviewtrust.multipart", level=logging.CRITICAL + 1)
_FIELDS = {"file", "mapping", "category", "language", "schema_version"}
_FILE_TYPES = {
    b"text/csv",
    b"application/csv",
    b"text/plain",
    b"application/octet-stream",
    b"application/vnd.ms-excel",
}


def content_type(value: str):
    media, options = parse_options_header(value)
    charset = options.get(b"charset", b"utf-8").lower()
    if charset not in {b"utf-8", b"utf8"}:
        raise ReviewInputError("charset", "Only UTF-8 request encoding is supported.", 415)
    return media.lower(), options


def parse_upload(data: bytes, header: str, deadline: float):
    media, options = content_type(header)
    boundary = options.get(b"boundary", b"")
    if media != b"multipart/form-data":
        raise ReviewInputError("media_type", "CSV uploads require multipart/form-data.", 415)
    if not re.fullmatch(rb"[0-9A-Za-z'()+_,./:=? -]{1,70}", boundary) or boundary.endswith(b" "):
        raise ReviewInputError("multipart_boundary", "Supply a valid multipart boundary.", 400)
    if not data.rstrip(b"\r\n").endswith(b"--" + boundary + b"--"):
        raise ReviewInputError("multipart_incomplete", "Multipart upload is incomplete.", 400)
    fields = {}
    current = {}
    parts = 0
    complete = False

    def begin():
        nonlocal parts
        check_deadline(deadline)
        parts += 1
        if parts > len(_FIELDS):
            raise ReviewInputError("multipart_parts", "Too many upload parts.", 413)
        current.clear()
        current.update(
            headers={}, name_bytes=bytearray(), value_bytes=bytearray(), data=bytearray()
        )

    def header_field(chunk, start, end):
        current["name_bytes"].extend(chunk[start:end])

    def header_value(chunk, start, end):
        current["value_bytes"].extend(chunk[start:end])

    def header_end():
        name = bytes(current["name_bytes"]).lower()
        if name in current["headers"] or name not in {b"content-type", b"content-disposition"}:
            raise ReviewInputError(
                "multipart_header", "Unsupported or duplicate part headers.", 400
            )
        current["headers"][name] = bytes(current["value_bytes"])
        current["name_bytes"].clear()
        current["value_bytes"].clear()

    def headers_finished():
        disposition, params = parse_options_header(current["headers"].get(b"content-disposition"))
        name = params.get(b"name", b"").decode("ascii", errors="replace")
        if disposition != b"form-data" or name not in _FIELDS or name in fields:
            raise ReviewInputError(
                "multipart_field", "Use one file and unique supported form fields."
            )
        if (name == "file") != (b"filename" in params):
            raise ReviewInputError(
                "multipart_file", "Only the file field may contain an uploaded file."
            )
        if name == "file" and not params[b"filename"]:
            raise ReviewInputError("multipart_file", "Choose a CSV file to upload.")
        if name == "file":
            part_type, _ = content_type(
                current["headers"]
                .get(b"content-type", b"application/octet-stream")
                .decode("latin-1")
            )
            if part_type not in _FILE_TYPES:
                raise ReviewInputError("file_media_type", "Upload a UTF-8 CSV file.", 415)
        current["name"] = name

    def part_data(chunk, start, end):
        check_deadline(deadline)
        limit = (
            MAX_BODY_BYTES
            if current["name"] == "file"
            else (4096 if current["name"] == "mapping" else 64)
        )
        if len(current["data"]) + end - start > limit:
            raise ReviewInputError(
                "multipart_field_limit", "An upload field exceeds its limit.", 413
            )
        current["data"].extend(chunk[start:end])

    def part_end():
        fields[current["name"]] = bytes(current["data"])

    def end():
        nonlocal complete
        complete = True

    parser = MultipartParser(
        boundary,
        {
            "on_part_begin": begin,
            "on_header_field": header_field,
            "on_header_value": header_value,
            "on_header_end": header_end,
            "on_headers_finished": headers_finished,
            "on_part_data": part_data,
            "on_part_end": part_end,
            "on_end": end,
        },
        max_size=MAX_BODY_BYTES,
        max_header_count=2,
        max_header_size=8192,
    )
    # Library diagnostics can include malformed header bytes; keep raw input out of logs.
    parser.logger = _QUIET_PARSER_LOGGER
    try:
        for start in range(0, len(data), 16_384):
            check_deadline(deadline)
            parser.write(data[start : start + 16_384])
        parser.finalize()
    except MultipartParseError:
        raise ReviewInputError(
            "malformed_multipart", "Check the multipart upload format.", 400
        ) from None
    if not complete:
        raise ReviewInputError("multipart_incomplete", "Multipart upload is incomplete.", 400)
    if not {"file", "category", "language", "schema_version"} <= fields.keys():
        raise ReviewInputError(
            "multipart_required", "File, category, language and schema_version are required."
        )
    try:
        metadata = {
            name: fields[name].decode("utf-8")
            for name in ("category", "language", "schema_version")
        }
    except UnicodeDecodeError:
        raise ReviewInputError("form_encoding", "Form fields must be UTF-8.", 415) from None
    mapping = decode_json(fields["mapping"]) if "mapping" in fields else None
    if "mapping" in fields and not isinstance(mapping, dict):
        raise ReviewInputError("csv_mapping", "Column mapping must be a JSON object.")
    result = parse_csv(fields["file"], mapping=mapping, **metadata)
    check_deadline(deadline)
    return result
