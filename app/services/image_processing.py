from base64 import b64encode
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.schemas.ai import ImageForAnalysis

MAX_IMAGE_SIDE = 1024
THUMBNAIL_SIZE = 512
OUTPUT_FORMAT_BY_CONTENT_TYPE = {
    "image/jpeg": ("JPEG", "image/jpeg"),
    "image/png": ("PNG", "image/png"),
    "image/webp": ("WEBP", "image/webp"),
}


def prepare_image_for_analysis(
    path: Path,
    content_type: str,
    max_bytes: int,
) -> ImageForAnalysis:
    if content_type not in OUTPUT_FORMAT_BY_CONTENT_TYPE:
        raise ValueError("Unsupported AI image content type.")

    data = resize_and_strip_metadata(path, content_type)
    if len(data) > max_bytes:
        raise ValueError("Image is larger than AI analysis limit.")

    return ImageForAnalysis(
        content_type=content_type,
        data_base64=b64encode(data).decode("ascii"),
    )


def resize_and_strip_metadata(path: Path, content_type: str) -> bytes:
    output_format, output_content_type = OUTPUT_FORMAT_BY_CONTENT_TYPE[content_type]
    try:
        with Image.open(path) as image:
            image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
            if output_format == "JPEG":
                image = image.convert("RGB")

            buffer = BytesIO()
            save_kwargs = {"format": output_format}
            if output_format in {"JPEG", "WEBP"}:
                save_kwargs["quality"] = 80
                save_kwargs["optimize"] = True
            image.save(buffer, **save_kwargs)
            return buffer.getvalue()
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError("Uploaded image cannot be decoded for AI analysis.") from exc


def create_square_thumbnail(path: Path, size: int = THUMBNAIL_SIZE) -> bytes:
    try:
        with Image.open(path) as image:
            image = image.convert("RGB")
            width, height = image.size
            edge = min(width, height)
            left = (width - edge) // 2
            top = (height - edge) // 2
            image = image.crop((left, top, left + edge, top + edge))
            image = image.resize((size, size), Image.Resampling.LANCZOS)

            buffer = BytesIO()
            image.save(buffer, format="WEBP", quality=82, optimize=True)
            return buffer.getvalue()
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError("Uploaded image cannot be decoded for thumbnail generation.") from exc
