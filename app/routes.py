from app import app
from flask import render_template, request, jsonify, abort
from app.constants import CLEANED_DATA_DIR
import csv
  
  
# Home Page
# - Renders landing-page.html
@app.route('/')
@app.route('/index')
def get_index_page():
    return render_template('landing-page.html')


# Map Page
# - Renders main.html (the map)
@app.route('/map')
def exploreData():
    return render_template('main.html')

# Determines UI options to display on the frontend based on data files
@app.route('/get_ui_options', methods=['GET'])
def get_ui_options():
    options = {
        'years': [],
        'areaType': [],
        'filterType': [],
        'units': [],
    }

    # Will be shown as the very first options in the UI dropdowns (given that they exist in the data folder)
    default_options = {
        'years':        2021,
        'areaType':     'LGA',
        'filterType':   'Homelessness category',
        'units':        'Rate (per 10,000)',
    }

    # Set the options based on the cleaned_data directory
    for file_path in CLEANED_DATA_DIR.iterdir():
        if file_path.is_file() and 'Table' not in file_path.name:
            parts = file_path.stem.split('_')
            
            # Add each option to the an array of options 
                                                    # e.g. given 'LGA_Homelessness category_2021_Rate (per 10,000).csv':
            options['areaType'].append(parts[0])    # LGA
            options['filterType'].append(parts[1])  # Homelessness category
            options['years'].append(int(parts[2]))  # 2021
            options['units'].append(parts[3])       # Rate (per 10,000)
    
    for key, value in options.items():
        # Remove duplicates by converting to set and then back to list
        unique_values = list(set(value))

        # Sort the filter types, so they always appear in the same order on the UI
        unique_values.sort()

        # Check if there is a default option for the key
        if key in default_options and default_options[key] in unique_values:
            # Move the default option to the first option for the dropdown
            unique_values.remove(default_options[key])
            unique_values.insert(0, default_options[key])

        options[key] = unique_values
    
    return options

# - No pages are rendered
# - Functions get the ABS data 
@app.route('/get_abs_data', methods=['GET'])
def get_abs_data_route():
    abs_data = get_abs_data(request)

    if abs_data is None:
        abort(404)
    return jsonify(abs_data)

# Helper function to retrieve cleaned ABS data
def get_abs_data(request):
    table_name = get_cleaned_data_file_name(request)
    table_path = CLEANED_DATA_DIR / f'{table_name}'

    abs_metadata = {}
    abs_data = {} 

    # Open the CSV file corresponding to the table
    try:
        with open(table_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Add the header row to the 'metadata' dictionary
            header = next(csv_reader)
            abs_metadata['header'] = header

            # Which index of the header do the numbers start
            data_start_index = 1
            abs_metadata['filterOptions'] = header[data_start_index:]

            # Which category (denoted by its index) to display by default
            abs_metadata['defaultOption'] = 0

            # Add the rest of the rows to the 'data' dictionary
            for row in csv_reader:
                key = row[0]
                values = row[1:]
                abs_data[key] = values

        return {'metadata': abs_metadata, 'data': abs_data}
    except FileNotFoundError as e:
        print(e)
        return None

# Helper function to retrieve the corresponding file where the data is stored
def get_cleaned_data_file_name(request):
    area_type = request.args.get('areaType')
    filter_type = request.args.get('filterType')
    year = request.args.get('year')
    units = request.args.get('units')

    cleaned_data_file_name = f"{area_type}_{filter_type}_{year}_{units}.csv"
    return cleaned_data_file_name