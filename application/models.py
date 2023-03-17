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


class Recording(Base):
    __tablename__ = 'lab_recordings'
    id = Column(Integer, primary_key=True)
    # TODO number the labs

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.WINDOWEXPOSED)
        self.clock = pygame.time.Clock()
        self.recording = False
        self.frames = []
        self.lab_datetime = db.Column(db.DateTime)
        self.lab_recording = db.Column(db.ARRAY, nullable=False, unique=True)

    def start_recording(self):
        self.recording = True

    def stop_recording(self):
        self.recording = False

    def record_frame(self):
        if self.recording:
            self.clock.tick(30)
            frame = pygame.surfarray.array3d(self.screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.frames.append(frame)

        else:
            self.lab_datetime = datetime.datetime.now()
            self.lab_recording = self.frames
