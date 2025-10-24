from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import hashlib, os, re
from dotenv import load_dotenv

load_dotenv()

class FingerprintStore:
    def __init__(self, table_name=os.getenv("CHUNK_STORAGE_TABLE_NAME")):
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        service = TableServiceClient.from_connection_string(conn_str)
        self.table = service.get_table_client(table_name)

    def compute_fingerprint(self, text, section="", filename="", url=""):
        raw = f"{text.strip().lower()}|{section.strip().lower()}|{filename.strip().lower()}|{url.strip().lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def sanitize_key(self, value, max_len=1024):
        value = re.sub(r'[\/\\#\?]', '_', value)
        value = ''.join(c for c in value if ord(c) >= 32)
        value = re.sub(r'^_+', '', value)
        value = value.strip()
        return ("doc_" + value[:max_len]) if value else "doc_unknown"

    def get(self, chunk_id, filename):
        pk = self.sanitize_key(filename)
        rk = self.sanitize_key(chunk_id)
        try:
            entity = self.table.get_entity(partition_key=pk, row_key=rk)
            return entity.get("fingerprint")
        except ResourceNotFoundError:
            return None

    def store(self, chunk_id, fingerprint, section, filename):
        pk = self.sanitize_key(filename)
        rk = self.sanitize_key(chunk_id)
        entity = {
            "PartitionKey": pk,
            "RowKey": rk,
            "fingerprint": fingerprint,
            "section": self.sanitize_key(section, max_len=500),
            "filename": filename[:1024],  # optional: store original
            "chunk_id": chunk_id[:1024]   # optional: store original
        }
        try:
            self.table.create_entity(entity)
        except ResourceExistsError:
            self.table.upsert_entity(entity, mode="replace")