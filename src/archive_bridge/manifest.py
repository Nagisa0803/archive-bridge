"""Read package/versionName from a bounded plain or binary Android manifest."""

import struct, xml.etree.ElementTree as ET
from .errors import BridgeError


def read_manifest(data):
    try:
        if data.lstrip().startswith(b"<"):
            root = ET.fromstring(data)
            return root.attrib.get("package"), root.attrib.get(
                "{http://schemas.android.com/apk/res/android}versionName"
            )
        if len(data) < 8 or struct.unpack_from("<H", data)[0] != 3:
            raise ValueError()
        strings = []
        at = struct.unpack_from("<H", data, 2)[0]
        total = struct.unpack_from("<I", data, 4)[0]
        if total > len(data):
            raise ValueError()
        while at + 8 <= total:
            kind, header, size = struct.unpack_from("<HHI", data, at)
            if header < 8 or size < header or at + size > total:
                raise ValueError()
            chunk = data[at : at + size]
            if kind == 1:
                count, styles, flags, start, _ = struct.unpack_from("<IIIII", chunk, 8)
                if count > 100000 or header + count * 4 > len(chunk):
                    raise ValueError()
                strings = []
                for index in range(count):
                    pos = start + struct.unpack_from("<I", chunk, header + index * 4)[0]
                    if flags & 256:

                        def length8(p):
                            first = chunk[p]
                            return (
                                (((first & 127) << 8) | chunk[p + 1], p + 2)
                                if first & 128
                                else (first, p + 1)
                            )

                        _, pos = length8(pos)
                        length, pos = length8(pos)
                        raw = chunk[pos : pos + length]
                        if len(raw) != length:
                            raise ValueError()
                        strings.append(raw.decode("utf-8"))
                    else:
                        length = struct.unpack_from("<H", chunk, pos)[0]
                        pos += 2
                        if length & 32768:
                            length = ((length & 32767) << 16) | struct.unpack_from(
                                "<H", chunk, pos
                            )[0]
                            pos += 2
                        raw = chunk[pos : pos + length * 2]
                        if len(raw) != length * 2:
                            raise ValueError()
                        strings.append(raw.decode("utf-16le"))
            elif kind == 258 and strings:
                name = struct.unpack_from("<I", chunk, 20)[0]
                if strings[name] == "manifest":
                    start, stride, count = struct.unpack_from("<HHH", chunk, 24)
                    if stride < 20 or 16 + start + count * stride > len(chunk):
                        raise ValueError()
                    attrs = {}
                    for index in range(count):
                        offset = 16 + start + index * stride
                        _, key, raw = struct.unpack_from("<III", chunk, offset)
                        value_type = chunk[offset + 15]
                        typed = struct.unpack_from("<I", chunk, offset + 16)[0]
                        if raw != 0xFFFFFFFF:
                            attrs[strings[key]] = strings[raw]
                        elif value_type == 3:
                            attrs[strings[key]] = strings[typed]
                    return attrs.get("package"), attrs.get("versionName")
            at += size
    except (ValueError, IndexError, struct.error, UnicodeError, ET.ParseError):
        pass
    raise BridgeError(
        "UNSUPPORTED_APK",
        "Could not read package and versionName from the original Android manifest.",
    )
