#!/usr/bin/env python3
"""Create and validate deterministic responsive WebP variants for VOweb assets."""
from __future__ import annotations

import argparse
import hashlib
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source-assets" / "b2b-vorigin-partner.png"
PUBLIC = ROOT / "public" / "assets"
EXPECTED_SOURCE_SHA256 = "5aabfff04d20b85499e4d6ea22eeba2b4b6924293e72134896677a3e93cc48f5"
EXPECTED_SOURCE_SIZE = (1020, 818)


@dataclass(frozen=True)
class Variant:
    width: int
    filename: str
    quality: int
    max_bytes: int


@dataclass(frozen=True)
class ResponsiveAsset:
    key: str
    source_filename: str
    source_size: tuple[int, int]
    variants: tuple[Variant, ...]


VARIANTS = (
    Variant(640, "b2b-vorigin-partner-640w.webp", 80, 120_000),
    Variant(1020, "b2b-vorigin-partner-1020w.webp", 82, 250_000),
)
RESPONSIVE_SPECS = {
    "hero-marigold-premium": ResponsiveAsset(
        "hero-marigold-premium", "hero-marigold-premium.webp", (1494, 1065),
        (Variant(480, "hero-marigold-premium-480w.webp", 80, 120_000),
         Variant(768, "hero-marigold-premium-768w.webp", 80, 190_000)),
    ),
    "marigold-lineup-premium": ResponsiveAsset(
        "marigold-lineup-premium", "marigold-lineup-premium.webp", (1300, 500),
        (Variant(480, "marigold-lineup-premium-480w.webp", 80, 60_000),
         Variant(768, "marigold-lineup-premium-768w.webp", 80, 100_000)),
    ),
}
for _flavor in ("apple", "orange", "mango", "grape"):
    _key = f"marigold-{_flavor}-premium"
    RESPONSIVE_SPECS[_key] = ResponsiveAsset(
        _key, f"{_key}.webp", (780, 840),
        (Variant(390, f"{_key}-390w.webp", 80, 45_000),
         Variant(640, f"{_key}-640w.webp", 80, 90_000)),
    )
Mode = Literal["write", "check"]


@dataclass(frozen=True)
class Report:
    mode: Mode
    source_sha256: str
    variants: tuple[tuple[str, int, str], ...]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_source() -> bytes:
    if not SOURCE.is_file():
        raise RuntimeError(f"missing canonical source: {SOURCE}")
    data = SOURCE.read_bytes()
    digest = sha256(data)
    if digest != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            "canonical source hash mismatch: "
            f"expected {EXPECTED_SOURCE_SHA256}, got {digest}"
        )
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format != "PNG" or image.mode != "RGB" or image.size != EXPECTED_SOURCE_SIZE:
                raise RuntimeError(
                    "canonical source metadata mismatch: "
                    f"expected PNG RGB {EXPECTED_SOURCE_SIZE}, "
                    f"got {image.format} {image.mode} {image.size}"
                )
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError(f"canonical source is not a readable PNG: {exc}") from exc
    return data


def render_variant(source_data: bytes, variant: Variant) -> bytes:
    with Image.open(io.BytesIO(source_data)) as source:
        source.load()
        width = variant.width
        height = round(source.height * width / source.width)
        if width > source.width or height > source.height:
            raise RuntimeError(f"refusing to upscale {variant.filename}")
        image = source.convert("RGB")
        if image.size != (width, height):
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(
            output,
            format="WEBP",
            lossless=False,
            quality=variant.quality,
            method=6,
            exact=False,
        )
        return output.getvalue()


def validate_variant(data: bytes, variant: Variant, source_size: tuple[int, int] = EXPECTED_SOURCE_SIZE) -> None:
    expected_size = (variant.width, round(source_size[1] * variant.width / source_size[0]))
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format != "WEBP" or image.mode != "RGB" or image.size != expected_size:
                raise RuntimeError(
                    f"{variant.filename}: expected WebP RGB {expected_size}, "
                    f"got {image.format} {image.mode} {image.size}"
                )
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError(f"{variant.filename}: invalid WebP: {exc}") from exc
    if len(data) > variant.max_bytes:
        raise RuntimeError(
            f"{variant.filename}: size {len(data)} exceeds {variant.max_bytes} bytes"
        )


def expected_variant_paths() -> set[Path]:
    paths = {PUBLIC / variant.filename for variant in VARIANTS}
    for spec in RESPONSIVE_SPECS.values():
        paths.update(PUBLIC / variant.filename for variant in spec.variants)
    return paths


def check_file_set() -> None:
    actual = {path for path in PUBLIC.glob("*.webp") if any(path.name == candidate.name for candidate in expected_variant_paths())}
    expected = expected_variant_paths()
    if actual != expected:
        missing = sorted(str(path.relative_to(ROOT)) for path in expected - actual)
        extra = sorted(str(path.relative_to(ROOT)) for path in actual - expected)
        details = []
        if missing:
            details.append(f"missing={missing}")
        if extra:
            details.append(f"unexpected={extra}")
        raise RuntimeError("variant file set drift: " + ", ".join(details))


def optimize_image(source: Path, variants: tuple[Variant, ...], mode: Mode) -> Report:
    if source != SOURCE:
        raise RuntimeError(f"unsupported source path: {source}")
    source_data = read_source()
    if mode == "write":
        PUBLIC.mkdir(parents=True, exist_ok=True)
    rendered: list[tuple[str, int, str]] = []
    for variant in variants:
        data = render_variant(source_data, variant)
        validate_variant(data, variant)
        target = PUBLIC / variant.filename
        if mode == "write":
            if not target.exists() or target.read_bytes() != data:
                target.write_bytes(data)
        elif not target.is_file():
            raise RuntimeError(f"missing generated variant: {target}")
        else:
            existing = target.read_bytes()
            if existing != data:
                raise RuntimeError(
                    f"byte/hash drift in {target.relative_to(ROOT)}: "
                    f"expected {sha256(data)}, got {sha256(existing)}"
                )
        rendered.append((variant.filename, len(data), sha256(data)))
    if mode == "check":
        check_file_set()
    return Report(mode, sha256(source_data), tuple(rendered))


def optimize_responsive_asset(spec: ResponsiveAsset, mode: Mode) -> Report:
    source = PUBLIC / spec.source_filename
    if not source.is_file():
        raise RuntimeError(f"missing responsive source: {source}")
    source_data = source.read_bytes()
    try:
        with Image.open(io.BytesIO(source_data)) as image:
            if image.format != "WEBP" or image.mode != "RGB" or image.size != spec.source_size:
                raise RuntimeError(
                    f"{spec.source_filename}: expected WebP RGB {spec.source_size}, "
                    f"got {image.format} {image.mode} {image.size}"
                )
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError(f"{spec.source_filename}: invalid source: {exc}") from exc
    if mode == "write":
        PUBLIC.mkdir(parents=True, exist_ok=True)
    rendered=[]
    for variant in spec.variants:
        data=render_variant(source_data, variant)
        validate_variant(data, variant, spec.source_size)
        target=PUBLIC / variant.filename
        if mode == "write":
            if not target.exists() or target.read_bytes()!=data: target.write_bytes(data)
        elif not target.is_file():
            raise RuntimeError(f"missing generated variant: {target}")
        elif target.read_bytes()!=data:
            raise RuntimeError(f"byte/hash drift in {target.relative_to(ROOT)}: expected {sha256(data)}, got {sha256(target.read_bytes())}")
        rendered.append((variant.filename,len(data),sha256(data)))
    return Report(mode, sha256(source_data), tuple(rendered))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write deterministic WebP variants")
    mode.add_argument("--check", action="store_true", help="validate without mutating files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode: Mode = "write" if args.write else "check"
    try:
        report = optimize_image(SOURCE, VARIANTS, mode)
        reports = [report]
        for spec in RESPONSIVE_SPECS.values():
            reports.append(optimize_responsive_asset(spec, mode))
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    for report in reports:
        print(f"PASS: {report.mode}; source sha256={report.source_sha256}")
        for filename, size, digest in report.variants:
            print(f"  {filename}: {size} bytes sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
