from sqlalchemy import Column, Integer, Text, String, Float, Numeric, Date, Time, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, CheckConstraint, DateTime, Interval, ARRAY, Enum
from sqlalchemy.orm import relationship
#from sqlalchemy.ext.hybrid import hybrid_property
#from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, TSTZRANGE
from datetime import datetime
from database import Base # Абсолютный импорт

class Airplane(Base):
    __tablename__ = 'airplanes_data'

    airplane_code = Column(String(3), primary_key=True) # Airplane code, IATA
    model = Column(JSONB, nullable=False)               # Airplane model
    range = Column(Integer, nullable=False)             # Maximum flight range, km
    speed = Column(Integer, nullable=False)             # Cruise speed, km/h

    # Relationships
    seats_info = relationship("Seat", back_populates="airplane")
    flights = relationship("Flight", back_populates="airplane")

class Airport(Base): # Airports (internal multilingual data)
    __tablename__ = 'airports_data'

    airport_code = Column(String(3), primary_key=True)  # Airport code, IATA
    airport_name = Column(JSONB, nullable=False)        # Airport name
    city = Column(JSONB, nullable=False)                # City
    country = Column(JSONB, nullable=False)             # Country
    coordinates = Column(String(50), nullable=False)    # Airport coordinates (longitude and latitude)
    timezone = Column(Text, nullable=False)             # Airport time zone

    # Relationships
    departure_flights = relationship("Flight", foreign_keys='Flight.departure_airport', back_populates="departure_airport_obj")
    arrival_flights = relationship("Flight", foreign_keys='Flight.arrival_airport', back_populates="arrival_airport_obj")
    routes_as_departure = relationship("Route", foreign_keys='Route.departure_airport', back_populates="departure_airport_obj")
    routes_as_arrival = relationship("Route", foreign_keys='Route.arrival_airport', back_populates="arrival_airport_obj")

class Flight(Base):
    __tablename__ = 'flights'

    flight_id = Column(Integer, primary_key=True)
    route_no = Column(Text, nullable=False) # Column(Integer, ForeignKey('routes.id'), nullable=False)
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

    route_no = Column(Text, primary_key=True)
    validity = Column(TSTZRANGE, nullable=False)    
    departure_airport = Column(String(3), ForeignKey('airports_data.iata_code'), nullable=False)
    arrival_airport = Column(String(3), ForeignKey('airports_data.iata_code'), nullable=False)
    airplane_code = Column(String(3), nullable=False)
    days_of_week = Column(ARRAY(Integer), nullable=False)
    scheduled_time = Column(Time, nullable=False)
    duration = Column(Interval, nullable=False)

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

    book_ref = Column(String(6), primary_key=True)
    book_date = Column(DateTime, timezone=True, nullable=False)
    total_amount = Column(Numeric(precision=10, scale=2), nullable=False)

    # Relationships
    tickets = relationship("Ticket", back_populates="booking")

class Ticket(Base):
    __tablename__ = 'tickets'

    ticket_no = Column(Text, primary_key=True)
    book_ref = Column(String(6), ForeignKey('bookings.book_ref'), nullable=False)
    passenger_id = Column(Text, nullable=False)
    passenger_name = Column(Text, nullable=False)
    outbound = Column(Boolean, nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="tickets")
    segments = relationship("Segment", back_populates="ticket")
    boarding_passes = relationship("BoardingPass", back_populates="ticket")

class Segment(Base):
    __tablename__ = 'segments'

    ticket_no = Column(Text, ForeignKey('tickets.ticket_no'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    fare_condition = Column(Text, nullable=False)
    price = Column(Numeric(precision=10, scale=2), nullable=False)

    # Relationships
    ticket = relationship("Ticket", back_populates="segments")
    flight = relationship("Flight", back_populates="segments")
    boarding_passes = relationship("BoardingPass", back_populates="segment")

class BoardingPass(Base):
    __tablename__ = 'boarding_passes'

    ticket_no = Column(Text, ForeignKey('tickets.ticket_no'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    seat_no = Column(Text, nullable=False)
    boarding_no = Column(Integer)
    boarding_time = Column(DateTime, timezone=True)

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

    airplane_code = Column(String(3), ForeignKey('airplanes_data.iata_code'), nullable=False)
    seat_no = Column(Text, nullable=False)
    fare_conditions = Column(Text, nullable=False)

    # Relationships
    airplane = relationship("Airplane", back_populates="seats_info")

    __table_args__ = (
        UniqueConstraint('airplane_iata_code', 'seat_no', name='unique_seat'),
    )
