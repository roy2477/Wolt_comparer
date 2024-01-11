from math import floor
import wolt_comparer as wc
import streamlit as st

st.set_page_config(
    page_title="Wolt Comparer", page_icon="💸", initial_sidebar_state="collapsed"
)
st.markdown("# Awesome Wolt Comparer 💸")

st.write("")
form = st.form(key="form_settings")
col1, col2, col3 = form.columns([3, 1, 1])

address = col1.text_input(
    "Location Address (עברית זה גם בסדר😄)",
    key="address",
    value="Tel Aviv"
)
product = col1.text_input(
    "Product to Search (עברית זה גם בסדר😄)",
    key="product",
)
only_open_now = col1.toggle(
    "Show Only Venues That Open Now",
    key="only_open_now",
    value=True
)

form.form_submit_button(label="Submit")

result_container = st.empty()
with st.spinner("Searching and comparing... (may take up to a minute)"):
    if address != '' and product != '':
        lat, lon = wc.get_lon_lat_from_address(address)
        product_name = product
        results, avg_price = wc.get_results(product_name, lat, lon, only_open_now)
        avg_price = floor(avg_price)
        row_size = 2
        if len(results) == 0:
            st.error('Sorry 😞 Product not found. Try another product name or address.')
        else:
            st.info(f'The Average Price is: :bold[{avg_price}]')
            grid = st.columns(row_size)
            col = 0
            for prod in results:
                with grid[col]:
                    try:
                        st.image(prod['image-path'], caption=prod["product_name"], use_column_width=True)
                    except AttributeError as e:
                        print(f'[!] Error in image processing: {str(e)}')
                        continue

                    if prod['price'] <= avg_price:
                        st.write(f'[{prod["venue"]}]({prod["link"]}) :green[{prod["price"]}]')
                    else:
                        st.write(f'[{prod["venue"]}]({prod["link"]}) :red[{prod["price"]}]')
                col = (col + 1) % row_size

st.markdown("---")
st.markdown(
    "Feel free to reach out, raise problems and connect on [Linkedin](https://www.linkedin.com/in/roy-elia/) 🙏🏻"
)
