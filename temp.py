

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