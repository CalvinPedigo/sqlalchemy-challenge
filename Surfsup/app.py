# Import the dependencies.
import pandas as pd
import numpy as np
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime as dt


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:////Users\Owner\Desktop\DA Classwork\M10 sqlalchkjfa\SurfsUP\sqlalchemy-challenge\Resources\hawaii.sqlite", echo=False)
# reflect the tables
Base = automap_base()
Base.prepare(autoload_with= engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii weather API<br/>"
        f"Available Routes:<br/>"
        "/api/v1.0/precipitation <br/>"
        "/api/v1.0/stations <br/>"
        "/api/v1.0/tobs <br/>"
        "/api/v1.0/start (YYYY-MM-DD) (Oldest date: 2010-01-01, Newest date: 2017-08-23) <br/>"
        "/api/v1.0/start/end (YYYY-MM-DD) ((Oldest date: 2010-01-01, Newest date: 2017-08-23))<br/>"
    )

# route for precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    precip = session.query(measurement.date, measurement.prcp).filter(measurement.date >= "2016-08-23").all()
    precip_dict = {}
    for day in precip:
        precip_dict[day.date] = day.prcp
    return jsonify(precip_dict)

# route for list of stations
@app.route("/api/v1.0/stations")
def stations():
    list_stations = [stat.station for stat in session.query(station.station).all()]
    return jsonify(list_stations)

# route for temp data for the (most active) station USC00519281 in the previoius year
@app.route("/api/v1.0/tobs")
def tobs():
    year_active = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281')\
                    .filter(measurement.date >= "2016-08-23").all()
    tobs_d = {}
    for date, tobs in year_active:
        tobs_d[date] = tobs
    return jsonify(tobs_d)

# route for a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range.
@app.route("/api/v1.0/<start>")
def start(start):
    try:
        start_date = dt.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "use yyyy-mm-dd"}), 404
    usc81 = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    starting_vals = session.query(*usc81).filter(measurement.date >= start).all()
    starting_val_dict = {"avg:": starting_vals[0][2], "min:": starting_vals[0][0], "max:": starting_vals[0][1]}
    return jsonify(starting_val_dict)

# route for a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    try:
        start_date = dt.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "use yyyy-mm-dd"}), 404
    usc81 = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    startend_vals = session.query(*usc81).filter(measurement.date >= start).filter(measurement.date <= end).all()
    startend_val_dict = {"avg:": startend_vals[0][2], "min:": startend_vals[0][0], "max:": startend_vals[0][1]}
    return jsonify(startend_val_dict)
    
if __name__ == "__main__":
    app.run(debug=True)

