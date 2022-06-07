# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
from matplotlib.pyplot import subplots_adjust
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
df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-02-22/freedom.csv").clean_names()

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=123).to_clipboard(index=False)

# EDA
df.info()
df.isnull().sum()
df.shape
jr.get_dupes(df)

# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python
# ============================================================================ #

# Get geometry
world_filepath = gp.datasets.get_path("naturalearth_lowres")
world = gp.read_file(world_filepath)

# Dataset
data_world = (df.query("year == 2020")
              .select_columns(["country", "status", "region_name"])
              .case_when(
    df.status == "F", "Free",
    df.status == "PF", "Partially Free",
    df.status == "NF", "Not Free",
    "N/A",
    column_name="status"
    )
    .query("region_name != 'Antarctica'")
    .merge(world, left_on="country", right_on="name")
)

# ============================================================================ #
# 2.1.1 Save to CSV
data_world.to_csv("2022/W08_freedom/data_freedom.csv")


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """
    SELECT
        country
        , CASE
            WHEN status = 'F' THEN 'Free'
            WHEN status = 'PF' THEN 'Partially Free'
            WHEN status = 'NF' THEN 'Not Free'
            ELSE NULL
            END AS status
        , region_name
    
    FROM df d
    INNER JOIN world
        ON d.country = w.name
    ;
    """

pysqldf(q)

# Error: https://docs.sqlalchemy.org/en/14/errors.html#error-rvf5

# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# ============================================================================ #
# 3.1 Plotnine
# ============================================================================ #

(
    p9.ggplot() +

    # geoms
    p9.geom_map(data=data_world,
                mapping=p9.aes(fill="status")) +
    p9.scale_fill_manual(values=["#61bb18", "#ff7e5e", "#fffd6e"]) +

    # labs
    p9.labs(x="", y="",
            title="Freedom in 2020") +

    # theme
    p9.theme_void() +
    p9.theme(
        subplots_adjust={'hspace': 0.25},
        figure_size=(10, 6),
        legend_position="bottom",
        legend_text=p9.element_text(face="bold", color="#8d7d7d"),
        legend_title=p9.element_text(face="bold", color="#8d7d7d"),
        axis_title=p9.element_blank(),
        panel_grid_minor=p9.element_blank(),
        panel_grid_major_y=p9.element_blank(),
        panel_grid_major_x=p9.element_blank(),
        panel_background=p9.element_rect(fill="#fdf9f3"),
        plot_background=p9.element_rect(fill="#fdf9f3"),
        plot_title=p9.element_text(color="#8d7d7d", face="bold", size=15),
        axis_text_x=p9.element_blank(),
        axis_text_y=p9.element_blank()
    ) +
    
    # watermark
    p9.watermark("./vdicon.png", xo=25, yo=15)
)

# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #

# Link:
# https://public.tableau.com/app/profile/omar.valdez/viz/TidyTuesdayW08_freedom/Sheet1

# ============================================================================ #
# END
# ============================================================================ #
