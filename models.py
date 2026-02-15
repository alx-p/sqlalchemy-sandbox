from sqlalchemy import Column, Integer, String, Float, Date, Time, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, CheckConstraint, DateTime, Interval, ARRAY, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from datetime import datetime
from database import Base # Абсолютный импорт

class Airplane(Base):
    __tablename__ = 'airplanes_data'

    airplane_code = Column(String(3), primary_key=True) # Airplane code, IATA
    model = Column(String(50), nullable=False) # Airplane model
    range = Column(Integer, nullable=False) # Maximum flight range, km
    speed = Column(Integer, nullable=False) # Cruise speed, km/h

    # Relationships
    seats_info = relationship("Seat", back_populates="airplane")
    flights = relationship("Flight", back_populates="airplane")

class Airport(Base): # Airports (internal multilingual data)
    __tablename__ = 'airports_data'

    airport_code = Column(String(3), primary_key=True)
    airport_name = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    coordinates = Column(String(50), nullable=False)
    timezone = Column(String(50), nullable=False)

    # Relationships
    departure_flights = relationship("Flight", foreign_keys='Flight.departure_airport', back_populates="departure_airport_obj")
    arrival_flights = relationship("Flight", foreign_keys='Flight.arrival_airport', back_populates="arrival_airport_obj")
    routes_as_departure = relationship("Route", foreign_keys='Route.departure_airport', back_populates="departure_airport_obj")
    routes_as_arrival = relationship("Route", foreign_keys='Route.arrival_airport', back_populates="arrival_airport_obj")

class Flight(Base):
    __tablename__ = 'flights'

    flight_id = Column(Integer, primary_key=True)
    route_no = Column(String(50), nullable=False) # Column(Integer, ForeignKey('routes.id'), nullable=False)
    status = Column(Enum('scheduled', 'delayed', 'cancelled', 'completed', name='flight_status'), default='scheduled')
    scheduled_departure = Column(DateTime, timezone=True, nullable=False)
    scheduled_arrival = Column(DateTime, timezone=True, nullable=False)
    actual_departure = Column(DateTime, timezone=True)
    actual_arrival = Column(DateTime, timezone=True)

    # Relationships
    route = relationship("Route", back_populates="flights")
    airplane = relationship("Airplane", back_populates="flights")
    departure_airport = Column(String(3), ForeignKey('airports_data.iata_code'))
    departure_airport_obj = relationship("Airport", foreign_keys=[departure_airport], back_populates="departure_flights")
    arrival_airport = Column(String(3), ForeignKey('airports_data.iata_code'))
    arrival_airport_obj = relationship("Airport", foreign_keys=[arrival_airport], back_populates="arrival_flights")
    segments = relationship("Segment", back_populates="flight")
    boarding_passes = relationship("BoardingPass", back_populates="flight")

class Route(Base):
    __tablename__ = 'routes'

    route_no = Column(Integer, primary_key=True)
    departure_airport = Column(String(3), ForeignKey('airports_data.iata_code'), nullable=False)
    arrival_airport = Column(String(3), ForeignKey('airports_data.iata_code'), nullable=False)
    validity_period = Column(Interval, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    departure_airport_obj = relationship("Airport", foreign_keys=[departure_airport], back_populates="routes_as_departure")
    arrival_airport_obj = relationship("Airport", foreign_keys=[arrival_airport], back_populates="routes_as_arrival")
    flights = relationship("Flight", back_populates="route")

    __table_args__ = (
        UniqueConstraint('departure_airport', 'arrival_airport', 'validity_period', name='unique_route_validity'),
        CheckConstraint("validity_period[1] - validity_period[0] > interval '0 days'", name='validity_period_duration'),
    )

class Booking(Base):
    __tablename__ = 'bookings'

    booking_ref = Column(String(6), primary_key=True)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    tickets = relationship("Ticket", back_populates="booking")

class Ticket(Base):
    __tablename__ = 'tickets'

    ticket_no = Column(String(13), primary_key=True)
    booking_ref = Column(String(6), ForeignKey('bookings.booking_ref'), nullable=False)
    passenger_name = Column(String(100), nullable=False)
    passenger_doc = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    booking = relationship("Booking", back_populates="tickets")
    segments = relationship("Segment", back_populates="ticket")
    boarding_passes = relationship("BoardingPass", back_populates="ticket")

class Segment(Base):
    __tablename__ = 'segments'

    id = Column(Integer, primary_key=True)
    ticket_no = Column(String(13), ForeignKey('tickets.ticket_no'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    fare_condition = Column(Enum('economy', 'business', 'first', name='fare_condition'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="segments")
    flight = relationship("Flight", back_populates="segments")
    boarding_passes = relationship("BoardingPass", back_populates="segment")

class BoardingPass(Base):
    __tablename__ = 'boarding_passes'

    id = Column(Integer, primary_key=True)
    ticket_no = Column(String(13), ForeignKey('tickets.ticket_no'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    boarding_no = Column(Integer)
    seat_no = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="boarding_passes")
    flight = relationship("Flight", back_populates="boarding_passes")
    segment = relationship("Segment", back_populates="boarding_passes")

    __table_args__ = (
        UniqueConstraint('flight_id', 'boarding_no', name='unique_boarding_pass_boarding_no'),
        UniqueConstraint('flight_id', 'seat_no', name='unique_boarding_pass_seat_no'),
    )

class Seat(Base):
    __tablename__ = 'seats'

    id = Column(Integer, primary_key=True)
    airplane_iata_code = Column(String(3), ForeignKey('airplanes_data.iata_code'), nullable=False)
    seat_no = Column(String(10), nullable=False)
    fare_condition = Column(Enum('economy', 'business', 'first', name='fare_condition'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    airplane = relationship("Airplane", back_populates="seats_info")

    __table_args__ = (
        UniqueConstraint('airplane_iata_code', 'seat_no', name='unique_seat'),
    )
