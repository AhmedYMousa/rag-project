import hashlib
import uuid


def generate_document_id(file_contet: bytes) -> str:
    # Idempotent operation of generation the same hash using file's binaries
    file_hash = hashlib.sha256(file_contet).hexdigest()

    return str(uuid.uuid5(uuid.NAMESPACE_DNS, file_hash))


def generate_chunk_ids(document_id: str, chunks_count: int) -> list[str]:
    # Convert document_id to UUID first then store it as the namespace for file's own chunks
    file_namespace = uuid.UUID(document_id)

    return [str(uuid.uuid5(file_namespace, str(i))) for i in range(chunks_count)]
