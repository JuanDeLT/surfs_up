#import dependencies
import datetime as dt
import numpy as np
import pandas as pd
#import dependencies for SQLalchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#import dependencies for flask
from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite", connect_args={"check_same_thread": False}) #this allows us to access the sqlite database
Base = automap_base() #reflect the database into our classes
Base.prepare(engine, reflect=True)

#with the database reflected, we can save our references to each table.
Measurement = Base.classes.measurement
Station = Base.classes.station

#create a sesion link from python to our database
session = Session(engine)

#SET UP FLASK

app = Flask(__name__)
@app.route('/')
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API! <br/>
    Available Routes: <br/>
    /api/v1.0/precipitation <br/>
    /api/v1.0/stations <br/>
    /api/v1.0/tobs <br/>
    /api/v1.0/temp/start/end <br/>
    ''')

@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365) #calculates the day one year ago
    precipitation  = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all() #query to get the date and precipitation for the preious year
    precip = {date: prcp for date, prcp in precipitation} #create a dictionary witht he date as the key and the precipitation as the value
    return jsonify(precip) #jsonify the dictionary so that it is read on the web

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all() #query to get all the staions in the database
    stations = list(np.ravel(results)) #unravel results into one dimensional array, convert that array into a list
    return jsonify(stations=stations) #jsonify the array

@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365) #calculates the day one year ago
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps = temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start = None, end = None): 
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all() # query the database using the list that we just made
        temps = list(np.ravel(results)) # unravel the results into a 1D array and convert them to a list
        return jsonify(temps=temps) # jsonify and return the results # (*sel) indicates there will be multiple results for our query: min,avg, and max
    
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all() 
    temps = list(np.ravel(results))
    return jsonify(temps=temps)                                             
