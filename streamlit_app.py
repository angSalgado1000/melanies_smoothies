import pandas as pd
import requests
import streamlit as st
from snowflake.snowpark.functions import col


# Display the app title and instructions
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)


# Ask for the customer's name
name_on_order = st.text_input("Name on Smoothie:")

st.write(
    "The name on your Smoothie will be:",
    name_on_order,
)


# Connect to Snowflake through Streamlit Community Cloud
connection = st.connection("snowflake")
session = connection.session()


# Get the fruit display names and API search values
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON"),
    )
)


# Convert the Snowpark dataframe to a Pandas dataframe
pd_df = my_dataframe.to_pandas()


# Create a list of fruit names for the multiselect
fruit_options = pd_df["FRUIT_NAME"].tolist()


# Let the user choose up to five fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5,
)


if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Find the API search value for the selected fruit
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON",
        ].iloc[0]

        st.write(
            "The search value for",
            fruit_chosen,
            "is",
            search_on,
            ".",
        )

        st.subheader(
            f"{fruit_chosen} Nutrition Information"
        )

        try:
            smoothiefroot_response = requests.get(
                "https://my.smoothiefroot.com/api/fruit/"
                + str(search_on),
                timeout=10,
            )

            smoothiefroot_response.raise_for_status()

            st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True,
            )

        except requests.exceptions.RequestException as error:
            st.error(
                f"Unable to retrieve nutrition information "
                f"for {fruit_chosen}: {error}"
            )


    # Submit the smoothie order
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
                    ingredients_string.strip(),
                    name_on_order.strip(),
                ],
            ).collect()

            st.success(
                f"Your Smoothie is ordered, "
                f"{name_on_order.strip()}!",
                icon="✅",
            )
