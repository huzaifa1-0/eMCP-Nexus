from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base



Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    
    
    tools: Mapped[list["DBTool"]] = relationship("DBTool", back_populates="owner")
    transactions: Mapped[list["DBTransaction"]] = relationship("DBTransaction", back_populates="user")

    ratings: Mapped[list["DBRating"]] = relationship("DBRating", back_populates="user")

class DBTool(Base):
    __tablename__ = "tools"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    cost: Mapped[float] = mapped_column(Float)

    rep_url: Mapped[str] = mapped_column(String)
    branch: Mapped[str] = mapped_column(String, default="main")
    
    
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    url: Mapped[str] = mapped_column(String)
    
    
    owner: Mapped["DBUser"] = relationship("DBUser", back_populates="tools")
    transactions: Mapped[list["DBTransaction"]] = relationship("DBTransaction", back_populates="tool")

    ratings: Mapped[list["DBRating"]] = relationship("DBRating", back_populates="tool")
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
    """Database model for a Rating."""
    __tablename__ = "ratings"
    __table_args__ = (
        CheckConstraint('rating >= 0 AND rating <= 5', name='rating_range'),
        UniqueConstraint('tool_id', 'user_id', name='unique_tool_user_rating'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rating: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

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
    