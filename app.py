from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import sqlite3
from threading import Thread # To send emails in the background
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import requests
import pandas as pd
import json
from constants import mapping_dict, state_mapping, yoy_list

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def trim_array(column_labels, values):
    start_index = 0
    end_index = len(values) - 1
    
    while start_index < len(values) - 1 and (pd.isna(values[start_index]) or values[start_index] == '#VALUE!'):
        start_index += 1
    
    while end_index >= 0 and (pd.isna(values[start_index]) or values[start_index] == '#VALUE!'):
        end_index -= 1
    
    trimmed_values = values[start_index:end_index + 1]
    trimmed_column_labels = column_labels[start_index:end_index + 1]
    
    trimmed_values = [0 if pd.isna(v) or v == '#VALUE!' else v for v in trimmed_values]
    
    return trimmed_column_labels, trimmed_values

def calculate_m2y(column_labels, values):

    selected_labels = []
    selected_values = []
    
    for i in range(len(column_labels) - 1, -1, -12):
        selected_labels.append(column_labels[i][:4])
        selected_values.append(values[i])
    
    final_labels = selected_labels[::-1]
    final_values = selected_values[::-1]
    
    return final_labels, final_values

def calculate_y2m(yoy_labels, yoy_values):
       
    mom_values = []
    mom_labels = []
    
    for i in range(len(yoy_values) - 1):
        start_value = float(yoy_values[i])
        end_value = float(yoy_values[i + 1])
        start_year = int(yoy_labels[i])  # Year from the yoy_labels
        end_year = int(yoy_labels[i + 1])  # Year from the yoy_labels
        
        mom_labels.append(f'{start_year}12')  # December (12th month)
        mom_values.append(start_value)
        
        months_between = 11
        for j in range(1, months_between + 1):
            interpolated_value = start_value + (j / months_between) * (end_value - start_value)
            
            month_index = (12 + j - 1) % 12 + 1  # For Jan-Nov of the end year
            year_index = start_year + (j // 12)  # Increase year after December
            
            mom_labels.append(f'{start_year + (j // 12)}{str(month_index).zfill(2)}')
            mom_values.append(interpolated_value)
    
    return mom_labels, mom_values

@app.route('/api/state/yoy', methods=['GET'])
def state_yoy():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    data_point_request = request.args.get('dataPoint')
    
    data_point = mapping_dict[data_point_request]["slug"]
    additional_fields = mapping_dict[data_point_request]["additional-data"]
    
    state_code = int(state_code)
    
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-{data_point}.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    print(column_labels) 
    print(values)
    
    final_labels, final_values = column_labels, values
    
    response = {
        "fullLabels": final_labels,
        "fullData": final_values
    }
    
    return jsonify(response)
    

@app.route('/api/state/mom', methods=['GET'])
def state_mom():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    data_point = request.args.get('dataPoint')
    
    data_point = mapping_dict[data_point]["slug"]
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-{data_point}.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
        
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    
    if data_point in yoy_list:
        final_labels, final_values = calculate_y2m(column_labels, values)
    else:
        final_labels, final_values = column_labels, values
    
    response = {
        "fullLabels": final_labels,
        "fullData": final_values
    }
    
    return jsonify(response)

@app.route('/api/all-states', methods=['GET'])
def all_states():
    data_point = request.args.get('dataPoint')
    data_point = mapping_dict[data_point]["slug"]
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-{data_point}.csv'), index_col=0)
    last_column_name = df.columns[-1]  # Column name
    last_column_data = df.iloc[:, -1]  # Column values
    filtered_data = last_column_data.dropna()

    json_data = dict(zip(filtered_data.index.astype(str), filtered_data.values.tolist()))
    return jsonify(json_data)

@app.route('/api/metro/yoy', methods=['GET'])
def metro_yoy():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    data_point = request.args.get('dataPoint')
    
    data_point = mapping_dict[data_point]["slug"]
    metro_code = int(metro_code)
    
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-{data_point}.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    
    if data_point in yoy_list:
        final_labels, final_values = column_labels, values
    else:
        final_labels, final_values = calculate_m2y(column_labels, values)
        
    
    response = {
        "fullLabels": final_labels,
        "fullData": final_values
    }
    
    return jsonify(response)
    

@app.route('/api/metro/mom', methods=['GET'])
def metro_mom():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    data_point = request.args.get('dataPoint')
    
    data_point = mapping_dict[data_point]["slug"]
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-{data_point}.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
        
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    
    if data_point in yoy_list:
        final_labels, final_values = calculate_y2m(column_labels, values)
    else:
        final_labels, final_values = column_labels, values
    
    response = {
        "fullLabels": final_labels,
        "fullData": final_values
    }
    
    return jsonify(response)

@app.route('/api/all-metros', methods=['GET'])
def all_metros():
    data_point = request.args.get('dataPoint')
    data_point = mapping_dict[data_point]["slug"]
    
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-{data_point}.csv'), index_col=0)
    last_column_name = df.columns[-1]  # Column name
    last_column_data = df.iloc[:, -1]  # Column values
    filtered_data = last_column_data.dropna()
    json_data = dict(zip(filtered_data.index.astype(str), filtered_data.values.tolist()))

    return jsonify(json_data)

@app.route('/api/county/yoy', methods=['GET'])
def county_yoy():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    data_point = request.args.get('dataPoint')
    
    data_point = mapping_dict[data_point]["slug"]
    county_code = int(county_code)
    
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-{data_point}.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    
    if data_point in yoy_list:
        final_labels, final_values = column_labels, values
    else:
        final_labels, final_values = calculate_m2y(column_labels, values)
        
    
    response = {
        "fullLabels": final_labels,
        "fullData": final_values
    }
    
    return jsonify(response)
    

@app.route('/api/county/mom', methods=['GET'])
def county_mom():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    data_point = request.args.get('dataPoint')
    
    data_point = mapping_dict[data_point]["slug"]
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-{data_point}.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
        
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    
    if data_point in yoy_list:
        final_labels, final_values = calculate_y2m(column_labels, values)
    else:
        final_labels, final_values = column_labels, values
    
    response = {
        "fullLabels": final_labels,
        "fullData": final_values
    }
    
    return jsonify(response)

@app.route('/api/all-counties', methods=['GET'])
def all_counties():
    data_point = request.args.get('dataPoint')
    
    data_point = mapping_dict[data_point]["slug"]
    
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-{data_point}.csv'), index_col=0)
    last_column_name = df.columns[-1]  # Column name
    last_column_data = df.iloc[:, -1]  # Column values
    filtered_data = last_column_data.dropna()

    json_data = dict(zip(filtered_data.index.astype(str), filtered_data.values.tolist()))

    return jsonify(json_data)
# @app.route('/api/metro/<string:metro_code>/<string:data_point>/yoy', methods=['GET'])
# @app.route('/api/metro/<string:metro_code>/<string:data_point>/mom', methods=['GET'])
# @app.route('/api/all-metros/<string:data_point>/mom', methods=['GET'])

# @app.route('/api/county/<string:county_code>/<string:data_point>/yoy', methods=['GET'])
# @app.route('/api/county/<string:county_code>/<string:data_point>/mom', methods=['GET'])
# @app.route('/api/all-counties/<string:data_point>/mom', methods=['GET'])







# @app.route('/api/zipcode/<string:zipcode>/<string:data_point>/yoy', methods=['GET'])
# @app.route('/api/zipcode/<string:zipcode>/<string:data_point>/mom', methods=['GET'])
# @app.route('/api/all-zipcodes/<string:data_point>/mom', methods=['GET'])


if __name__ == '__main__':
    app.run()
    
