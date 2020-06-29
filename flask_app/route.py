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
    device_name = request.form.get('device')
    duration = request.form.get('duration')
    duration = int(duration)
    source = request.form.get('source')

    device_monitor.device_name = device_name
    result = device_monitor.collect_stats(duration, source)

    summary = {
        key: value
        for key, value in result.items()
        if key not in ["Outliers: ", "Percentiles: "]
    }

    summary["25th"] = result.get("Percentiles: ")[0]
    summary["50th"] = result.get("Percentiles: ")[1]
    summary["75th"] = result.get("Percentiles: ")[2]
    summary["95th"] = result.get("Percentiles: ")[3]

    for key, value in summary.items():
        if isinstance(value, float):
            summary[key] = round(value, 2)

    if result.get("Outliers: "):
        summary["Outlier count: "] = len(result.get("Outliers: "))
    else:
        summary["Outlier count:"] = 0

    return render_template("index.html", summary=summary)


if __name__ == "__main__":
    app.run(debug=True)
