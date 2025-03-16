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
        if len(column_labels[i]) == 6:
            selected_labels.append(column_labels[i][:4])
        else:
            selected_labels.append(column_labels[i][-4:])
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

@app.route('/api/state/yoy/home-value', methods=['GET'])
def state_yoy_home_value():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-home-value.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)
    
@app.route('/api/state/yoy/home-value-growth-yoy', methods=['GET'])
def state_yoy_home_value_growth_yoy():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-home-value-growth-yoy.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    
    df1 = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-home-value.csv'), index_col=0)
    if state_code in df1.index:
        state_row1 = df1.loc[state_code]
    else:
        state_row1 = df1.loc[abbreviation]
    column_labels1 = state_row1.index.tolist()
    values1 = state_row1.values.tolist()
    column_labels1, values1 = trim_array(column_labels1, values1)
    final_labels1, final_values1 = calculate_m2y(column_labels1, values1)
    
    response = { "fullLabels": [final_labels, final_labels1[:-1], final_labels1[1:]], "fullData": [final_values, final_values1[:-1], final_values1[1:]] }
    return jsonify(response)

@app.route('/api/state/yoy/overvalued-percent', methods=['GET'])
def state_yoy_overvalued_percent():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-overvalued-percent.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    
    df1 = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-home-value.csv'), index_col=0)
    if state_code in df1.index:
        state_row1 = df1.loc[state_code]
    else:
        state_row1 = df1.loc[abbreviation]
    column_labels1 = state_row1.index.tolist()
    values1 = state_row1.values.tolist()
    column_labels1, values1 = trim_array(column_labels1, values1)
    final_labels1, final_values1 = calculate_m2y(column_labels1, values1)
    
    filtered_labels1 = [label for label in final_labels1 if label in column_labels]
    filtered_values1 = [final_values1[final_labels1.index(label)] for label in filtered_labels1]

    
    response = { "fullLabels": [final_labels], "fullData": [final_values, filtered_values1] }
    return jsonify(response)

@app.route('/api/state/yoy/value-to-income-ratio', methods=['GET'])
def state_yoy_value_to_income_ration():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    
    additinal_fields = []
    
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-value-to-income-ratio.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/mortgage-payment', methods=['GET'])
def state_yoy_mortgage_payment():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-mortgage-payment.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/salary-to-house', methods=['GET'])
def state_yoy_salary_to_house():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-salary-to-house.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/mtg-payment-to-income', methods=['GET'])
def state_yoy_mtg_payment_to_income():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-mtg-payment-to-income.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/property-tax-rate', methods=['GET'])
def state_yoy_property_tax_rate():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-property-tax-rate.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/percent-crash-07-12', methods=['GET'])
def state_yoy_percent_crash_07_12():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-percent-crash-07-12.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/home-value-growth-mom', methods=['GET'])
def state_yoy_home_value_growth_mom():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-home-value-growth-mom.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/vacancy-rate', methods=['GET'])
def state_yoy_vacancy_rate():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-vacancy-rate.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/shadow-inventory-percent', methods=['GET'])
def state_yoy_shadow_inventory_percent():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-shadow-inventory-percent.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/migration-total', methods=['GET'])
def state_yoy_migration_total():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-migration-total.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/migration-percent-of-population', methods=['GET'])
def state_yoy_migration_percent_of_population():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-migration-percent-of-population.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/population', methods=['GET'])
def state_yoy_population():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-population.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/median-household-income', methods=['GET'])
def state_yoy_median_household_income():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-median-household-income.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/population-growth', methods=['GET'])
def state_yoy_population_growth():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-population-growth.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/income-growth', methods=['GET'])
def state_yoy_income_growth():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-income-growth.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/remote-work-percent', methods=['GET'])
def state_yoy_remote_work_percent():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-remote-work-percent.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/homeownership-rate', methods=['GET'])
def state_yoy_homeownership_rate():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-homeownership-rate.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/mortgaged-home-percent', methods=['GET'])
def state_yoy_mortgaged_home_percent():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-mortgaged-home-percent.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/median-age', methods=['GET'])
def state_yoy_median_age():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-median-age.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/poverty-rate', methods=['GET'])
def state_yoy_poverty_rate():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-poverty-rate.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/housing-units', methods=['GET'])
def state_yoy_housing_units():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-housing-units.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/housing-units-growth-rate', methods=['GET'])
def state_yoy_housing_units_growth_rate():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-housing-units-growth-rate.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/college-degree-rate', methods=['GET'])
def state_yoy_college_degree_rate():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-college-degree-rate.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/building-permits', methods=['GET'])
def state_yoy_building_permits():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-building-permits.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/for-sale-inventory', methods=['GET'])
def state_yoy_for_sale_inventory():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-for-sale-inventory.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/sale-inventory-growth-yoy', methods=['GET'])
def state_yoy_sale_inventory_growth_yoy():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-sale-inventory-growth-yoy.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/sale-inventory-growth-mom', methods=['GET'])
def state_yoy_sale_inventory_growth_mom():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-sale-inventory-growth-mom.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/inventory-surplus-to-deficit', methods=['GET'])
def state_yoy_inventory_surplus_to_deficit():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-inventory-surplus-to-deficit.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/price-cut-percent', methods=['GET'])
def state_yoy_price_cut_percent():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-price-cut-percent.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/days-on-market', methods=['GET'])
def state_yoy_days_on_market():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-days-on-market.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/days-on-market-growth-yoy', methods=['GET'])
def state_yoy_days_on_market_growth_yoy():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-days-on-market-growth-yoy.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/inventory-to-houses', methods=['GET'])
def state_yoy_inventory_to_houses():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-inventory-to-houses.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/median-listing-price', methods=['GET'])
def state_yoy_median_listing_price():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-median-listing-price.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/median-listing-price-growth-yoy', methods=['GET'])
def state_yoy_median_listing_price_growth_yoy():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-median-listing-price-growth-yoy.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/new-listing-count', methods=['GET'])
def state_yoy_new_listing_count():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-new-listing-count.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/state/yoy/new-listing-count-growth-yoy', methods=['GET'])
def state_yoy_new_listing_count_growth_yoy():
    state_code = request.args.get('stateCode')
    abbreviation = request.args.get('abbreviation')
    state_code = int(state_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'state/us-state-new-listing-count-growth-yoy.csv'), index_col=0)
    if state_code in df.index:
        state_row = df.loc[state_code]
    else:
        state_row = df.loc[abbreviation]
    column_labels = state_row.index.tolist()
    values = state_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/home-value', methods=['GET'])
def metro_yoy_home_value():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-home-value.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)
    
@app.route('/api/metro/yoy/home-value-growth-yoy', methods=['GET'])
def metro_yoy_home_value_growth_yoy():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-home-value-growth-yoy.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/overvalued-percent', methods=['GET'])
def metro_yoy_overvalued_percent():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-overvalued-percent.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/value-to-income-ratio', methods=['GET'])
def metro_yoy_value_to_income_ration():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    
    additinal_fields = []
    
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-value-to-income-ratio.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/mortgage-payment', methods=['GET'])
def metro_yoy_mortgage_payment():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-mortgage-payment.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/salary-to-house', methods=['GET'])
def metro_yoy_salary_to_house():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-salary-to-house.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/mtg-payment-to-income', methods=['GET'])
def metro_yoy_mtg_payment_to_income():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-mtg-payment-to-income.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/property-tax-rate', methods=['GET'])
def metro_yoy_property_tax_rate():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-property-tax-rate.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/buy-v-rent-differential', methods=['GET'])
def metro_yoy_buy_v_rent_differential():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-buy-v-rent-differential.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/percent-crash-07-12', methods=['GET'])
def metro_yoy_percent_crash_07_12():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-percent-crash-07-12.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/home-value-growth-mom', methods=['GET'])
def metro_yoy_home_value_growth_mom():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-home-value-growth-mom.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/vacancy-rate', methods=['GET'])
def metro_yoy_vacancy_rate():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-vacancy-rate.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/shadow-inventory-percent', methods=['GET'])
def metro_yoy_shadow_inventory_percent():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-shadow-inventory-percent.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/migration-total', methods=['GET'])
def metro_yoy_migration_total():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-migration-total.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/migration-percent-of-population', methods=['GET'])
def metro_yoy_migration_percent_of_population():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-migration-percent-of-population.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/population', methods=['GET'])
def metro_yoy_population():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-population.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/median-household-income', methods=['GET'])
def metro_yoy_median_household_income():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-median-household-income.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/population-growth', methods=['GET'])
def metro_yoy_population_growth():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-population-growth.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/income-growth', methods=['GET'])
def metro_yoy_income_growth():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-income-growth.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/remote-work-percent', methods=['GET'])
def metro_yoy_remote_work_percent():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-remote-work-percent.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/homeownership-rate', methods=['GET'])
def metro_yoy_homeownership_rate():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-homeownership-rate.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/mortgaged-home-percent', methods=['GET'])
def metro_yoy_mortgaged_home_percent():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-mortgaged-home-percent.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/median-age', methods=['GET'])
def metro_yoy_median_age():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-median-age.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/poverty-rate', methods=['GET'])
def metro_yoy_poverty_rate():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-poverty-rate.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/housing-units', methods=['GET'])
def metro_yoy_housing_units():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-housing-units.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/housing-units-growth-rate', methods=['GET'])
def metro_yoy_housing_units_growth_rate():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-housing-units-growth-rate.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/college-degree-rate', methods=['GET'])
def metro_yoy_college_degree_rate():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-college-degree-rate.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/building-permits', methods=['GET'])
def metro_yoy_building_permits():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-building-permits.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/for-sale-inventory', methods=['GET'])
def metro_yoy_for_sale_inventory():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-for-sale-inventory.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/sale-inventory-growth-yoy', methods=['GET'])
def metro_yoy_sale_inventory_growth_yoy():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-sale-inventory-growth-yoy.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/sale-inventory-growth-mom', methods=['GET'])
def metro_yoy_sale_inventory_growth_mom():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-sale-inventory-growth-mom.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/inventory-surplus-to-deficit', methods=['GET'])
def metro_yoy_inventory_surplus_to_deficit():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-inventory-surplus-to-deficit.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/price-cut-percent', methods=['GET'])
def metro_yoy_price_cut_percent():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-price-cut-percent.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/days-on-market', methods=['GET'])
def metro_yoy_days_on_market():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-days-on-market.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/days-on-market-growth-yoy', methods=['GET'])
def metro_yoy_days_on_market_growth_yoy():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-days-on-market-growth-yoy.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/inventory-to-houses', methods=['GET'])
def metro_yoy_inventory_to_houses():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-inventory-to-houses.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/median-listing-price', methods=['GET'])
def metro_yoy_median_listing_price():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-median-listing-price.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/median-listing-price-growth-yoy', methods=['GET'])
def metro_yoy_median_listing_price_growth_yoy():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-median-listing-price-growth-yoy.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/new-listing-count', methods=['GET'])
def metro_yoy_new_listing_count():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-new-listing-count.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/new-listing-count-growth-yoy', methods=['GET'])
def metro_yoy_new_listing_count_growth_yoy():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-new-listing-count-growth-yoy.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/rental-rate', methods=['GET'])
def metro_yoy_rental_rate():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-rental-rate.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/rent-for-houses', methods=['GET'])
def metro_yoy_rent_for_houses():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-rent-for-houses.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/cap-rate', methods=['GET'])
def metro_yoy_cap_rate():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-cap-rate.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/home-value-to-rent-ratio', methods=['GET'])
def metro_yoy_home_value_to_rent_ratio():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-home-value-to-rent-ratio.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/rent-to-income', methods=['GET'])
def metro_yoy_rent_to_income():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-rent-to-income.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/metro/yoy/rent-growth-yoy', methods=['GET'])
def metro_yoy_rent_growth_yoy():
    metro_code = request.args.get('metroCode')
    abbreviation = request.args.get('abbreviation')
    metro_code = int(metro_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'metro/us-metro-rent-growth-yoy.csv'), index_col=0)
    if metro_code in df.index:
        metro_row = df.loc[metro_code]
    else:
        metro_row = df.loc[abbreviation]
    column_labels = metro_row.index.tolist()
    values = metro_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/home-value', methods=['GET'])
def county_yoy_home_value():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-home-value.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)
    
@app.route('/api/county/yoy/home-value-growth-yoy', methods=['GET'])
def county_yoy_home_value_growth_yoy():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-home-value-growth-yoy.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/overvalued-percent', methods=['GET'])
def county_yoy_overvalued_percent():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-overvalued-percent.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/value-to-income-ratio', methods=['GET'])
def county_yoy_value_to_income_ration():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    
    additinal_fields = []
    
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-value-to-income-ratio.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/mortgage-payment', methods=['GET'])
def county_yoy_mortgage_payment():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-mortgage-payment.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/salary-to-house', methods=['GET'])
def county_yoy_salary_to_house():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-salary-to-house.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/mtg-payment-to-income', methods=['GET'])
def county_yoy_mtg_payment_to_income():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-mtg-payment-to-income.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/property-tax-rate', methods=['GET'])
def county_yoy_property_tax_rate():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-property-tax-rate.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/buy-v-rent-differential', methods=['GET'])
def county_yoy_buy_v_rent_differential():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-buy-v-rent-differential.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/percent-crash-07-12', methods=['GET'])
def county_yoy_percent_crash_07_12():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-percent-crash-07-12.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/home-value-growth-mom', methods=['GET'])
def county_yoy_home_value_growth_mom():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-home-value-growth-mom.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/vacancy-rate', methods=['GET'])
def county_yoy_vacancy_rate():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-vacancy-rate.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/shadow-inventory-percent', methods=['GET'])
def county_yoy_shadow_inventory_percent():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-shadow-inventory-percent.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/migration-total', methods=['GET'])
def county_yoy_migration_total():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-migration-total.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/migration-percent-of-population', methods=['GET'])
def county_yoy_migration_percent_of_population():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-migration-percent-of-population.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/population', methods=['GET'])
def county_yoy_population():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-population.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/median-household-income', methods=['GET'])
def county_yoy_median_household_income():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-median-household-income.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/population-growth', methods=['GET'])
def county_yoy_population_growth():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-population-growth.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/income-growth', methods=['GET'])
def county_yoy_income_growth():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-income-growth.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/remote-work-percent', methods=['GET'])
def county_yoy_remote_work_percent():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-remote-work-percent.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/homeownership-rate', methods=['GET'])
def county_yoy_homeownership_rate():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-homeownership-rate.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/mortgaged-home-percent', methods=['GET'])
def county_yoy_mortgaged_home_percent():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-mortgaged-home-percent.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/median-age', methods=['GET'])
def county_yoy_median_age():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-median-age.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/poverty-rate', methods=['GET'])
def county_yoy_poverty_rate():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-poverty-rate.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/housing-units', methods=['GET'])
def county_yoy_housing_units():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-housing-units.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/housing-units-growth-rate', methods=['GET'])
def county_yoy_housing_units_growth_rate():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-housing-units-growth-rate.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/college-degree-rate', methods=['GET'])
def county_yoy_college_degree_rate():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-college-degree-rate.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/building-permits', methods=['GET'])
def county_yoy_building_permits():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-building-permits.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/for-sale-inventory', methods=['GET'])
def county_yoy_for_sale_inventory():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-for-sale-inventory.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/sale-inventory-growth-yoy', methods=['GET'])
def county_yoy_sale_inventory_growth_yoy():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-sale-inventory-growth-yoy.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/sale-inventory-growth-mom', methods=['GET'])
def county_yoy_sale_inventory_growth_mom():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-sale-inventory-growth-mom.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/inventory-surplus-to-deficit', methods=['GET'])
def county_yoy_inventory_surplus_to_deficit():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-inventory-surplus-to-deficit.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/price-cut-percent', methods=['GET'])
def county_yoy_price_cut_percent():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-price-cut-percent.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/days-on-market', methods=['GET'])
def county_yoy_days_on_market():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-days-on-market.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/days-on-market-growth-yoy', methods=['GET'])
def county_yoy_days_on_market_growth_yoy():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-days-on-market-growth-yoy.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/inventory-to-houses', methods=['GET'])
def county_yoy_inventory_to_houses():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-inventory-to-houses.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/median-listing-price', methods=['GET'])
def county_yoy_median_listing_price():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-median-listing-price.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/median-listing-price-growth-yoy', methods=['GET'])
def county_yoy_median_listing_price_growth_yoy():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-median-listing-price-growth-yoy.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/new-listing-count', methods=['GET'])
def county_yoy_new_listing_count():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-new-listing-count.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/new-listing-count-growth-yoy', methods=['GET'])
def county_yoy_new_listing_count_growth_yoy():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-new-listing-count-growth-yoy.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/rental-rate', methods=['GET'])
def county_yoy_rental_rate():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-rental-rate.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/rent-for-houses', methods=['GET'])
def county_yoy_rent_for_houses():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-rent-for-houses.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/cap-rate', methods=['GET'])
def county_yoy_cap_rate():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-cap-rate.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/home-value-to-rent-ratio', methods=['GET'])
def county_yoy_home_value_to_rent_ratio():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-home-value-to-rent-ratio.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/rent-to-income', methods=['GET'])
def county_yoy_rent_to_income():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-rent-to-income.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/county/yoy/rent-growth-yoy', methods=['GET'])
def county_yoy_rent_growth_yoy():
    county_code = request.args.get('countyCode')
    abbreviation = request.args.get('abbreviation')
    county_code = int(county_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'county/us-county-rent-growth-yoy.csv'), index_col=0)
    if county_code in df.index:
        county_row = df.loc[county_code]
    else:
        county_row = df.loc[abbreviation]
    column_labels = county_row.index.tolist()
    values = county_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/home-value', methods=['GET'])
def zipcode_yoy_home_value():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-home-value.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)
    
@app.route('/api/zipcode/yoy/home-value-growth-yoy', methods=['GET'])
def zipcode_yoy_home_value_growth_yoy():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-home-value-growth-yoy.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/overvalued-percent', methods=['GET'])
def zipcode_yoy_overvalued_percent():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-overvalued-percent.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/value-to-income-ratio', methods=['GET'])
def zipcode_yoy_value_to_income_ration():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    
    additinal_fields = []
    
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-value-to-income-ratio.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/mortgage-payment', methods=['GET'])
def zipcode_yoy_mortgage_payment():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-mortgage-payment.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/salary-to-house', methods=['GET'])
def zipcode_yoy_salary_to_house():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-salary-to-house.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/mtg-payment-to-income', methods=['GET'])
def zipcode_yoy_mtg_payment_to_income():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-mtg-payment-to-income.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/property-tax-rate', methods=['GET'])
def zipcode_yoy_property_tax_rate():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-property-tax-rate.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/buy-v-rent-differential', methods=['GET'])
def zipcode_yoy_buy_v_rent_differential():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-buy-v-rent-differential.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/percent-crash-07-12', methods=['GET'])
def zipcode_yoy_percent_crash_07_12():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-percent-crash-07-12.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/home-value-growth-mom', methods=['GET'])
def zipcode_yoy_home_value_growth_mom():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-home-value-growth-mom.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/vacancy-rate', methods=['GET'])
def zipcode_yoy_vacancy_rate():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-vacancy-rate.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/shadow-inventory-percent', methods=['GET'])
def zipcode_yoy_shadow_inventory_percent():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-shadow-inventory-percent.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/migration-total', methods=['GET'])
def zipcode_yoy_migration_total():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-migration-total.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/migration-percent-of-population', methods=['GET'])
def zipcode_yoy_migration_percent_of_population():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-migration-percent-of-population.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/population', methods=['GET'])
def zipcode_yoy_population():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-population.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/median-household-income', methods=['GET'])
def zipcode_yoy_median_household_income():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-median-household-income.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/population-growth', methods=['GET'])
def zipcode_yoy_population_growth():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-population-growth.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/income-growth', methods=['GET'])
def zipcode_yoy_income_growth():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-income-growth.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/remote-work-percent', methods=['GET'])
def zipcode_yoy_remote_work_percent():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-remote-work-percent.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/homeownership-rate', methods=['GET'])
def zipcode_yoy_homeownership_rate():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-homeownership-rate.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/mortgaged-home-percent', methods=['GET'])
def zipcode_yoy_mortgaged_home_percent():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-mortgaged-home-percent.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/median-age', methods=['GET'])
def zipcode_yoy_median_age():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-median-age.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/poverty-rate', methods=['GET'])
def zipcode_yoy_poverty_rate():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-poverty-rate.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/housing-units', methods=['GET'])
def zipcode_yoy_housing_units():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-housing-units.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/housing-units-growth-rate', methods=['GET'])
def zipcode_yoy_housing_units_growth_rate():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-housing-units-growth-rate.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/college-degree-rate', methods=['GET'])
def zipcode_yoy_college_degree_rate():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-college-degree-rate.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/building-permits', methods=['GET'])
def zipcode_yoy_building_permits():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-building-permits.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/for-sale-inventory', methods=['GET'])
def zipcode_yoy_for_sale_inventory():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-for-sale-inventory.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/sale-inventory-growth-yoy', methods=['GET'])
def zipcode_yoy_sale_inventory_growth_yoy():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-sale-inventory-growth-yoy.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/sale-inventory-growth-mom', methods=['GET'])
def zipcode_yoy_sale_inventory_growth_mom():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-sale-inventory-growth-mom.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/inventory-surplus-to-deficit', methods=['GET'])
def zipcode_yoy_inventory_surplus_to_deficit():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-inventory-surplus-to-deficit.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/price-cut-percent', methods=['GET'])
def zipcode_yoy_price_cut_percent():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-price-cut-percent.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/days-on-market', methods=['GET'])
def zipcode_yoy_days_on_market():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-days-on-market.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/days-on-market-growth-yoy', methods=['GET'])
def zipcode_yoy_days_on_market_growth_yoy():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-days-on-market-growth-yoy.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/inventory-to-houses', methods=['GET'])
def zipcode_yoy_inventory_to_houses():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-inventory-to-houses.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = column_labels, values
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/median-listing-price', methods=['GET'])
def zipcode_yoy_median_listing_price():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-median-listing-price.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/median-listing-price-growth-yoy', methods=['GET'])
def zipcode_yoy_median_listing_price_growth_yoy():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-median-listing-price-growth-yoy.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/new-listing-count', methods=['GET'])
def zipcode_yoy_new_listing_count():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-new-listing-count.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/new-listing-count-growth-yoy', methods=['GET'])
def zipcode_yoy_new_listing_count_growth_yoy():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-new-listing-count-growth-yoy.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/rental-rate', methods=['GET'])
def zipcode_yoy_rental_rate():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-rental-rate.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/rent-for-houses', methods=['GET'])
def zipcode_yoy_rent_for_houses():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-rent-for-houses.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/cap-rate', methods=['GET'])
def zipcode_yoy_cap_rate():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-cap-rate.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/home-value-to-rent-ratio', methods=['GET'])
def zipcode_yoy_home_value_to_rent_ratio():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-home-value-to-rent-ratio.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/rent-to-income', methods=['GET'])
def zipcode_yoy_rent_to_income():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-rent-to-income.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

@app.route('/api/zipcode/yoy/rent-growth-yoy', methods=['GET'])
def zipcode_yoy_rent_growth_yoy():
    zipcode_code = request.args.get('zipCode')
    abbreviation = request.args.get('abbreviation')
    zipcode_code = int(zipcode_code)
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'zipcode/us-zipcode-rent-growth-yoy.csv'), index_col=0)
    if zipcode_code in df.index:
        zipcode_row = df.loc[zipcode_code]
    else:
        zipcode_row = df.loc[abbreviation]
    column_labels = zipcode_row.index.tolist()
    values = zipcode_row.values.tolist()
    column_labels, values = trim_array(column_labels, values)
    final_labels, final_values = calculate_m2y(column_labels, values)
    response = { "fullLabels": [final_labels], "fullData": [final_values] }
    return jsonify(response)

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
    
