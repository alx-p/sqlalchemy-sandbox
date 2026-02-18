from sqlalchemy import Column, Integer, Text, String, Float, Numeric, Date, 
Time, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, CheckConstraint, 
DateTime, Interval, ARRAY, Enum, UniqueConstraint, Sequence
from sqlalchemy.orm import relationship
#from sqlalchemy.ext.hybrid import hybrid_property
#from sqlalchemy.sql import func
from sqlalchemy.sql.expression import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, TSTZRANGE, ExcludeConstraint
from sqlalchemy.schema import PrimaryKeyConstraint, CheckConstraint
from datetime import datetime
from database import Base # Абсолютный импорт
from geoalchemy2 import Geometry

class Airplane(Base):
    __tablename__ = 'airplanes_data'
    __table_args__ = {
        'comment': 'Airplanes (internal multilingual data)',
        'schema': 'bookings',
        'constraints': (
            PrimaryKeyConstraint('airplane_code', name='airplanes_data_pkey'),
            CheckConstraint('range > 0', name='airplanes_data_range_check'),
            CheckConstraint('speed > 0', name='airplanes_data_speed_check'),
        )
    }

    airplane_code = Column(String(3), comment='Airplane code, IATA')
    model = Column(JSONB, nullable=False, comment='Airplane model')
    range = Column(Integer, nullable=False, comment='Maximum flight range, km')
    speed = Column(Integer, nullable=False, comment='Cruise speed, km/h')

class Airport(Base): # Airports (internal multilingual data)
    __tablename__ = 'airports_data'
    __table_args__ = {
        'comment': 'Airports (internal multilingual data)',
        'schema': 'bookings',
        'constraints': (
            PrimaryKeyConstraint('airport_code', name='airports_data_pkey'),
        )
    }

    airport_code = Column(String(3), primary_key=True, comment='Airport code, IATA')
    airport_name = Column(JSONB, nullable=False, comment='Airport name')
    city = Column(JSONB, nullable=False, comment='City')
    country = Column(JSONB, nullable=False, comment='Country')
    coordinates = Column(Geometry(geometry_type='POINT'), nullable=False, comment='Airport coordinates (longitude and latitude)')
    timezone = Column(Text, nullable=False, comment='Airport time zone')

class Flight(Base):
    __tablename__ = 'flights'

    flight_id = Column(Integer, Sequence('flight_id_seq', start=1, increment=1), comment='Flight ID')
    route_no = Column(Text, nullable=False, comment='Route number')
    status = Column(Text, nullable=False, comment='Flight status')
    scheduled_departure = Column(DateTime, timezone=True, nullable=False), comment='Scheduled departure time'
    scheduled_arrival = Column(DateTime, timezone=True, nullable=False, comment='Scheduled arrival time')
    actual_departure = Column(DateTime, timezone=True, comment='Actual departure time')
    actual_arrival = Column(DateTime, timezone=True, comment='Actual arrival time')

    __table_args__ = {
        'comment': 'Flights',
        'schema': 'bookings',
        'constraints': (
            PrimaryKeyConstraint('flight_id', name='flights_pkey'),
            UniqueConstraint(route_no, scheduled_departure, name='flights_route_no_scheduled_departure_key'),
            CheckConstraint('((actual_arrival IS NULL) OR ((actual_departure IS NOT NULL) AND (actual_arrival IS NOT NULL) AND (actual_arrival > actual_departure)))', name='flight_actual_check'),
            CheckConstraint('scheduled_arrival > scheduled_departure', name='flight_scheduled_check'),
            CheckConstraint('status = ANY (ARRAY[''Scheduled''::text, ''On Time''::text, ''Delayed''::text, ''Boarding''::text, ''Departed''::text, ''Arrived''::text, ''Cancelled''::text])', name='flight_status_check'),
        )
    }

class Route(Base):
    __tablename__ = 'routes'

    route_no = Column(Text, nullable=False, comment='Route number')
    validity = Column(TSTZRANGE, nullable=False, comment='Period of validity')    
    departure_airport = Column(String(3), nullable=False, comment='Airport of departure') # ForeignKey('airports_data.iata_code'), 
    arrival_airport = Column(String(3), nullable=False, comment='Airport of arrival') # ForeignKey('airports_data.iata_code'), 
    airplane_code = Column(String(3), nullable=False, comment='Airplane code, IATA')
    days_of_week = Column(ARRAY(Integer), nullable=False, comment='Days of week array')
    scheduled_time = Column(Time, nullable=False, comment='Scheduled local time of departure')
    duration = Column(Interval, nullable=False, comment='Estimated duration')

    __table_args__ = {
        'comment': 'Routes',
        'schema': 'bookings',
        'constraints': (
            ExcludeConstraint(
                ('route_id', '='),
                ('validity', '&&'),
                name='routes_route_no_validity_excl'
            ),
            Index('routes_departure_airport_lower_idx', departure_airport, func.lower(validity)),
            ForeignKeyConstraint(['airplane_code'], ['bookings.airplanes_data.airplane_code'], name="routes_airplane_code_fkey"),
            ForeignKeyConstraint(['arrival_airport'], ['bookings.airports_data.airport_code'], name="routes_arrival_airport_fkey"),
            ForeignKeyConstraint(['departure_airport'], ['bookings.airports_data.airport_code'], name="routes_departure_airport_fkey"),
        )
    }

class Booking(Base):
    __tablename__ = 'bookings'

    book_ref = Column(String(6), comment='Booking number')
    book_date = Column(DateTime, timezone=True, nullable=False, comment='Booking date')
    total_amount = Column(Numeric(precision=10, scale=2), nullable=False, comment='Total booking amount')

    __table_args__ = {
        'comment': 'Bookings',
        'schema': 'bookings',
        'constraints': (
            PrimaryKeyConstraint('book_ref', name='bookings_pkey'),
        )
    }

class Ticket(Base):
    __tablename__ = 'tickets'
    
    ticket_no = Column(Text, nullable=False, comment='Ticket number')
    book_ref = Column(String(6), nullable=False, comment='Booking number')
    passenger_id = Column(Text, nullable=False, comment='Passenger ID')
    passenger_name = Column(Text, nullable=False, comment='Passenger name')
    outbound = Column(Boolean, nullable=False, comment='Outbound flight?')

    __table_args__ = {
        'comment': 'Tickets',
        'schema': 'bookings',
        'constraints': (
            PrimaryKeyConstraint('ticket_no', name='tickets_pkey'),
            ForeignKeyConstraint(['book_ref'], ['bookings.bookings.book_ref'], name="tickets_book_ref_fkey"),
        )
    }

class Segment(Base):
    __tablename__ = 'segments'

    ticket_no = Column(Text, nullable=False)
    flight_id = Column(Integer, nullable=False)
    fare_condition = Column(Text, nullable=False)
    price = Column(Numeric(precision=10, scale=2), nullable=False)

    __table_args__ = {
        'comment': 'Flight segment (leg)',
        'schema': 'bookings',
        'constraints': (
            PrimaryKeyConstraint('ticket_no', 'flight_id', name='segments_pkey'),
            #ForeignKeyConstraint(['book_ref'], ['bookings.bookings.book_ref'], name="tickets_book_ref_fkey"),
        )
    }

class BoardingPass(Base):
    __tablename__ = 'boarding_passes'

    ticket_no = Column(Text, nullable=False)
    flight_id = Column(Integer, nullable=False)
    seat_no = Column(Text, nullable=False)
    boarding_no = Column(Integer)
    boarding_time = Column(DateTime, timezone=True)

    __table_args__ = {
        'comment': 'Boarding passes',
        'schema': 'bookings',
        'constraints': (
            PrimaryKeyConstraint('ticket_no', 'flight_id', name='boarding_passes_pkey'),
            # UniqueConstraint('flight_id', 'boarding_no', name='unique_boarding_pass_boarding_no'),
            # UniqueConstraint('flight_id', 'seat_no', name='unique_boarding_pass_seat_no'),
        )
    )

class Seat(Base):
    __tablename__ = 'seats'

    airplane_code = Column(String(3), nullable=False)
    seat_no = Column(Text, nullable=False)
    fare_conditions = Column(Text, nullable=False)

    __table_args__ = {
        'comment': 'Seats',
        'schema': 'bookings',
        'constraints': (
            PrimaryKeyConstraint('airplane_code', 'seat_no', name='seats_pkey'),
            # UniqueConstraint('flight_id', 'boarding_no', name='unique_boarding_pass_boarding_no'),
            # UniqueConstraint('flight_id', 'seat_no', name='unique_boarding_pass_seat_no'),
        )
    )
