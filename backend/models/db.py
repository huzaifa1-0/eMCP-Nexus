from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from sqlalchemy import JSON
from typing import List,Optional


Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    api_key: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    
    tools: Mapped[list["DBTool"]] = relationship("DBTool", back_populates="owner")
    transactions: Mapped[list["DBTransaction"]] = relationship("DBTransaction", back_populates="user")
    ratings: Mapped[list["DBRating"]] = relationship("DBRating", back_populates="user")
    subscriptions: Mapped[List["DBSubscription"]] = relationship("DBSubscription", back_populates="user")

class DBTool(Base):
    __tablename__ = "tools"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    cost: Mapped[float] = mapped_column(Float)
    repo_url: Mapped[str] = mapped_column(String)  # Corrected typo from rep_url
    branch: Mapped[str] = mapped_column(String, default="main")
    build_command: Mapped[str] = mapped_column(String, default="npm install && npm run build")
    start_command: Mapped[str] = mapped_column(String, default="npm start")
    root_dir: Mapped[str] = mapped_column(String, default="", nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id")) # Corrected to Integer
    url: Mapped[str] = mapped_column(String)
    tool_definitions: Mapped[dict] = mapped_column(JSON, nullable=True)
    deploy_id: Mapped[str] = mapped_column(String, nullable=True)
    subscriptions: Mapped[List["DBSubscription"]] = relationship("DBSubscription", back_populates="tool")
    
    owner: Mapped["DBUser"] = relationship("DBUser", back_populates="tools")
    transactions: Mapped[list["DBTransaction"]] = relationship("DBTransaction", back_populates="tool")
    ratings: Mapped[list["DBRating"]] = relationship("DBRating", back_populates="tool")
    @property
    def author_tools_count(self) -> int:
        return len(self.owner.tools) if self.owner else 0

    @property
    def author(self) -> str:
        return self.owner.username if self.owner else "Unknown"

    @property
    def reviews(self) -> list:
        return [
            {
                "user": r.user.username if r.user else "Anonymous",
                "rating": r.rating,
                "comment": r.comment,
                "timestamp": r.timestamp
            } for r in self.ratings
        ]

    status: Mapped[str] = mapped_column(String, default="deploying")

class DBTransaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    method: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    tool_id: Mapped[int] = mapped_column(Integer, ForeignKey("tools.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
    tool: Mapped["DBTool"] = relationship("DBTool", back_populates="transactions")
    user: Mapped["DBUser"] = relationship("DBUser", back_populates="transactions")

class DBRating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        CheckConstraint('rating >= 0 AND rating <= 5', name='rating_range'),
        UniqueConstraint('tool_id', 'user_id', name='unique_tool_user_rating'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tool_id: Mapped[int] = mapped_column(Integer, ForeignKey("tools.id")) # Corrected to Integer
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id")) # Corrected to Integer

    tool: Mapped["DBTool"] = relationship(back_populates="ratings")
    user: Mapped["DBUser"] = relationship(back_populates="ratings")

class DBUsageLog(Base):
    __tablename__ = "usage_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tool_id: Mapped[int] = mapped_column(Integer, ForeignKey("tools.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    success: Mapped[bool] = mapped_column(default=True)
    processing_time: Mapped[float] = mapped_column(Float)

    tool: Mapped["DBTool"] = relationship()
    user: Mapped["DBUser"] = relationship()

class DBSubscription(Base):
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    tool_id: Mapped[int] = mapped_column(Integer, ForeignKey("tools.id"))
    stripe_session_id: Mapped[str] = mapped_column(String, nullable=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String, nullable=True)
    plan: Mapped[str] = mapped_column(String)  # weekly, monthly, yearly
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, active, cancelled
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["DBUser"] = relationship("DBUser", back_populates="subscriptions")
    tool: Mapped["DBTool"] = relationship("DBTool", back_populates="subscriptions")