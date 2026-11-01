"""Public Solis protocol interoperability. No TLS session or account secrets."""

import gzip, hashlib, struct, datetime, re, io
from pathlib import Path
from google.protobuf import (
    descriptor_pb2,
    descriptor_pool,
    message_factory,
    json_format,
)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

SOURCE = Path(__file__).parent / "resources/public-solis-marshaler.go"
public_key = re.search(r'const KEY = "([^"]+)"', SOURCE.read_text()).group(1).encode()
aeskey = hashlib.md5(public_key).digest()


def safe_gzip(data):
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
        body = stream.read(128 * 1024 * 1024 + 1)
    if len(body) > 128 * 1024 * 1024:
        raise ValueError("Decompressed response exceeds limit")
    return body


def frames(data, encoding):
    result = []
    at = 0
    while at < len(data):
        if not at + 5 <= len(data):
            raise ValueError("Incomplete gRPC frame header")
        flags = data[at]
        n = int.from_bytes(data[at + 1 : at + 5], "big")
        if not (flags in (0, 1) and at + 5 + n <= len(data)):
            raise ValueError("Incomplete or unsupported gRPC frame")
        wire = data[at + 5 : at + 5 + n]
        at += 5 + n
        content = wire
        if flags:
            if not encoding == "gzip":
                raise ValueError("Unsupported grpc-encoding")
            content = safe_gzip(content)
        meta = {
            "grpc_compressed": bool(flags),
            "grpc_encoding": encoding,
            "wire_message_bytes": n,
            "empty_protobuf_message": n == 0,
            "qua_envelope": False,
        }
        if content:
            if not len(content) >= 4:
                raise ValueError("Nonempty message lacks Qua header")
            header_len = content[3]
            if not (
                content[0] == header_len + 2
                and content[1] == 0
                and (content[2] in (0, 1))
            ):
                raise ValueError("Not pinned Qua envelope")
            if not (
                len(content) >= 4 + header_len + 16
                and (len(content) - 4 - header_len) % 16 == 0
            ):
                raise ValueError("Invalid Qua AES-CBC body length")
            iv = hashlib.md5(public_key + content[4 : 4 + header_len]).digest()
            decryptor = Cipher(algorithms.AES(aeskey), modes.CBC(iv)).decryptor()
            padded = decryptor.update(content[4 + header_len :]) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plain = unpadder.update(padded) + unpadder.finalize()
            compressed = bool(content[2])
            if compressed:
                plain = safe_gzip(plain)
            meta.update(
                qua_envelope=True,
                qua_header_bytes=header_len,
                qua_gzip=compressed,
                protobuf_bytes=len(plain),
            )
            content = plain
        else:
            meta["protobuf_bytes"] = 0
        if not len(content) <= 256 * 1024 * 1024:
            raise ValueError("Invalid wire response")
        result.append((meta, content))
    return result


def schema():
    fds = descriptor_pb2.FileDescriptorSet.FromString(
        (Path(__file__).parent / "resources/schema.pb").read_bytes()
    )
    pool = descriptor_pool.DescriptorPool()
    pending = list(fds.file)
    while pending:
        left = []
        for f in pending:
            try:
                pool.Add(f)
            except TypeError:
                left.append(f)
        if len(left) == len(pending):
            raise ValueError("Unresolved schema dependencies")
        pending = left
    return pool


POOL = schema()


def descriptor(path):
    return POOL.FindMethodByName(path[1:].replace("/", "."))


def encode(desc, values):
    obj = message_factory.GetMessageClass(desc)()
    json_format.ParseDict(values, obj)
    return obj.SerializeToString()


def decode(desc, data):
    obj = message_factory.GetMessageClass(desc)()
    obj.ParseFromString(data)
    return json_format.MessageToDict(obj, preserving_proto_field_name=True)


def pack(data):
    if not data:
        return b""
    delta = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime(
        1, 1, 1, tzinfo=datetime.timezone.utc
    )
    nonce = (
        (delta.days * 86400 + delta.seconds) * 10000000 + delta.microseconds * 10
    ).to_bytes(8, "little")
    padder = padding.PKCS7(128).padder()
    body = padder.update(data) + padder.finalize()
    encryptor = Cipher(
        algorithms.AES(aeskey), modes.CBC(hashlib.md5(public_key + nonce).digest())
    ).encryptor()
    return (
        struct.pack("<HBB", 10, 0, 8)
        + nonce
        + encryptor.update(body)
        + encryptor.finalize()
    )
