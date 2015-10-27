#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import City, Base, Event, User
from datetime import datetime, date
 
engine = create_engine('sqlite:///androidevents.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Check existing db content
allUsers = session.query(User.name).all()
print allUsers

allCityNames = session.query(City.name).all()
print allCityNames

allEventNames = session.query(Event.city_id).all()
print allEventNames

# Drop tables in case columns have changed during development  
# Base.metadata.drop_all(engine)

# Confirm table columns
# print Event.__table__.columns.keys()

# Clear database tables - City, Event, User
session.query(User).delete()
session.query(City).delete()
session.query(Event).delete()
session.commit()


# Create initial user for adding data
User1 = User(name="TW", email="plwhetzel@gmail.com",
             picture='https://lh6.googleusercontent.com/-VnxWuzSW494/UEiyeA06zoI/AAAAAAAAWtU/LOxkmbmhFV8/w461-h460/photo-7c.png')
session.add(User1)
session.commit()
print User1.name


# City info for San Francisco
city1 = City(user_id=1, name = "San Francisco", state="California")
session.add(city1)
session.commit()


event1 = Event(user_id=1, name = "Droidcon San Francisco 2016", 
	description = "The droidcon conferences around the world support the \
	Android platform and create a global network for developers and \
	companies. We offer best-in-class presentations from leaders in all \
	parts of the Android ecosystem, including core development, embedded \
	solutions augmented reality, business solutions and games.", 
	city = city1, 
	event_date=date(2016, 3, 17), 
	event_url="http://sf.droidcon.com/", 
	image_url="https://embed.gyazo.com/11e1eaa28bf28afaa3a1f235b5f985e6.png")
session.add(event1)
session.commit()


event2 = Event(user_id=1, name = "SF Android User Group", 
	description = "We are an interactive group of Android developers and \
	contractors discussing trends in technology, business, and job outlook.", 
	city = city1, 
	event_date=date(2015, 10, 27), 
	event_url='http://www.meetup.com/sfandroid/', 
	image_url="http://img2.meetupstatic.com/img/8308650022681532654/header/logo-2x.png")
session.add(event2)
session.commit()


event3 = Event(user_id=1, name = "Advanced Android Espresso", 
	description = "Espresso is a very powerful UI testing framework. Attend \
	this meetup to learn the following techniques to get the most out of it.", 
	city = city1, 
	event_date=date(2015, 11, 30), 
	event_url='http://www.meetup.com/bayareaandroid/events/226197227/', 
	image_url="http://img2.meetupstatic.com/img/8308650022681532654/header/logo-2x.png")
session.add(event3)
session.commit()


event4 = Event(user_id=1, name = "Persistent Queues with Tape", 
	description = "Processing background tasks in Android apps can be tricky. \
	You need to think about cases such as low memory situations, running \
	out of battery and flaky networks. Persisting tasks to disk helps you \
	reliably handle such edge cases. Enter Tape, a collection of queue \
	related classes. This talk will be primarily about it''s core component, \
	QueueFile a lightning fast, transactional, persistent file-based FIFO. \
	For new users, we''ll compare it to alternatives and dig into it''s API \
	with real world examples. For veterans, we''ll take a deep dive into it's \
	technical implementation and see how it guarantees both reliability and \
	efficiency.", 
	city = city1, 
	event_date=date(2015, 10, 27), 
	event_url='http://www.meetup.com/sfandroid/events/226198822/', 
	image_url="http://img2.meetupstatic.com/img/8308650022681532654/header/logo-2x.png")
session.add(event4)
session.commit()


event5 = Event(user_id=1, name = "Android Development Like a Pro", 
	description = "The Android SDK has changed much since its first version. \
	Every new version comes with many new APIs. However, there is no perfect \
	API, some do too much under the hood, others couple your classes to the \
	context, others have more lifecycle events than you have years in your \
	life. The talk will show how to make your app scalable, your code clean, \
	your performance optimized and your UI neat. The talk will show in a \
	pragmatic way the pros and cons of using certain Android APIs, strategies \
	and libraries. It will touch on Fragments, Loaders, AsyncTasks, OOP \
	patterns (mvp vs mvvm vs viper) and styling. This talk is a compendium of \
	my experience in large code bases since I started to work in Android in \
	2009.", 
	city = city1, 
	event_date=date(2015, 9, 29), 
	event_url='http://www.meetup.com/sfandroid/events/224952292/', 
	image_url="http://img2.meetupstatic.com/img/8308650022681532654/header/logo-2x.png")
session.add(event5)
session.commit()


event6 = Event(user_id=1, name = "Android Speech Recognition APIs", 
	description = "This class will provide an overview of the current state \
	of the art regarding voice recognition for Android, the most popular \
	APIs, their limitations and special features. After the introduction, \
	there will be a coding tutorial using code samples. You will be able to \
	follow the instructor to implement together a working voice recognition \
	application. The focus will be on voice commands as opposed to dictation.", 
	city = city1, 
	event_date=date(2015, 8, 11), 
	event_url='http://www.meetup.com/sfandroid/events/224952292/', 
	image_url="http://img2.meetupstatic.com/img/8308650022681532654/header/logo-2x.png")
session.add(event6)
session.commit()



# City info for New York
city2 = City(name = "New York", state="New York", user_id=1)
session.add(city2)
session.commit()


event1 = Event(user_id=1, name = "Droidcon New York 2015", 
	description = "The Droidcon conferences around the world support the \
	Android platform and create a global network for developers and \
	companies. We offer best-in-class presentations from leaders in all \
	parts of the Android ecosystem, including core development, embedded \
	solutions augmented reality, business solutions and games.", 
	city = city2, 
	event_date=date(2015, 8, 27), 
	event_url='http://droidcon.nyc/2015/', 
	image_url="http://i28.photobucket.com/albums/c218/TanyaKarsou/EBHeader_960x350FNL_zpshqud9wxt.png")
session.add(event1)
session.commit()


# City info for Dallas
city3 = City(name = "Dallas", state="Texas", user_id=1)
session.add(city3)
session.commit()

event1 = Event(user_id=1, name = "Big Android BBQ", 
	description = "The Droidcon conferences around the world support the \
	Android platform and create a global network for developers and \
	companies. We offer best-in-class presentations from leaders in all \
	parts of the Android ecosystem, including core development, embedded \
	solutions augmented reality, business solutions and games.", 
	city = city3, 
	event_date=date(2015, 10, 22), 
	event_url='http://www.bigandroidbbq.com/index.html', 
	image_url="http://www.bigandroidbbq.com/images/babbq15_logo.svg")
session.add(event1)
session.commit()



# Debug statements to confirm data entry
print "Added cities and events and users!"
allEvents = session.query(Event).join(Event.city).order_by(City.name, Event.name).all()
print allEvents[0].user_id, allEvents[0].event_date



