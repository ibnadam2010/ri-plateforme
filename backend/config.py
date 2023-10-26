from decouple import config
import os

#file current path
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

#Global config class
class Config:
    SECRET_KEY=config('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS=config('SQLALCHEMY_TRACK_MODIFICATIONS', cast=bool)  

#Development config
class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI="sqlite:///"+os.path.join(BASE_DIR,'bdd.db')  
    DEBUG=True
    SQLACHEMY_ECHO=True 

class prodConfig(Config):
    pass    

class testConfig(Config):
    SQLALCHEMY_DATABASE_URI="sqlite:///"+os.path.join(BASE_DIR,'test.db')  
    SQLACHEMY_ECHO=False
    TESTING:True