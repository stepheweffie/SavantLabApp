import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer
import pygame
import cv2
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()
Base = declarative_base()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)



class Recording():
    def __init__(self):
        self.drawing = []
        self.video = []
        self.webcam = []
        self.eyes = []



#pygame recreated drawing with pixels
class Recreate(Base):
    __tablename__ = 'lab_recordings'
    id = Column(Integer, primary_key=True)

    def __init__(self):
        pygame.init()
        self.screen =
        self.clock = pygame.time.Clock()
        self.recording = False
        self.drawing = []
        self.frames = []
        self.lab_datetime = db.Column(db.DateTime)
        self.lab_recording = db.Column(db.ARRAY, nullable=False, unique=True)

    def start_recreate(self):
        self.recording = True

    def stop_recreate(self):
        self.recording = False

    def recreate_frame(self):
        if self.recording:
            self.drawing = []
            frame = pygame.surfarray.array3d(self.screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.frames.append(frame)

        else:
            self.lab_datetime = datetime.datetime.now()
            self.lab_recording = self.frames
