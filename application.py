#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os

from flask import Flask, Markup, jsonify, render_template, request

from news_updater import update_stock_news

app = Flask(__name__)
app.config['CRON_TOKEN'] = os.getenv('CRON_TOKEN')

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

@app.route('/')
def flask_viz():
    return render_template('flask_viz.html',title='Bitcoin Monthly Price in USD')


@app.route('/home')
def flask_viz1():
    pie_labels = labels
    pie_values = values
    return render_template('flask_viz.html', title='Bitcoin Monthly Price in USD', max=17000, set=zip(values, labels, colors))

@app.route('/bar')
def bar():
    bar_labels=labels
    bar_values=values
    return render_template('bar_chart.html', title='Bitcoin Monthly Price in USD', max=17000, labels=bar_labels, values=bar_values)

@app.route('/line')
def line():
    line_labels=labels
    line_values=values
    return render_template('line_chart.html', title='Bitcoin Monthly Price in USD', max=17000, labels=line_labels, values=line_values)

@app.route('/pie')
def pie():
    pie_labels = labels
    pie_values = values
    return render_template('pie_chart.html', title='Bitcoin Monthly Price in USD', max=17000, set=zip(values, labels, colors))



@app.route('/tasks/update-stock-news', methods=['POST'])
def update_stock_news_task():
    expected_token = app.config.get('CRON_TOKEN')
    provided_token = request.headers.get('X-Cron-Token')

    if expected_token and provided_token != expected_token:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    result = update_stock_news()
    return jsonify(result), 200


if __name__ == '__main__':
    app.run()

