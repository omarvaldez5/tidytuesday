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

# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #



# ============================================================================ #
# END
# ============================================================================ #
