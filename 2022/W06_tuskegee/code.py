# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
import pandas as pd
import janitor as jr
import valdezds as vds

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


# ============================================================================ #
# 2.1.1 Save to CSV


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

# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #



# ============================================================================ #
# END
# ============================================================================ #
