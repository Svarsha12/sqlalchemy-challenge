# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import requests as request

from flask import Flask, jsonify, request



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

Base.classes.keys()

# Save references to each table

Station= Base.classes.station
measurement = Base.classes.measurement
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation:/api/v1.0/precipitation<br/>"
        f"Stations :/api/v1.0/stations<br/>"
        f"Temp for one year:/api/v1.0/tobs<br/>"
        f"Start date(yyyy/mm/dd):/api/v1.0/<start><br/>"
        f"Start date (yyyy/mm/dd) and end date (yyyy/mm/dd):/api/v1.0/<start>/<end><br/>"
    )
    
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    date_one_year_ago= dt.date(2017,8,23) - dt.timedelta(days=365)
    prcp_scores =session.query(measurement.date, measurement.prcp).filter(measurement.date > date_one_year_ago).\
        order_by(measurement.date).all()
    prcp_scores
    
    session.close()
    
    precipitation = []
    for date, prcp in prcp_scores:
        prcp_dict = {}
        prcp_dict['Date']= date
        prcp_dict['precipitation']= prcp
        precipitation.append(prcp_dict)
   
    #return result in json
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    station_query = [Station.station, Station.name,Station.latitude, Station.longitude, Station.elevation]
    query_station = session.query(*station_query).all()
    
    session.close()
    
    stations = []
    for station, name, latitude, longitude, elevation in query_station:
        station_dict = {}
        station_dict['Station'] = station
        station_dict['Name'] = name
        station_dict['Lat'] = latitude
        station_dict['Lon'] = longitude
        station_dict['Elevation'] = elevation
        stations.append(station_dict)
    
    # Return a JSON list of stations from the dataset
    return jsonify(stations)


@app.route("/api/v1.0/start", methods=['GET'])
def get_start_date():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Get the start date from the query parameters
    start = request.args.get('start')
    
    if start is None:
        return jsonify({'error': 'Start date parameter is missing'})
    
    # For a specified start, calculate min, avg, and max for all the dates greater than or equal to the start date
    start_date = session.query(measurement.station,
                                func.min(measurement.tobs),
                                func.max(measurement.tobs),
                                func.avg(measurement.tobs)).\
                            filter(measurement.date >= start).all()
    
    session.close()
    
    get_start_date = []
    for station, min_temp, max_temp, avg_temp in start_date:
        start_date_tobs_dict = {}
        start_date_tobs_dict['Station'] = station
        start_date_tobs_dict['Tmin'] = min_temp
        start_date_tobs_dict['Tmax'] = max_temp
        start_date_tobs_dict['Tavg'] = avg_temp
        get_start_date.append(start_date_tobs_dict)
        
    return jsonify(get_start_date)
# use this url http://localhost:5000/api/v1.0/start?start=2010-01-01


@app.route("/api/v1.0/<start>/<end>", methods=['GET'])
def get_start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    start_end_date = session.query(measurement.station,
                                   func.min(measurement.tobs),
                                   func.max(measurement.tobs),
                                   func.avg(measurement.tobs)).\
                      filter(measurement.date >= start).\
                      filter(measurement.date <= end).all()
    
    session.close()
    
    get_start_end_date = []
    for station, min_temp, max_temp, avg_temp in start_end_date:
        start_end_tobs_dict = {}
        start_end_tobs_dict['station'] = station
        start_end_tobs_dict['Tmin'] = min_temp
        start_end_tobs_dict['Tmax'] = max_temp
        start_end_tobs_dict['Tavg'] = avg_temp
        get_start_end_date.append(start_end_tobs_dict)
    
    return jsonify(get_start_end_date)

#use this url http://127.0.0.1:5000/api/v1.0/2010-01-01/2017-08-23     
        

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year ago from the last date in the database
    date_one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query to retrieve temperature observations for the last year
    sta_tobs = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date > date_one_year_ago).\
        order_by(measurement.date).all()
    
    session.close()
    
    tobs_all = []
    
    for date, tobs in sta_tobs:
        tobs_all_dict = {}
        tobs_all_dict['Date'] = date
        tobs_all_dict['Tobs'] = tobs
        tobs_all.append(tobs_all_dict)
    
    return jsonify(tobs_all)
        
        
        
if __name__ == '__main__':
    app.run(debug=True)