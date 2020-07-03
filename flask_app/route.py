import os
import sys
import plotly
import json
import numpy as np
import plotly.graph_objs as go

from flask import make_response, request, render_template
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from flask_app import device_monitor, app
from flask_googlemaps import Map


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/monitor', methods=['GET', 'POST'])
def monitor():
    '''
    For rendering results on HTML GUI
    '''
    duration = request.form.get('duration')
    duration = int(duration)
    source = request.form.get('source')

    result = device_monitor.collect_stats(duration, source)

    meta = {
        key: value
        for key, value in result.items() if key not in ["stats"]
    }

    stats = result["stats"]
    names = [stat["sensor_name"] for stat in stats]
    num_observations = [stat["num_of_observations"] for stat in stats]
    outliers = [stat["outlier_count"] for stat in stats]

    plot = outlier_plot(names, num_observations, outliers)

    return render_template("index.html", meta=meta, stats=stats, plot=plot)


@app.route('/detail', methods=['GET', 'POST'])
def detail():
    """
    Method for retreiving and ploting sensor-specific 
    location and histogram.
    """
    plot = None
    sensorloc = None
    device = request.form.get("device")
    duration = request.form.get("duration")

    data = device_monitor.from_db(3600, device)
    data = data.get(device)

    sensor_location = device_monitor.get_location(device)
    if device:
        plot = hist_plot(device, data)
        sensor_location = sensor_location[0]
        lng, lat = float(sensor_location[0]), float(sensor_location[1])

        sensorloc = Map(identifier="view-side",
                        lat=lat,
                        lng=lng,
                        markers=[(lat, lng)])
    return render_template("detail.html", plot=plot, sensorloc=sensorloc)


def outlier_plot(sensor_names, observations, outliers):
    """
    Generates a scatter plot of sensors vs observations with 
    the size of points indicating the number of outlier 
    observations.
    """
    min_size = 10
    max_size = 50

    markers = []
    min_val = min(outliers)
    max_val = max(outliers)

    for val in outliers:
        marker = min_size + (max_size - min_size) * (val / (max_val - min_val))
        markers.append(marker)

    fig = go.Figure()

    data = fig.add_trace(
        go.Scatter(x=sensor_names,
                   y=observations,
                   mode='markers',
                   marker_color=markers,
                   marker=dict(size=markers),
                   text=outliers))

    fig.update_layout(
        autosize=False,
        width=1000,
        height=600,
        yaxis=dict(title_text="Number of readings",
                   titlefont=dict(size=16),
                   showgrid=False,
                   zeroline=False),
        xaxis=dict(title_text="Sensor name",
                   titlefont=dict(size=16),
                   showgrid=False,
                   zeroline=False),
        plot_bgcolor="rgb(179,226,205)",
    )

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def hist_plot(device_name, data):
    """
    Given a sensor, plot a histogram of observations.
    """
    fig = go.Figure()

    data = fig.add_trace(
        go.Histogram(x=data,
                     name=device_name,
                     marker_color='#330C73',
                     opacity=0.75))

    fig.update_layout(yaxis=dict(title_text="Count",
                                 titlefont=dict(size=16),
                                 showgrid=False,
                                 zeroline=False),
                      xaxis=dict(title_text=device_name,
                                 showgrid=False,
                                 zeroline=False),
                      plot_bgcolor="rgb(179,226,205)",
                      bargap=0.05)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


if __name__ == "__main__":
    app.run(debug=True)
