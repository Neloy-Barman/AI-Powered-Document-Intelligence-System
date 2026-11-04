import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class InvoiceDocument(Base):
    __tablename__ = "invoice_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    page_no: Mapped[int | None] = mapped_column(Integer, nullable=True)

    invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    invoice_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    supplier_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    tax: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    total: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    line_items: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)

    has_missing_fields: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_numeric_issues: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_consistency_issues: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_duplicate_issues: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    missing_fields: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    numeric_issues: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    consistency_issues: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    duplicate_issues: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    raw_extraction: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    qdrant_point_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bm25_entry_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    document = relationship("Document", back_populates="invoice_document")
