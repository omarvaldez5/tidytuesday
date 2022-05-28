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
df = pd.read_csv("2022/W07_duBois/data.csv").clean_names()

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=49).to_clipboard(index=False)

# Quick EDA
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

# Getting united states geographical data
us_states_geo = gp.read_file("https://raw.githubusercontent.com/sunny2309/datasets/master/us-states.json")
us_states_geo.to_clipboard()

# Join
us_map = pd.merge(us_states_geo, df, how="left", left_on="id", right_on="state")
us_map.to_clipboard()

# ============================================================================ #
# 2.1.1 Save to CSV
us_map.to_csv("2022/W07_duBois/data_duBios.csv", index=False)


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """
    ;
    """

pysqldf(q)


# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# ============================================================================ #
# 3.1 Plotnine
# ============================================================================ #

(
    p9.ggplot() +
    p9.geom_map(data=us_map, mapping=p9.aes(fill="population", color="population")) +
    # p9.guides(fill=p9.guide_legend(title="", ncol=2)) +
    p9.xlim(-170, -60) +
    p9.ylim(25, 72) +
    p9.theme_void() +
    p9.theme(
        subplots_adjust={'hspace': 0.25},
        figure_size=(10,6),
        legend_position="top",
        plot_title=p9.element_text(face="bold", size=15),
        plot_background=p9.element_rect(fill="#E2D0BF"),
    )
)

# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #

# Link:

# ============================================================================ #
# END
# ============================================================================ #
