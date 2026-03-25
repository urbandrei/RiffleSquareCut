import enum
from datetime import datetime, date

from sqlalchemy import (
    String, Text, Numeric, Integer, Boolean, Date, DateTime,
    ForeignKey, Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .engine import Base


# ── Enums ────────────────────────────────────────────────────────────

class PaymentMethod(enum.Enum):
    cash = "cash"
    card = "card"
    check = "check"
    online = "online"
    stripe = "stripe"
    paypal = "paypal"
    venmo = "venmo"
    cashapp = "cashapp"
    other = "other"


class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    refunded = "refunded"
    failed = "failed"


class SaleChannel(enum.Enum):
    in_person = "in_person"
    online = "online"
    ebay = "ebay"
    convention = "convention"
    business = "business"
    etsy = "etsy"
    meetup = "meetup"
    other = "other"


class InvoiceStatus(enum.Enum):
    draft = "draft"
    sent = "sent"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"


class StockTransactionType(enum.Enum):
    sale = "sale"
    damage = "damage"
    giveaway = "giveaway"
    adjustment = "adjustment"
    return_ = "return"


class ContactRole(enum.Enum):
    influencer = "influencer"
    reviewer = "reviewer"
    developer = "developer"
    retailer = "retailer"
    media = "media"
    other = "other"


class ConversationMedium(enum.Enum):
    email = "email"
    phone = "phone"
    discord = "discord"
    in_person = "in_person"
    other = "other"


class ConversationOutcome(enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    follow_up = "follow_up"
    closed = "closed"


class EventType(enum.Enum):
    convention = "convention"
    meetup = "meetup"
    demo = "demo"
    launch = "launch"
    deadline = "deadline"
    other = "other"


class ChatSessionStatus(enum.Enum):
    active = "active"
    waiting = "waiting"
    offline = "offline"
    closed = "closed"


# ── Customer ─────────────────────────────────────────────────────────

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    address_line1: Mapped[str] = mapped_column(String(200), nullable=False)
    address_line2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False, default="US")
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_stock: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
    )

    sales: Mapped[list["Sale"]] = relationship(back_populates="customer")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="customer")
    stock_checks: Mapped[list["BusinessStockCheck"]] = relationship(back_populates="customer")

    def __repr__(self) -> str:
        return f"<Customer {self.id} {self.business_name!r}>"


# ── Product ──────────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Product {self.sku} {self.name!r}>"


# ── Sale ─────────────────────────────────────────────────────────────

class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=True,
    )
    invoice_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("invoices.id"), nullable=True,
    )
    channel: Mapped[SaleChannel] = mapped_column(Enum(SaleChannel), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), nullable=False,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.completed,
    )
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tax: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sale_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    recorded_by: Mapped[str] = mapped_column(String(50), nullable=False)

    customer: Mapped[Customer | None] = relationship(back_populates="sales")
    invoice: Mapped["Invoice | None"] = relationship(
        back_populates="sales", foreign_keys=[invoice_id],
    )
    items: Mapped[list["SaleItem"]] = relationship(
        back_populates="sale", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Sale {self.id} ${self.total}>"


# ── SaleItem ─────────────────────────────────────────────────────────

class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales.id"), nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    sale: Mapped[Sale] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()

    def __repr__(self) -> str:
        return f"<SaleItem {self.quantity}x @ ${self.unit_price}>"


# ── CustomerSale ────────────────────────────────────────────────────

class CustomerSale(Base):
    __tablename__ = "customer_sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    channel: Mapped[SaleChannel] = mapped_column(Enum(SaleChannel), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), nullable=False,
    )
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sale_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    recorded_by: Mapped[str] = mapped_column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f"<CustomerSale C{self.id} ${self.total}>"


# ── Invoice ──────────────────────────────────────────────────────────

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False,
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False,
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.draft,
    )
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    tax: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    adjustments: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=0)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    payable_to: Mapped[str | None] = mapped_column(String(200), nullable=True)
    project_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    payment_terms: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Net 30",
    )
    issue_date: Mapped[date] = mapped_column(Date, default=date.today)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        Enum(PaymentMethod), nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[str] = mapped_column(String(50), nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="invoices")
    sales: Mapped[list[Sale]] = relationship(
        back_populates="invoice", foreign_keys=[Sale.invoice_id],
    )
    line_items: Mapped[list["InvoiceLineItem"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number} ${self.total}>"


# ── InvoiceLineItem ──────────────────────────────────────────────────

class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("invoices.id"), nullable=False,
    )
    product_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=True,
    )
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    invoice: Mapped[Invoice] = relationship(back_populates="line_items")
    product: Mapped[Product | None] = relationship()

    def __repr__(self) -> str:
        return f"<InvoiceLineItem {self.description!r} {self.quantity}x>"


# ── Box ─────────────────────────────────────────────────────────────

class Box(Base):
    __tablename__ = "boxes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    initial_count: Mapped[int] = mapped_column(Integer, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_open: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    recorded_by: Mapped[str] = mapped_column(String(50), nullable=False)

    transactions: Mapped[list["StockTransaction"]] = relationship(
        back_populates="box", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Box {self.id} {self.current_count}/{self.initial_count}>"


# ── StockTransaction ────────────────────────────────────────────────

class StockTransaction(Base):
    __tablename__ = "stock_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    box_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("boxes.id"), nullable=False,
    )
    transaction_type: Mapped[StockTransactionType] = mapped_column(
        Enum(StockTransactionType), nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    sale_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sales.id"), nullable=True,
    )
    customer_sale_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("customer_sales.id"), nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    box: Mapped[Box] = relationship(back_populates="transactions")

    def __repr__(self) -> str:
        return f"<StockTransaction {self.transaction_type.value} qty={self.quantity}>"


# ── Contact ─────────────────────────────────────────────────────────

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[ContactRole] = mapped_column(Enum(ContactRole), nullable=False)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Contact {self.id} {self.name!r}>"


# ── Conversation ────────────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contact_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contacts.id"), nullable=False,
    )
    conversation_date: Mapped[date] = mapped_column(Date, default=date.today)
    medium: Mapped[ConversationMedium] = mapped_column(
        Enum(ConversationMedium), nullable=False,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[ConversationOutcome] = mapped_column(
        Enum(ConversationOutcome), default=ConversationOutcome.neutral,
    )
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contact: Mapped[Contact] = relationship(back_populates="conversations")

    def __repr__(self) -> str:
        return f"<Conversation {self.id} {self.medium.value}>"


# ── Note ────────────────────────────────────────────────────────────

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<Note {self.id} {self.title!r}>"


# ── Event ───────────────────────────────────────────────────────────

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Event {self.id} {self.title!r}>"


# ── BusinessStockCheck ─────────────────────────────────────────────

class BusinessStockCheck(Base):
    __tablename__ = "business_stock_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False,
    )
    observed_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    adjusted_stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sale_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sales.id"), nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[str] = mapped_column(String(50), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    customer: Mapped[Customer] = relationship(back_populates="stock_checks")

    def __repr__(self) -> str:
        return f"<BusinessStockCheck {self.id} customer={self.customer_id} observed={self.observed_stock}>"


# ── ChatSession ────────────────────────────────────────────────────

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    discord_channel_id: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[ChatSessionStatus] = mapped_column(
        Enum(ChatSessionStatus), default=ChatSessionStatus.active,
    )
    visitor_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    staff_user_id: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ChatSession {self.session_id} {self.status.value}>"


# ── ChatMessage ────────────────────────────────────────────────────

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chat_sessions.id"), nullable=False,
    )
    sender_type: Mapped[str] = mapped_column(String(10), nullable=False)
    sender_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[ChatSession] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage {self.id} {self.sender_type}>"


# ── StaffCheckin ───────────────────────────────────────────────────

class StaffCheckin(Base):
    __tablename__ = "staff_checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discord_user_id: Mapped[str] = mapped_column(String(30), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    checked_in_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<StaffCheckin {self.display_name} expires={self.expires_at}>"
