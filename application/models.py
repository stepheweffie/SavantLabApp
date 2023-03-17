from flask_sqlalchemy import SQLAlchemy
import pygame
import cv2
db = SQLAlchemy()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    date_sold = db.Column(db.String(), nullable=False)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)


class Recording():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.WINDOWEXPOSED)
        self.clock = pygame.time.Clock()
        self.recording = False
        self.frames = []

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


