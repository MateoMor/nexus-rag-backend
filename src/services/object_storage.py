from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Dict, Iterable, List, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile

from src.core.config import settings

logger = logging.getLogger(__name__)


class ObjectStorageError(Exception):
	"""Custom exception for object storage operations."""


@dataclass(slots=True)
class ObjectStorageUploadResult:
	"""Metadata returned after uploading a file to object storage."""

	key: str
	bucket: str
	size: int
	etag: Optional[str]
	url: Optional[str]


@dataclass(slots=True)
class ObjectStorageObject:
	"""Representation of an object stored in the bucket."""

	key: str
	size: int
	last_modified: Optional[datetime]
	url: Optional[str]

	@property
	def filename(self) -> str:
		return self.key.split("/")[-1]


class ObjectStorageService:
	"""Service layer for interacting with Cloudflare R2 (S3-compatible) storage."""

	def __init__(self) -> None:
		self._validate_configuration()

		self.bucket: str = settings.R2_BUCKET_NAME or ""
		self.endpoint_url: str = self._resolve_endpoint_url()
		self.public_base_url: Optional[str] = (
			settings.R2_PUBLIC_BASE_URL.rstrip("/") if settings.R2_PUBLIC_BASE_URL else None
		)

		self.client = boto3.client(
			"s3",
			region_name="auto",
			endpoint_url=self.endpoint_url,
			aws_access_key_id=settings.R2_ACCESS_KEY_ID,
			aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
			config=Config(signature_version="s3v4"),
		)

		logger.debug("ObjectStorageService initialized for bucket '%s'", self.bucket)

	async def upload_file(
		self,
		file: UploadFile,
		*,
		destination_path: Optional[str] = None,
		metadata: Optional[Dict[str, str]] = None,
	) -> ObjectStorageUploadResult:
		"""Upload an incoming FastAPI UploadFile to the configured bucket."""

		if not file.filename:
			raise ObjectStorageError("El archivo proporcionado no tiene nombre válido.")

		key = destination_path or self.build_key(file.filename)
		safe_metadata = self._prepare_metadata(metadata, original_filename=file.filename)

		content = await file.read()
		size = len(content)

		if size == 0:
			raise ObjectStorageError("El archivo está vacío. Nada que subir al bucket.")

		content_type = file.content_type or "application/octet-stream"

		try:
			response = await asyncio.to_thread(
				self.client.put_object,
				Bucket=self.bucket,
				Key=key,
				Body=content,
				ContentType=content_type,
				Metadata=safe_metadata,
			)
		except ClientError as exc:
			logger.exception("Error subiendo archivo '%s' al bucket.", key)
			raise ObjectStorageError(str(exc)) from exc

		try:
			await file.seek(0)
		except Exception:
			# No es crítico si no logramos reposicionar el cursor del archivo.
			pass

		upload_result = ObjectStorageUploadResult(
			key=key,
			bucket=self.bucket,
			size=size,
			etag=response.get("ETag"),
			url=self._build_public_url(key),
		)

		logger.info(
			"Archivo '%s' subido correctamente a R2 (bucket=%s, size=%s bytes)",
			key,
			self.bucket,
			size,
		)

		return upload_result

	async def list_objects(
		self,
		*,
		prefix: Optional[str] = None,
		max_keys: int = 1000,
	) -> List[ObjectStorageObject]:
		"""List objects from the bucket, optionally filtered by prefix."""
		effective_max_keys = max(1, min(max_keys, 1000))
		clean_prefix = prefix.strip("/") if prefix else None

		objects: List[ObjectStorageObject] = []
		continuation_token: Optional[str] = None

		while True:
			request_params = {"Bucket": self.bucket, "MaxKeys": effective_max_keys}
			if clean_prefix:
				request_params["Prefix"] = clean_prefix
			if continuation_token:
				request_params["ContinuationToken"] = continuation_token

			try:
				response = await asyncio.to_thread(self.client.list_objects_v2, **request_params)
			except ClientError as exc:
				logger.exception("No se pudo listar objetos con el prefijo '%s'", prefix)
				raise ObjectStorageError(str(exc)) from exc

			for item in response.get("Contents", []):
				key = item["Key"]
				objects.append(
					ObjectStorageObject(
						key=key,
						size=item.get("Size", 0),
						last_modified=item.get("LastModified"),
						url=self._build_public_url(key),
					)
				)

			if not response.get("IsTruncated") or len(objects) >= max_keys:
				break

			continuation_token = response.get("NextContinuationToken")

		return objects[:max_keys]

	async def delete_objects(self, keys: Iterable[str]) -> int:
		"""Delete multiple objects from the bucket."""

		key_list = [key for key in keys if key]
		if not key_list:
			return 0

		delete_payload = {"Objects": [{"Key": key} for key in key_list], "Quiet": True}

		try:
			await asyncio.to_thread(
				self.client.delete_objects,
				Bucket=self.bucket,
				Delete=delete_payload,
			)
		except ClientError as exc:
			logger.exception("No se pudieron eliminar los objetos: %s", key_list)
			raise ObjectStorageError(str(exc)) from exc

		logger.info("Eliminados %d objetos del bucket R2", len(key_list))
		return len(key_list)

	async def delete_prefix(self, prefix: str) -> int:
		"""Delete all objects under a given prefix."""

		normalized_prefix = prefix.strip("/")
		if not normalized_prefix:
			raise ObjectStorageError("El prefijo proporcionado no es válido.")

		total_deleted = 0

		while True:
			objects = await self.list_objects(prefix=normalized_prefix, max_keys=1000)
			if not objects:
				break

			total_deleted += await self.delete_objects(obj.key for obj in objects)

			if len(objects) < 1000:
				break

		return total_deleted

	async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
		"""Generate a temporary signed URL for a given object key."""

		try:
			url = await asyncio.to_thread(
				self.client.generate_presigned_url,
				"get_object",
				Params={"Bucket": self.bucket, "Key": key},
				ExpiresIn=expires_in,
			)
		except ClientError as exc:
			logger.exception("No se pudo generar URL presignada para '%s'", key)
			raise ObjectStorageError(str(exc)) from exc

		return url

	def build_key(self, filename: str, prefix: Optional[str] = None) -> str:
		"""Build a storage key applying optional prefix and sanitizing the filename."""

		safe_name = self._sanitize_filename(filename)
		if prefix:
			clean_prefix = prefix.strip("/")
			return f"{clean_prefix}/{safe_name}"
		return safe_name

	def _validate_configuration(self) -> None:
		required_fields = {
			"R2_ACCESS_KEY_ID": settings.R2_ACCESS_KEY_ID,
			"R2_SECRET_ACCESS_KEY": settings.R2_SECRET_ACCESS_KEY,
			"R2_BUCKET_NAME": settings.R2_BUCKET_NAME,
		}

		missing = [field for field, value in required_fields.items() if not value]
		if missing:
			raise ObjectStorageError(
				"Faltan variables de entorno necesarias para R2: " + ", ".join(missing)
			)

		if not settings.R2_ENDPOINT_URL and not settings.R2_ACCOUNT_ID:
			raise ObjectStorageError(
				"Debes definir R2_ACCOUNT_ID o proporcionar R2_ENDPOINT_URL para construir el endpoint de R2."
			)

	def _resolve_endpoint_url(self) -> str:
		if settings.R2_ENDPOINT_URL:
			return settings.R2_ENDPOINT_URL.rstrip("/")
		return f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

	def _build_public_url(self, key: str) -> Optional[str]:
		if not self.public_base_url:
			return None
		return f"{self.public_base_url}/{key}"

	@staticmethod
	def _prepare_metadata(
		metadata: Optional[Dict[str, str]], *, original_filename: Optional[str] = None
	) -> Dict[str, str]:
		meta = {k: str(v) for k, v in (metadata or {}).items() if v is not None}
		if original_filename:
			meta.setdefault("original_filename", original_filename)
		return meta

	@staticmethod
	def _sanitize_filename(filename: str) -> str:
		base = filename.strip()
		base = base.replace("\\", "/").split("/")[-1]
		base = re.sub(r"[^A-Za-z0-9_.-]", "_", base)
		return base or "file"


@lru_cache(maxsize=1)
def get_object_storage_service() -> ObjectStorageService:
	"""Return a singleton instance of the object storage service."""

	return ObjectStorageService()
