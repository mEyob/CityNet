import os
import sys
import plotly
import json
import numpy as np
import plotly.graph_objs as go

from flask import make_response
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from flask_app import device_monitor, app
from flask import request, jsonify, render_template


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

    plot = create_plot(names, num_observations, outliers)

    return render_template("index.html", meta=meta, stats=stats, plot=plot)


@app.route('/sensor_detail', methods=['GET', 'POST'])
def sensor_detail():
    pass


def chart(stats, device_name, url):
    x = range(len(stats))
    fig, ax = plt.subplots()
    x_label = ['25%', '50%', 'Mean', '75th', '95th']
    sns.barplot(x=x_label, y=stats, palette="rocket", ax=ax)
    ax.set_ylabel(device_name)
    plt.savefig(url)


def create_plot(sensor_names, observations, outliers):
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
                   titlefont=dict(size=18),
                   showgrid=False,
                   zeroline=False),
        xaxis=dict(showgrid=False, zeroline=False),
        plot_bgcolor="rgb(179,226,205)",
    )

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


if __name__ == "__main__":
    app.run(debug=True)
