"""รูปที่อัปโหลดต้องไม่มีพิกัด GPS / ข้อมูลแฝงติดไปถึง AI"""
import io
import os

from PIL import Image

os.environ.setdefault("SECRET_KEY", "x" * 40)


def _jpeg_with_gps():
    im = Image.new("RGB", (40, 20), (200, 30, 30))
    ex = Image.Exif()
    ex[0x010F] = "PhoneMaker"                     # Make
    ex[0x0112] = 6                                # หมุน 90° ตอนแสดง
    ex[0x8825] = {1: "N", 2: (13.0, 45.0, 0.0), 3: "E", 4: (100.0, 30.0, 0.0)}   # GPS
    b = io.BytesIO(); im.save(b, "JPEG", exif=ex); return b.getvalue()


def test_gps_and_exif_removed_orientation_applied():
    import app
    raw = _jpeg_with_gps()
    assert Image.open(io.BytesIO(raw)).getexif().get(0x8825)            # ต้นฉบับมี GPS จริง
    out, mime = app._strip_image_metadata(raw, "image/jpeg")
    im = Image.open(io.BytesIO(out))
    assert mime == "image/jpeg" and not im.getexif() and "exif" not in im.info
    assert im.size == (20, 40)                                          # หมุนตามที่ถ่ายแล้ว ภาพไม่ตะแคง


def test_png_with_alpha_ok_and_wired_before_send():
    import app
    b = io.BytesIO(); Image.new("RGBA", (8, 8), (0, 0, 0, 0)).save(b, "PNG")
    out, mime = app._strip_image_metadata(b.getvalue(), "image/png")
    assert mime == "image/jpeg" and Image.open(io.BytesIO(out)).mode == "RGB"
    src = open("app.py", encoding="utf-8").read()
    body = src[src.index("def _analyze_image_sync("):]
    assert body.index("_strip_image_metadata(data, mime)") < body.index("Part.from_bytes")
