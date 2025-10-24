from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceNotFoundError
import os, hashlib

class TableFingerprintStore:
    def __init__(self):
        self.table_name = os.getenv("CHUNK_STORAGE_TABLE_NAME", "chunkfingerprints").lower()
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.service = TableServiceClient.from_connection_string(conn_str)
        self.table = self.service.get_table_client(self.table_name)

        try:
            self.table.create_table()
        except Exception:
            pass  # Table already exists

    def compute_fingerprint(self, text, section="", filename="", url=""):
        raw = f"{text.strip()}|{section}|{filename}|{url}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, chunk_id, filename):
        pk = self._safe_key(filename)
        rk = self._safe_key(chunk_id)
        try:
            entity = self.table.get_entity(partition_key=pk, row_key=rk)
            return entity.get("fingerprint")
        except ResourceNotFoundError:
            return None
    def save(self):
     pass  # Azure Table Storage writes are immediate


    def _safe_key(self, value, max_len=1024):
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:max_len]
    
    def store_fp(self, chunk_id, fingerprint, section, filename):
        pk = self._safe_key(filename)
        rk = self._safe_key(chunk_id)

        entity = {
            "PartitionKey": pk,
            "RowKey": rk,
            "fingerprint": fingerprint,
            "section": section[:500],  # safe for display
            "filename": filename[:1024],  # truncate for safety
            "chunk_id": chunk_id[:1024]   # truncate for safety
        }

        # print(f"🧪 PK length: {len(pk)}")
        # print(f"🧪 RK length: {len(rk)}")
        # print(f"🧪 Section length: {len(section)}")
        # print(f"🧪 Fingerprint length: {len(fingerprint)}")
        # print(f"🧪 Entity: {entity}")

        self.table.upsert_entity(entity, mode=UpdateMode.REPLACE)