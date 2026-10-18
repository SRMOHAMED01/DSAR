import os
import json
import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text
import structlog

logger = structlog.get_logger()


class DSAREngine:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", "postgresql://Mohamed:12345@localhost:5432/dsar_db"
        )
        self.engine = create_engine(self.database_url)
        self.sensitive_fields = [
            "ssn",
            "social_security_number",
            "email",
            "phone",
            "phone_number",
            "address",
            "customer_id",
            "full_name",
            "name",
        ]

    def _mask_sensitive_data(self, value: Any, field_name: str) -> Any:
        if value is None:
            return value
        field_lower = str(field_name).lower()
        if any(s in field_lower for s in self.sensitive_fields):
            if isinstance(value, str):
                if field_lower in ("email",):
                    parts = value.split("@")
                    if len(parts) == 2:
                        return f"{parts[0][:2]}***@{parts[1]}"
                    return "***"
                elif field_lower in ("ssn", "social_security_number"):
                    return "XXX-XX-****"
                elif field_lower in ("phone", "phone_number"):
                    digits = ''.join(c for c in value if c.isdigit())
                    if len(digits) >= 4:
                        return f"***-***-{digits[-4:]}"
                    return "***"
                elif field_lower in ("customer_id",):
                    return f"{str(value)[:3]}***"
                else:
                    return "***"
        return value

    def discover_data(self, identifier: str, identifier_type: str = "email") -> Dict[str, List[Dict]]:
        """Discover all data associated with a subject identifier"""
        results = {}
        with self.engine.connect() as conn:
            tables_query = text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_type='BASE TABLE' 
                AND table_schema IN ('raw', 'public')
                ORDER BY table_schema, table_name
            """)
            tables = conn.execute(tables_query).fetchall()

            for schema, table in tables:
                try:
                    columns_query = text(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema = '{schema}' AND table_name = '{table}'
                        ORDER BY ordinal_position
                    """)
                    cols = conn.execute(columns_query).fetchall()
                    col_names = [c[0] for c in cols]

                    match_col = None
                    if identifier_type == "email":
                        match_col = next((c for c in col_names if 'email' in c.lower()), None)
                    elif identifier_type == "customer_id":
                        match_col = next((c for c in col_names if 'customer' in c.lower() and 'id' in c.lower()), None)
                    elif identifier_type == "name":
                        match_col = next((c for c in col_names if 'name' in c.lower()), None)

                    if not match_col:
                        for c in col_names:
                            if identifier.lower() in str(c).lower() or str(c).lower() in identifier.lower():
                                match_col = c
                                break

                    if match_col:
                        select_query = text(f"SELECT * FROM {schema}.{table} WHERE {match_col} ILIKE :ident")
                        rows = conn.execute(select_query, {"ident": f"%{identifier}%"}).fetchall()
                        if rows:
                            results[f"{schema}.{table}"] = [dict(row._mapping) for row in rows]
                except Exception as e:
                    logger.error("table_discovery_error", table=f"{schema}.{table}", error=str(e))
                    continue
        return results

    def export_data(self, discovered_data: Dict[str, List[Dict]], export_format: str = "json", mask_data: bool = True) -> bytes:
        if export_format == "json":
            data = discovered_data
            if mask_data:
                data = self._mask_discovered_data(discovered_data)
            return json.dumps(data, default=str, indent=2).encode("utf-8")
        elif export_format == "csv":
            output = io.StringIO()
            if discovered_data:
                all_rows = []
                for table_rows in discovered_data.values():
                    all_rows.extend(table_rows)
                if all_rows:
                    if mask_data:
                        all_rows = [self._mask_dict(r) for r in all_rows]
                    writer = csv.DictWriter(output, fieldnames=all_rows[0].keys())
                    writer.writeheader()
                    writer.writerows(all_rows)
            return output.getvalue().encode("utf-8")
        else:
            return json.dumps(discovered_data, default=str).encode("utf-8")

    def _mask_discovered_data(self, discovered_data: Dict) -> Dict:
        masked = {}
        for key, rows in discovered_data.items():
            masked[key] = [self._mask_dict(r) for r in rows]
        return masked

    def _mask_dict(self, row: Dict) -> Dict:
        return {k: self._mask_sensitive_data(v, k) for k, v in row.items()}

    def log_audit(self, action: str, identifier: str, details: Dict[str, Any] = None):
        logger.info("dsar_audit", action=action, identifier=identifier, details=details or {})
