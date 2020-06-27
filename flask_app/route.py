from flask_app import device_monitor, app
from flask import request, jsonify, render_template


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/monitor', methods=['POST'])
def monitor():
    '''
    For rendering results on HTML GUI
    '''
    device_name = request.form.get('device')
    duration = request.form.get('duration')

    device_monitor.device_name = device_name
    result = device_monitor.collect_stats(duration)

    summary = {key: value for key, value in result if key != "outliers"}
    outlier = result.get("outliers")

    return render_template('index.html', summary=summary, outlier=outlier)


if __name__ == "__main__":
    app.run(debug=True)
