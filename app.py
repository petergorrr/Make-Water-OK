import pandas as pd
import plotly.express as px
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import streamlit as st
import folium


# Function to create the fuzzy system


def create_fuzzy_system():
    # Create input variables
    rainfall = ctrl.Antecedent(np.arange(0, 101, 1), 'rainfall')
    soil_saturation = ctrl.Antecedent(np.arange(0, 101, 1), 'soil_saturation')
    terrain_steepness = ctrl.Antecedent(
        np.arange(0, 101, 1), 'terrain_steepness')

    # Create output variable
    landslide_risk = ctrl.Consequent(np.arange(0, 101, 1), 'landslide_risk')

    # Define membership functions
    rainfall['low'] = fuzz.trimf(rainfall.universe, [0, 0, 50])
    rainfall['moderate'] = fuzz.trimf(rainfall.universe, [0, 50, 100])
    rainfall['high'] = fuzz.trimf(rainfall.universe, [50, 100, 100])

    soil_saturation['low'] = fuzz.trimf(soil_saturation.universe, [0, 0, 50])
    soil_saturation['medium'] = fuzz.trimf(
        soil_saturation.universe, [0, 50, 100])
    soil_saturation['high'] = fuzz.trimf(
        soil_saturation.universe, [50, 100, 100])

    terrain_steepness['gentle'] = fuzz.trimf(
        terrain_steepness.universe, [0, 0, 50])
    terrain_steepness['moderate'] = fuzz.trimf(
        terrain_steepness.universe, [0, 50, 100])
    terrain_steepness['steep'] = fuzz.trimf(
        terrain_steepness.universe, [50, 100, 100])

    landslide_risk['low'] = fuzz.trimf(landslide_risk.universe, [0, 0, 50])
    landslide_risk['moderate'] = fuzz.trimf(
        landslide_risk.universe, [0, 50, 100])
    landslide_risk['high'] = fuzz.trimf(
        landslide_risk.universe, [50, 100, 100])

    # Define rules
    rule1 = ctrl.Rule(antecedent=((rainfall['low'] & soil_saturation['low'])),
                      consequent=landslide_risk['low'])

    rule2 = ctrl.Rule(antecedent=((rainfall['high'] | soil_saturation['high'] | terrain_steepness['steep'])),
                      consequent=landslide_risk['high'])

    rule3 = ctrl.Rule(antecedent=((rainfall['moderate'] & soil_saturation['medium'])),
                      consequent=landslide_risk['moderate'])

    rule4 = ctrl.Rule(antecedent=(terrain_steepness['gentle']),
                      consequent=landslide_risk['low'])

    rule5 = ctrl.Rule(antecedent=((rainfall['high'] & terrain_steepness['moderate'])),
                      consequent=landslide_risk['moderate'])

    rule6 = ctrl.Rule(antecedent=((soil_saturation['high'] & terrain_steepness['gentle'])),
                      consequent=landslide_risk['moderate'])

    rule7 = ctrl.Rule(antecedent=((rainfall['moderate'] & terrain_steepness['steep'])),
                      consequent=landslide_risk['high'])

    # Create the control system
    return ctrl.ControlSystem(rules=[rule1, rule2, rule3, rule4, rule5, rule6, rule7])

# Function to calculate landslide risk


def calculate_landslide_risk(fuzzy_system, inputs):
    landslide_sim = ctrl.ControlSystemSimulation(fuzzy_system)
    landslide_sim.input['rainfall'] = inputs['rainfall']
    landslide_sim.input['soil_saturation'] = inputs['soil_saturation']
    landslide_sim.input['terrain_steepness'] = inputs['terrain_steepness']
    landslide_sim.compute()
    return landslide_sim.output['landslide_risk']

# Function to map risk to category


def map_risk_to_category(landslide_risk_result):
    if landslide_risk_result <= 30:
        return "Low Risk"
    elif 30 < landslide_risk_result <= 70:
        return "Moderate Risk"
    else:
        return "High Risk"

# Function to display landslide risk assessment interface


# Function to display landslide risk assessment interface
def display_landslide_risk_interface():
    st.title("Landslide Risk Assessment")

    # Sidebar for additional information
    st.sidebar.title("Environment Assessment Portal")
    st.sidebar.image("images/landslide.jpg", use_column_width=True)
    st.sidebar.info(
        "This app uses a fuzzy logic system to assess landslide risk based on input parameters. "
        "Adjust the parameters and click 'Calculate Risk' to see the results on the map."
    )

    # User Input: Latitude and Longitude
    st.header("Location Coordinates")
    latitude_longitude = st.text_input(
        "Enter Latitude and Longitude (comma-separated):", "5.4085,100.2773")
    latitude, longitude = map(float, latitude_longitude.split(','))

    # User Input: Fuzzy Logic Variables
    st.header("Landslide Risk Parameters")
    with st.expander("Input Parameters", expanded=True):
        rainfall_value = st.slider("Select Rainfall (0-100):", 0, 100, 50)
        saturation_value = st.slider(
            "Select Soil Saturation (0-100):", 0, 100, 50)
        steepness_value = st.slider(
            "Select Terrain Steepness (0-100):", 0, 100, 50)

    inputs = {
        'rainfall': float(rainfall_value),
        'soil_saturation': float(saturation_value),
        'terrain_steepness': float(steepness_value)
    }

    # Create and calculate fuzzy system
    fuzzy_system = create_fuzzy_system()

    if st.button("Calculate Risk"):
        landslide_risk_result = calculate_landslide_risk(fuzzy_system, inputs)
        risk_category = map_risk_to_category(landslide_risk_result)

        # Display the risk category
        st.success(
            f"Landslide Risk: {landslide_risk_result:.2f}% - Category: {risk_category}")

        # Display Map with Marker
        st.header("GIS Mapping")
        with st.expander("GIS Mapping", expanded=True):
            m = folium.Map(location=[latitude, longitude], zoom_start=10)

            # Choose marker color based on risk category
            marker_color = 'red' if risk_category == 'High Risk' else 'orange' if risk_category == 'Moderate Risk' else 'green'

            # Add Marker with Popup
            folium.Marker(
                location=[latitude, longitude],
                popup=f'Landslide Risk: {landslide_risk_result:.2f}%',
                icon=folium.Icon(color=marker_color)
            ).add_to(m)

            # Display Map
            st.write(m)


# Main function
def main():
    st.set_page_config(
        page_title="Environment Assessment Portal", page_icon="🌍")

    # Display welcome message
    st.title("Welcome to the Environment Assessment Portal")

    # Navigation bar
    st.sidebar.title("Navigation")
    selected_section = st.sidebar.radio(
        "", ["Landslide Risk Assessment"])

    # Display selected section
    if selected_section == "Landslide Risk Assessment":
        display_landslide_risk_interface()


if __name__ == "__main__":
    main()
