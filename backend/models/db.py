from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    
    
    tools: Mapped[list["DBTool"]] = relationship("DBTool", back_populates="owner")
    transactions: Mapped[list["DBTransaction"]] = relationship("DBTransaction", back_populates="user")

class DBTool(Base):
    __tablename__ = "tools"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    cost: Mapped[float] = mapped_column(Float)
    
    
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    url: Mapped[str] = mapped_column(String)
    
    
    owner: Mapped["DBUser"] = relationship("DBUser", back_populates="tools")
    transactions: Mapped[list["DBTransaction"]] = relationship("DBTransaction", back_populates="tool")

class DBTransaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    method: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    
    tool_id: Mapped[int] = mapped_column(Integer, ForeignKey("tools.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
    
    tool: Mapped["DBTool"] = relationship("DBTool", back_populates="transactions")
    user: Mapped["DBUser"] = relationship("DBUser", back_populates="transactions")