import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("""
Choose the fruits you want in your custom Smoothie!
""")

name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake from Streamlit Community Cloud
connection = st.connection("snowflake")
session = connection.session()

# Get fruit names
fruit_rows = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
    .collect()
)

fruit_options = [row["FRUIT_NAME"] for row in fruit_rows]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        if not name_on_order.strip():
            st.warning("Please enter a name for the order.")
        else:
            session.sql(
                """
                INSERT INTO SMOOTHIES.PUBLIC.ORDERS
                (INGREDIENTS, NAME_ON_ORDER)
                VALUES (?, ?)
                """,
                params=[
                    ingredients_string,
                    name_on_order.strip()
                ]
            ).collect()

            st.success(
                f"Your Smoothie is ordered, {name_on_order.strip()}!",
                icon="✅"
            )
# Call the SmoothieFroot API
try:
    smoothiefroot_response = requests.get(
        "https://my.smoothiefroot.com/api/fruit/watermelon",
        timeout=10
    )

    smoothiefroot_response.raise_for_status()

    smoothiefroot_data = smoothiefroot_response.json()

    st.subheader("SmoothieFroot Nutrition Information")
    st.write(smoothiefroot_data)
    st.dataframe(smoothiefroot_data)

except requests.exceptions.RequestException as error:
    st.error(f"Unable to retrieve fruit information: {error}")
