from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status

from app.settings import Settings

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ("photo", ".jpg"),
    "image/png": ("photo", ".png"),
    "image/webp": ("photo", ".webp"),
    "video/mp4": ("video", ".mp4"),
    "video/quicktime": ("video", ".mov"),
}
CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class StoredFile:
    asset_type: str
    bucket_name: str
    object_key: str
    content_type: str
    byte_size: int
    checksum_sha256: str


class LocalStorage:
    def __init__(self, settings: Settings) -> None:
        self.root = Path(settings.local_storage_root)
        self.bucket_name = settings.local_storage_bucket
        self.max_bytes = settings.local_file_max_bytes

    async def save_upload(self, user_id: UUID, record_id: UUID, file: UploadFile) -> StoredFile:
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file content type.",
            )

        asset_type, suffix = ALLOWED_CONTENT_TYPES[content_type]
        object_key = f"users/{user_id}/records/{record_id}/assets/{uuid4()}{suffix}"
        target_path = self.resolve_path(object_key)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        checksum = sha256()
        byte_size = 0

        try:
            with target_path.open("wb") as output:
                while chunk := await file.read(CHUNK_SIZE):
                    byte_size += len(chunk)
                    if byte_size > self.max_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="Uploaded file is too large.",
                        )
                    checksum.update(chunk)
                    output.write(chunk)
        except Exception:
            target_path.unlink(missing_ok=True)
            raise
        finally:
            await file.close()

        return StoredFile(
            asset_type=asset_type,
            bucket_name=self.bucket_name,
            object_key=object_key,
            content_type=content_type,
            byte_size=byte_size,
            checksum_sha256=checksum.hexdigest(),
        )

    def resolve_path(self, object_key: str) -> Path:
        path = (self.root / object_key).resolve()
        root = self.root.resolve()
        if root not in path.parents and path != root:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid object key.",
            )
        return path

    def delete(self, object_key: str) -> None:
        path = self.resolve_path(object_key)
        path.unlink(missing_ok=True)
