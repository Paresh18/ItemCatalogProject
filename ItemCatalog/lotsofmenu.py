from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base,Items, User

engine = create_engine('sqlite:///itemcatalog.db')
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


newUser=User(name="Rahul",email="rahul@gmail.com")
session.add(newUser)
session.commit()

Itemvalue=Items(name="Hockeyballs",category_id=9,user_id=1,description="There"+
"are great hockeyballs out there")
session.add(Itemvalue)
session.commit()

mySoccercategory=Category(name="Soccer")
session.add(mySoccercategory)
session.commit()


myBasketballcategory=Category(name="Basketball")
session.add(myBasketballcategory)
session.commit()


myBaseballcategory=Category(name="Baseball")
session.add(myBaseballcategory)
session.commit()


myFrisbeecategory=Category(name="Frisbee")
session.add(myFrisbeecategory)
session.commit()


mySnowboardingcategory=Category(name="Snowboarding")
session.add(mySnowboardingcategory)
session.commit()



myRockclimbingcategory=Category(name="Rockclimbing")
session.add(myRockclimbingcategory)
session.commit()


myFossballcategory=Category(name="Fossball")
session.add(myFossballcategory)
session.commit()


mySkatingcategory=Category(name="Skating")
session.add(mySkatingcategory)
session.commit()


myHockeycategory=Category(name="Hockey")
session.add(myHockeycategory)
session.commit()