# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
import pandas as pd
import janitor as jr
import valdezds as vds
import geopandas as gp
import plotnine as p9

vds.getwd() # Confirm working directory

# Display set for terminal
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Read data
df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-02-08/airmen.csv").clean_names()

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=283).to_clipboard(index=False)

# Quick EDA
df.info()
df.isnull().sum()
df.shape
vds.select_by_number(df, 3, 7, 5, 14).describe()


# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# Plotnine info map:
# https://plotnine.readthedocs.io/en/stable/generated/plotnine.geoms.geom_map.html

# Installation geopandas
# https://geopandas.org/en/stable/getting_started/install.html

# Intro
# https://geopandas.org/en/stable/getting_started/introduction.html

# ============================================================================ #
# 2.1 Python
# ============================================================================ #

# https://towardsdatascience.com/interactive-geographical-maps-with-geopandas-4586a9d7cc10
# https://geopandas.org/en/stable/docs/user_guide/mapping.html
# https://coderzcolumn.com/tutorials/data-science/maps-using-plotnine-choropleth-scatter-bubble-maps

# Example World data
world_filepath = gp.datasets.get_path("naturalearth_lowres")
world = gp.read_file(world_filepath)
world.to_clipboard()
united_states = world.query("iso_a3 == 'USA'")  # USA filter

# Getting united states geographical data from another source
us_states_geo = gp.read_file("https://raw.githubusercontent.com/sunny2309/datasets/master/us-states.json")
us_states_geo.to_clipboard()

# Join
us_map = pd.merge(us_states_geo, df, how="left", left_on="id", right_on="state")

# Total count
size_count = (us_map.pipe(vds.select_by_number, 10, 12)
              .groupby(["state"])
              .size()
              .to_frame("n_size")
              .reset_index()
              .sort_values("n_size", ascending=False)
              )

# Merge with main data
us_count = pd.merge(us_map, size_count, how="left", on="state")


# ============================================================================ #
# 2.1.1 Save to CSV
us_count.to_csv("2022/W06_tuskegee/data_tuskgee.csv", index=False)


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """
    SELECT * FROM us_map
    ;
    """

pysqldf(q)

# Error: https://docs.sqlalchemy.org/en/14/errors.html#error-rvf5
# Search

# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# ============================================================================ #
# 3.1 Plotnine
# ============================================================================ #

# Geom Map

(
    p9.ggplot() +
    
    # geoms
    p9.geom_map(data=us_count, mapping=p9.aes(fill="n_size", color="n_size")) +
    p9.scale_fill_cmap(cmap_name="RdYlBu") +
    p9.scale_color_cmap(cmap_name="RdYlBu") +
    p9.xlim(-170, -60) +
    p9.ylim(25, 72) +
    
    # labs
    p9.labs(x="",
            y="",
            title="Tuskegee Airmen - Qty Pilot Types from U.S.A") +
    
    # theme
    p9.theme(
        subplots_adjust={'hspace': 0.25},
        figure_size=(10,6),
        panel_background=p9.element_rect(fill="snow"),
        legend_title=p9.element_text(face="bold"),
        legend_text=p9.element_text(face="italic"),
        plot_title=p9.element_text(face="bold", size=15),
        axis_text_x=p9.element_blank(),
        axis_text_y=p9.element_blank(),
        axis_ticks_major_x=p9.element_blank(),
        axis_ticks_major_y=p9.element_blank()
    ) +
    
    # watermark
    p9.watermark("./iconvaldezdata.png")
)

# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #



# ============================================================================ #
# END
# ============================================================================ #
