import asyncio
from sqlalchemy import create_engine, select, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.engine import Result

Base = declarative_base()

class T(Base):
    __tablename__ = 't'
    id = Column(Integer, primary_key=True)
    val = Column(String)

def main():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(T(val='a'))
        session.commit()
        
        result = session.execute(select(T.val))
        print(f"Result type: {type(result)}")
        
        # This is the line in question
        scalars = result.scalars()
        print(f"Scalars type: {type(scalars)}")
        
        roles = scalars.all()
        print(f"Success: {roles}")

main()
