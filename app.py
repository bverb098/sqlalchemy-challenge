from flask import Flask, jsonify
from matplotlib.pyplot import close
from requests import session
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from sqlalchemy import create_engine, func
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base=automap_base()
Base.prepare(engine,reflect=True)
# Save references to each table
measurement=Base.classes.measurement
station=Base.classes.station

#determine the last year of data recorded
session=Session(engine)
most_recent_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
qry_date=dt.datetime.strptime(most_recent_date[0],'%Y-%m-%d')-dt.timedelta(days=365)
qry_date=qry_date.strftime('%Y-%m-%d')
session.close()

app = Flask(__name__)

@app.route("/")
def home_page():
    return (
        f"Hawaiin Weather Station Data <br/>"
        f"Available routes:<br/><br/>"
        f"Most recent year of data from all stations:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"All weather station details:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Last year of temperature data from the most active station:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Search minimum, maximum and average temperature from start date of your choosing (all stations, up til most current data):<br/>"
        f"/api/v1.0/start<br/>"
        f"Enter start date in format YYYY-MM-DD<br/><br/>"
        f"Search minimum, maximum and average temperature from start and end date of your choosing (all stations):<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Enter start and end dates in format YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #use query and make a list of dictionaries
    session=Session(engine)
    prcp_scores=session.query(measurement.date,measurement.prcp).\
    filter(measurement.date >= qry_date).all()
    precip_list = []
    precip_dic={}
    for row in prcp_scores:
        precip_dic[row[0]]=row[1]
        precip_list.append(precip_dic)
    session.close()

    return (
        jsonify(precip_list)
        )
    
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    station_list=[]
    station_dic={}
    station_info=session.query(station.station,station.name,station.latitude,station.longitude,station.elevation).all()
    for stat in station_info:
        station_dic["Station ID"]=stat[0]
        station_dic["Station Name"]=stat[1]
        station_dic["Latitude"]=stat[2]
        station_dic["Longitude"]=stat[3]
        station_dic["Elevation"]=stat[4]
        station_list.append(station_dic)
    session.close()

    return(jsonify(station_list))
    


@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    temp_list=[]
    temp_dic={}

    most_active_station=session.query(measurement.station,func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).\
        first()[0]

    temp_obvs=session.query(measurement.date,measurement.tobs).\
        filter(measurement.date>=qry_date,measurement.station == most_active_station).all()

    for temps in temp_obvs:
        temp_dic[temps[0]]=temps[1]
        temp_list.append(temp_dic)
    session.close()

    return (
        jsonify(temp_list)
    ) 
    
@app.route("/api/v1.0/<start>")
def start(start):

    session=Session(engine)
    start_list=[]
    start_dic={}

    temp_results=session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >=start).all()
    
    date_start=session.query(measurement.date).filter(measurement.date>=start).first()[0]

    for temp in temp_results:
        start_dic["Date Range"]=f"{date_start} - {qry_date}"
        start_dic["Min Temp"]=temp_results[0][0]
        start_dic["Max Temp"]=temp_results[0][1]
        start_dic["Average Temp"]=round(temp_results[0][2],1)

        start_list.append(start_dic)
    
    session.close()

    return (
        jsonify(start_list)
    )

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session=Session(engine)
    start_end_list=[]
    start_end_dic={}

    temp_results=session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >=start,measurement.date <= end).all()
    
    date_start=session.query(measurement.date).filter(measurement.date>=start).first()[0]
    date_end=session.query(measurement.date).filter(measurement.date<=end).order_by(measurement.date.desc()).first()[0]

    for temp in temp_results:
        start_end_dic["Date Range"]=f"{date_start} - {date_end}"
        start_end_dic["Min Temp"]=temp_results[0][0]
        start_end_dic["Max Temp"]=temp_results[0][1]
        start_end_dic["Average Temp"]=round(temp_results[0][2],1)

        start_end_list.append(start_end_dic)
    
    session.close()

    return (
        jsonify(start_end_list)
    )

if __name__ == "__main__":
    app.run(debug=True)
