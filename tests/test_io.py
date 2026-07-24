import aion


def test_atomic_write(tmp_path):
    path = tmp_path / "sample.txt"
    aion.io.atomic_write(path, "hello")
    assert path.read_text(encoding="utf-8") == "hello"


def test_atomic_write_bytes(tmp_path):
    path = tmp_path / "sample.bin"
    aion.io.atomic_write_bytes(path, b"\x00\x01\x02")
    assert path.read_bytes() == b"\x00\x01\x02"


def test_iter_lines(tmp_path):
    path = tmp_path / "lines.txt"
    path.write_text("a\nb\nc\n", encoding="utf-8")
    assert list(aion.io.iter_lines(path)) == ["a", "b", "c"]


def test_read_chunks(tmp_path):
    path = tmp_path / "chunks.bin"
    path.write_bytes(b"abcdef")
    chunks = list(aion.io.read_chunks(path, size=2))
    assert b"".join(chunks) == b"abcdef"
