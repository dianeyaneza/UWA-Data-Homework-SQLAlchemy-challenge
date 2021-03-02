import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
# Base = automap_base()
# # reflect the tables
# Base.prepare(engine, reflect=True)

Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# create session
session = Session(engine)

app = Flask(__name__)


## 1. Home page.
# List all routes that are available.
@app.route("/")
def home():
    return (
        f"Welcome to the Surfs Up Weather API!<br/>"
        f"Add the following available routes to the address on the address bar to view the following:<br/>"
        f"PRECIPITATION: /api/v1.0/precipitation<br/>"
        f"AVAILABLE STATIONS: /api/v1.0/stations<br/>"
		f"TEMPERATURE OBSERVATIONS: /api/v1.0/tobs<br/>"
		f"YOUR START DATE'S MIN, AVE, MAX TEMPERATURE (F): /api/v1.0/(YYYY-MM-DD)<br/>"
        f"YOUR START AND END DATE'S MIN, AVE, MAX TEMPERATURE (F): /api/v1.0/(YYYY-MM-DD/YYYY-MM-DD)"
    )


## 2. Precipitation
# Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session 
    session = Session(engine)
    # Query precipitation by date
    results = session.query(Measurement.prcp, Measurement.date).order_by(Measurement.date.desc()).all()
    # Place the results into a dictionary
    precipitation_data = []
    for result in results:
        dt_dict = {}
        dt_dict["date"] = result.date
        dt_dict["prcp"] = result.prcp
        precipitation_data.append(dt_dict)
    # Return the JSON dictionary
    return jsonify(precipitation_data)


## 3. Stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create session
    session = Session(engine)
    # Query Stations
    results = session.query(Station.station, Station.name).all()
    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))
	# Return json results
    return jsonify(stations_list)


## 4. TOBS
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs") 
def tobs():
    # Create session 
    session = Session(engine)
    # First, view all the stations total number of tobs
    tobs_recorded = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    # Choose the station with the highest number of temperature observations.
    highest_tobs = tobs_recorded[0][0]
    # Query the last 12 months of temperature observation data for this station
    htobs_last12 = dt.datetime(2016, 8, 18)
    results = session.query(Measurement.date, Measurement.station, Measurement.tobs).order_by(Measurement.date.desc()).filter(Measurement.station == highest_tobs).filter(Measurement.date > htobs_last12).all()
    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(results))
    # Return json results
    return jsonify(tobs_list)


## 5. Start Date
# When given the start only, calculate temp_min, temp_avg, and temp_max for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>") 
def start_only(start_date):
    # Create session 
    session = Session(engine)
    # Query rhe min, ave, max temps for the date greater than and equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    # Convert list of tuples into normal list
    start_list = list(np.ravel(results))
    # Return json results
    return jsonify(start_list)


## 6. Start and End Date
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>") 
def start_end(start, end):
    # Create session 
    session = Session(engine)
    # Query rhe min, ave, max temps for the date greater than and equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    # Convert list of tuples into normal list
    start_end_list = list(np.ravel(results))
    # Return json results
    return jsonify(start_end_list)


if __name__ == '__main__':
    app.run(debug=True)