import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer
import pygame
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
import redis

redis_host = 'localhost'
redis_port = 6379
redis_db = 0
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

db = SQLAlchemy()
Base = declarative_base()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Drawing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    video_path = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Drawing {self.title}>"


class MouseData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movements = db.Column(db.Text, nullable=False)
    drawing = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return f'<MouseData {self.id}>'


class Recording():
    def __init__(self):
        self.video = []
        self.frames = []

    def start_recording(self):
        pass


class Recreate(Base):
    __tablename__ = 'lab_recreations'
    id = Column(Integer, primary_key=True)

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Recreating Drawing')
        self.surface = pygame.Surface((canvas_width, canvas_height))
        self.clock = pygame.time.Clock()
        self.recording = False
        self.drawing = []
        self.frames = []
        self.pixel_data = r.get('drawing_data')
        self.lab_datetime = db.Column(db.DateTime)
        self.lab_recording = db.Column(db.ARRAY, nullable=False, unique=True)

    def start_recreate(self):
        self.drawing = [self.pixel_data]

    def stop_recreate(self):
        self.drawing = False
        self.recording = False

    def recreate_frame(self):
        if self.start_recreate():
            # Draw the pixels in the order they were drawn
            for i in range(len(self.pixel_data)):
                x = self.pixel_data[i]
                y = self.pixel_data[i + 1]
                r = self.pixel_data[i + 2]
                g = self.pixel_data[i + 3]
                b = self.pixel_data[i + 4]
                pygame.draw.rect(self.surface, (r, g, b), (x, y, 1, 1))
                pygame.display.update()
                # Wait for a short period of time to create a drawing effect
                pygame.time.wait(10)

            # Run the Pygame loop
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

            pygame.quit()
        else:
            self.lab_recording = self.drawing
