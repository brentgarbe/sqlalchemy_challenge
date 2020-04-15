#%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

from datetime import date
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import create_engine, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes['measurement']
Station = Base.classes['station']

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def HomePage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"//api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def rain():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #This is running a query for all the all dates and precipitation and 
    #storing it into a data frame so I can do analysis on it
    precip = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).all()
    precip_df = pd.DataFrame(precip,columns=['date','prcp'])

    session.close()

    #Converting to datetime
    precip_df['date'] = pd.to_datetime(precip_df['date'])

    # Convert list of tuples into normal list
    rain = list(np.ravel(precip_df))

    #Returning precipitation data
    return jsonify(rain)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Design a query to show how many stations are available in this dataset?
    station = session.query(Station.id,Station.name,Station.station).all()
    station_df = pd.DataFrame(station,columns=['id','name','station'])

    session.close()

    station_list = station_df['station']

    # Convert list of tuples into normal list
    station_return = list(np.ravel(station_list))

    return jsonify(station_return)

@app.route("/api/v1.0/tobs")
def temps():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    measure_all = session.query(Measurement).statement
    measure_all_df = pd.read_sql_query(measure_all,session.bind)

    station_all = session.query(Station).statement
    station_all_df = pd.read_sql_query(station_all,session.bind)

    session.close()

    #This is a merge of the two databases for info needed below
    merge_db = pd.merge(measure_all_df,station_all_df,on="station")

   
    # List the stations and the counts in descending order.
    most_active = merge_db.groupby(merge_db['station'])
    row_count = most_active['tobs'].count()
    row_count = row_count.to_frame()
    row_count = row_count.sort_values(['tobs'],ascending=False)

    #This is the station with the most data
    max_data = row_count.max()
    max_station = row_count.loc[row_count['tobs'] == max_data[0]]

    #This gets data for only the most active station and databases it
    active_station = merge_db.loc[merge_db['station']== max_station.index[0]]


    #Converting to datetime and sorting by most recent date
    active_station['date'] = pd.to_datetime(active_station['date'])
    active_station = active_station.sort_values(['date'],ascending=False)

    #This is getting the most recent date in the database
    lastdate = active_station.iloc[0]['date']
    lastdate = pd.to_datetime(lastdate)
    print(lastdate)

    #Getting date from 12 months ago
    query_date = lastdate + relativedelta(months=-12)
    query_date = pd.to_datetime(query_date)
    print(query_date)

    #Here I am filtering only the dates after our query date
    last12mo_merge = active_station.loc[active_station["date"] >= query_date, :]


    #This is a DB of the dates and temps of the most active station for the last year
    date_temp = last12mo_merge[['date','tobs']]

    # Convert list of tuples into normal list
    temp_12mo = list(np.ravel(date_temp))

    return jsonify(temp_12mo)

@app.route("/api/v1.0/<start>")
def return_start_data(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    measure_all = session.query(Measurement).statement
    measure_all_df = pd.read_sql_query(measure_all,session.bind)

    station_all = session.query(Station).statement
    station_all_df = pd.read_sql_query(station_all,session.bind)

    session.close()

    #This is a merge of the two databases for info needed below
    merge_db = pd.merge(measure_all_df,station_all_df,on="station")

    #This is taking the date inputted and converting to a date
    query_date = pd.to_datetime(start)

    #Here I am filtering only the dates after our query date
    query_db = merge_db.loc[merge_db["date"] >= query_date, :]


    #This is a DB of the dates and temps of the most active station for the last year
    date_temp = query_db[['date','tobs']]

    # Convert list of tuples into normal list
    query = list(np.ravel(date_temp))

    return jsonify(query)

@app.route("/api/v1.0/<start>/<end>")
def return_end_data(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    measure_all = session.query(Measurement).statement
    measure_all_df = pd.read_sql_query(measure_all,session.bind)

    station_all = session.query(Station).statement
    station_all_df = pd.read_sql_query(station_all,session.bind)

    session.close()

    #This is a merge of the two databases for info needed below
    merge_db = pd.merge(measure_all_df,station_all_df,on="station")

    #This is taking the date inputted and converting to a date
    query_start_date = pd.to_datetime(start)
    query_end_date = pd.to_datetime(end)

    #Here I am filtering only the dates after our query date
    query_db1 = merge_db.loc[merge_db["date"] >= query_start_date, :]
    query_db1 = query_db1.loc[merge_db["date"] <= query_end_date, :]

    #This is a DB of the dates and temps of the most active station for the last year
    date_temp1 = query_db1[['date','tobs']]

    # Convert list of tuples into normal list
    query1 = list(np.ravel(date_temp1))

    return jsonify(query1)




if __name__ == '__main__':
    app.run(debug=True)


    # # Create a dictionary from the row data and append to a list of all_passengers
    # all_passengers = []
    # for name, age, sex in results:
    #     passenger_dict = {}
    #     passenger_dict["name"] = name
    #     passenger_dict["age"] = age
    #     passenger_dict["sex"] = sex
    #     all_passengers.append(passenger_dict)

    # return jsonify(all_passengers)


