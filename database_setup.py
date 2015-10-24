from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'

  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  email = Column(String(250), nullable=False)
  picture = Column(String(250))

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      'id' :self.id,
      'name'  : self.name,
      'email' : self.email,
      'picture' : self.picture,
    }


class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    state = Column(String(100), nullable=False)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
    events = relationship("Event", cascade="all, delete-orphan")
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
          'id': self.id,
          'name': self.name,
          'state': self.state,
          'user_id': self.user_id,
          'event': [e.serialize for e in self.events]
        }

 
class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    description = Column(String(250))
    #image_url = Column(String(250))
    city_id = Column(Integer,ForeignKey('city.id'))
    #city = relationship(City)
    city = relationship("City", backref=backref("city", cascade="all, delete-orphan"))
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'id': self.id,
           'name': self.name,
           'description': self.description,
           'user_id': self.user_id   
        }


engine = create_engine('sqlite:///androidevents.db', echo=True)
 

Base.metadata.create_all(engine)
