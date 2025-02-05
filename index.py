from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import sqlite3
from threading import Thread # To send emails in the background
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import requests

app = Flask(__name__)
CORS(app)
@app.route('/api/population/<int:year>/<string:stateCode>', methods=['GET'])
def get_population_by_year_state(year, stateCode):
    url = f"https://api.census.gov/data/{year}/acs/acsse?get=K200101_001E&for=state:{stateCode}&key=83e384a00001c1bfd012b612302bd069ac8b7b48"
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        return f"Error: {response.status_code}"

@app.route('/api/state/<string:geoid>/<string:checkedItems>', methods=['GET'])
def get_by_state(geoid, checkedItems):
    items = checkedItems.split(',')
    for item in items:
        if item == 'Population':
            population = get_population_by_state(geoid)
            print(population, 'population')
        elif item == 'Median Household Income':
            medianHouseholdIncome = get_median_household_income_by_state(geoid)
            print(medianHouseholdIncome, 'medianHouseholdIncome')
        elif item == 'Population Growth':
            populationGrowth = population_growth(geoid)
            print(populationGrowth, 'populationGrowth')
    return jsonify({'Population': population, 'Median Household Income': medianHouseholdIncome, 'Population Growth': populationGrowth})

def get_population_by_state(stateCode):
    year = 2023
    url = f"https://api.census.gov/data/{year}/acs/acsse?get=K200101_001E&for=state:{stateCode}&key=83e384a00001c1bfd012b612302bd069ac8b7b48"
    response = requests.get(url)
    if response.status_code == 200:
        return int(response.json()[1][0])
    else:
        return f"Error: {response.status_code}"

def get_median_household_income_by_state(stateCode):    
    year = 2023
    url = f"https://api.census.gov/data/{year}/acs/acs1?get=B19019_001E&for=state:{stateCode}&key=83e384a00001c1bfd012b612302bd069ac8b7b48"
    response = requests.get(url)
    if response.status_code == 200:
        return int(response.json()[1][0])
    else:
        return f"Error: {response.status_code}"

def population_growth(stateCode):
    past_year = 2022
    url = f"https://api.census.gov/data/{past_year}/acs/acsse?get=K200101_001E&for=state:{stateCode}&key=83e384a00001c1bfd012b612302bd069ac8b7b48"
    response = requests.get(url)
    if response.status_code == 200:
        past_polulation = int(response.json()[1][0])
    year = 2023
    url = f"https://api.census.gov/data/{year}/acs/acsse?get=K200101_001E&for=state:{stateCode}&key=83e384a00001c1bfd012b612302bd069ac8b7b48"
    response = requests.get(url)
    if response.status_code == 200:
        population = int(response.json()[1][0])
    return (population - past_polulation) / past_polulation * 100


if __name__ == '__main__':
    app.run()
    
