import streamlit as st

# --- Constants ---
LITRES_PER_GALLON = 4.54609

# --- Default Assumptions (Based on provided table initially, now budget focused) ---
# These are fixed assumptions for the calculation
DEFAULT_PARAMS = {
    "Small Van": {
        "mpg_std": 54.3, "mpg_under": 51.0,
        "tyre_cost_std": 240.0, "tyre_cost_under": 283.2 # Budget Estimate
    },
    "Medium Van": {
        "mpg_std": 44.8, "mpg_under": 42.1,
        "tyre_cost_std": 320.0, "tyre_cost_under": 377.6 # Budget Estimate
    },
    "Large Van": {
        "mpg_std": 40.9, "mpg_under": 38.4,
        "tyre_cost_std": 380.0, "tyre_cost_under": 448.4 # Budget Estimate
    },
    "Long Wheelbase Van": {
        "mpg_std": 32.5, "mpg_under": 30.6,
        "tyre_cost_std": 380.0, "tyre_cost_under": 448.4 # Budget Estimate (Same as Large)
    }
}
DEFAULT_TYRE_LIFESPAN_MILES = 20000 # Fixed assumption

# --- Helper Functions ---
def calculate_extra_fuel_cost_10k(mpg_std, mpg_under, price_per_litre):
    """Calculates the extra fuel cost per 10,000 miles due to underinflation."""
    if mpg_std <= 0 or mpg_under <= 0 or price_per_litre <= 0:
        return 0
    gallons_std = 10000 / mpg_std
    gallons_under = 10000 / mpg_under
    cost_std = gallons_std * LITRES_PER_GALLON * price_per_litre
    cost_under = gallons_under * LITRES_PER_GALLON * price_per_litre
    return cost_under - cost_std

def calculate_extra_tyre_cost_10k(tyre_cost_std, tyre_cost_under, lifespan_miles):
    """Calculates the extra tyre cost per 10,000 miles due to faster wear."""
    if lifespan_miles <= 0:
        return 0
    cost_diff_lifespan = tyre_cost_under - tyre_cost_std
    # Assume lifespan is for standard tyres, underinflated wear faster
    return cost_diff_lifespan / (lifespan_miles / 10000)

# --- Streamlit App Layout ---
st.set_page_config(page_title="Fleet Savings Calculator", layout="wide")
st.title("🚚 Fleet Tyre Maintenance Savings Calculator")

st.markdown("""
Estimate the potential annual savings for your fleet by maintaining correct tyre pressures.
Underinflated tyres lead to increased fuel consumption and faster tyre wear.
Enter your fleet details and the current diesel price below.
""")

# --- User Inputs ---
st.header("Configuration")
user_diesel_price = st.number_input(
    "Current Diesel Price (£/litre):",
    min_value=0.10,
    value=1.51, # Updated default slightly
    step=0.01,
    format="%.2f",
    key="diesel_price",
    help="Enter the current average price you pay for diesel."
)

# --- REMOVED Advanced Assumptions Expander --- 
# Calculations now use fixed DEFAULT_PARAMS and DEFAULT_TYRE_LIFESPAN_MILES

st.divider() # Adds a visual separator

# --- Fleet Input Section ---
st.header("Fleet Composition & Mileage")
st.markdown("Enter the details for each van type in your fleet:")

total_fleet_savings = 0
fleet_input_cols = st.columns(2) # Create two columns for layout

# Store calculated savings per 10k miles for summary display later
savings_per_10k_summary = {}

# Function to process each van type using fixed defaults
def process_van_type(van_type_name, diesel_price, column):
    # Use fixed defaults directly
    params = DEFAULT_PARAMS[van_type_name]
    tyre_lifespan = DEFAULT_TYRE_LIFESPAN_MILES

    with column:
        st.subheader(f"{van_type_name}s") # Pluralize
        key_prefix = van_type_name.lower().replace(" ", "_").replace("wheelbase", "wb") # e.g., "small_van", "lwb_van"

        count = st.number_input(f"Number of {van_type_name}s:", min_value=0, step=1, key=f"{key_prefix}_count")
        miles = st.number_input(f"Average Annual Mileage ({van_type_name}s):", min_value=0, step=1000, key=f"{key_prefix}_miles", value=10000 if 'Small' in van_type_name else 12000 if 'Medium' in van_type_name else 15000 if 'Large' in van_type_name else 20000) # Default mileages

        if count > 0 and miles > 0:
            extra_fuel_cost = calculate_extra_fuel_cost_10k(params["mpg_std"], params["mpg_under"], diesel_price)
            extra_tyre_cost = calculate_extra_tyre_cost_10k(params["tyre_cost_std"], params["tyre_cost_under"], tyre_lifespan)
            total_extra_cost_10k = extra_fuel_cost + extra_tyre_cost
            savings_per_10k_summary[van_type_name] = total_extra_cost_10k # Store for summary

            annual_savings = (miles / 10000) * total_extra_cost_10k * count
            st.write(f"Est. Annual Savings ({van_type_name}s): **£{annual_savings:,.2f}**")
            st.caption(f"(Based on £{total_extra_cost_10k:,.2f} saving per 10k miles)")
            return annual_savings
        else:
            st.write("Enter count and mileage to calculate savings.")
            savings_per_10k_summary[van_type_name] = 0 # Ensure key exists
            return 0

# Process each van type - calls updated
total_fleet_savings += process_van_type("Small Van", user_diesel_price, fleet_input_cols[0])
total_fleet_savings += process_van_type("Large Van", user_diesel_price, fleet_input_cols[0])
total_fleet_savings += process_van_type("Medium Van", user_diesel_price, fleet_input_cols[1])
total_fleet_savings += process_van_type("Long Wheelbase Van", user_diesel_price, fleet_input_cols[1])


st.divider()

# --- Results Section ---
st.header("Total Estimated Annual Savings")

if total_fleet_savings > 0:
    st.metric(label="Total Potential Savings Across Your Fleet", value=f"£{total_fleet_savings:,.2f}")

    # Summary of savings per 10k miles based on current inputs
    summary_text = "*(Calculated savings per 10,000 miles based on default assumptions: "
    summary_items = []
    for van_type, saving in savings_per_10k_summary.items():
         if saving > 0: # Only show if calculation resulted in saving
             summary_items.append(f"{van_type}: £{saving:,.2f}")
    summary_text += "; ".join(summary_items) + ")*"


    st.success(f"""
    Based on your input and the default calculation assumptions, maintaining correct tyre pressures could save your fleet an estimated **£{total_fleet_savings:,.2f}** per year
    in reduced fuel and tyre replacement costs.
    
{summary_text}
    """)
    st.markdown("Consider how this compares to the cost of a regular tyre maintenance service!")
else:
    st.info("Enter your fleet details above to calculate potential savings.")

st.markdown("---")
st.caption(f"""Disclaimer: This calculator provides an estimate based on default average data (MPG difference, budget tyre costs, {DEFAULT_TYRE_LIFESPAN_MILES:,} mile tyre lifespan). 
Actual savings may vary depending on specific driving conditions, vehicle maintenance, actual tyre type/cost, and fuel prices.""")