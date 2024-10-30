# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table

Station = Base.classes.station
Measurement = Base.classes.measurement
# Create our session (link) from Python to the DB
session =Session(engine)

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    dt_year_prior = ((dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d'))
    
    # Retrieve the data and precipitation scores
    year_prior_data  = (session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= dt_year_prior).all()) 

    # Close Session                                                  
    session.close()

    # Create a dictionary 
    prcp_data = []
    for date, prcp in year_prior_data:
        prior_dict = [f"{date}",f"{prcp} inches"]
        prcp_data.append(prior_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Retrieve data for all stations
    stations = session.query(Station.name, Station.station).all()
    
    # Close Session                                                  
    session.close()
              
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temps():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and temperature scores
    temps_data = (session
             .query(Measurement.station, Measurement.tobs)
             .filter(Measurement.date >= '2016-08-23') 
             .filter(Measurement.station == 'USC00519281')
             .all())

    session.close()

    #Return a JSON list
    return jsonify(dict(temps_data))

#5 - Return the temperature summary for a specified start or start-end range.
#5a
@app.route("/api/v1.0/<start>")
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Get the temperature summary for a specified start date to the end of the dataset
    results = (session
                .query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))
                .filter(Measurement.date >= start)
                .all())
    
        
    (min, max, avg) = results[0] 

    session.close()
    return jsonify(f"Start date: {start}",f"Temperature (F) High: {round(min,1)}, Low: {round(max,1)}, Average: {round(avg,1)}")

#5b
@app.route("/api/v1.0/<start>/<end>")
def range_date(start,end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Get the temperature summary for a specified start date to the specified end date
    results = (session
                .query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))
                .filter(Measurement.date >= start)
                .filter(Measurement.date <= end)
                .all())

    
    (min, max, avg) = results[0] 
                                              
    session.close()
     #Reture a JSON
    return jsonify(f"Start Date: {start}",
                   f"End Date: {start}",
                   f"Temperature (F) High: {round(min,1)}, Low: {round(max,1)}, Average: {round(avg,1)}")




if __name__ == '__main__':
    app.run(debug=True)