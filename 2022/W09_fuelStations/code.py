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
df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-03-01/stations.csv").clean_names()

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=4938).to_clipboard(index=False)

# EDA
df.info()
df.isnull().sum()
df.shape
jr.get_dupes(df)
vds.select_by_number(df, 3, 4, 7, 8, 12).describe()

# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python
# ============================================================================ #

fuel_data = (df.query("country == 'US'")
            .query("access_code == 'public'")
            .select_columns(["status_code", "facility_type"])
            .case_when(
                df.status_code == "E", "Available",
                df.status_code == "P", "Planned",
                df.status_code == "T", "Temporarily Unavailable",
                "N/A",
                column_name="status_code"
            )
            .query("status_code == 'Temporarily Unavailable'")
            .groupby(["status_code", "facility_type"])
            .size()
            .to_frame("n_size")
            .reset_index()
            .sort_values("n_size", ascending=False)
            .head(15)
            .assign(facility_type = lambda x: x["facility_type"].str.lower())
            .assign(facility_type = lambda x: x["facility_type"].str.replace("_", " "))
)

# ============================================================================ #
# 2.1.1 Save to CSV
fuel_data.to_csv("2022/W09_fuelStations/data_fuelStations.csv")


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """
    
    /* Filtering data */
    
    WITH cte_data AS
    (
        SELECT
        CASE
            WHEN status_code = 'E' THEN 'Available'
            WHEN status_code = 'P' THEN 'Planned'
            WHEN status_code = 'T' THEN 'Temporarily Unavailable'
            ELSE 'N/A'
            END AS status_code
        , facility_type
    
    FROM df
    WHERE 1=1
        AND country = 'US'
        AND access_code = 'public'
    )
    
    /* Was trying to filter 'Temporarily Unavailable' in cte */
    /* but it was returning an empty data frame. Dividing this in two steps */
    
    , cte_basepop AS
    (
        SELECT *
        
        FROM cte_data
        WHERE 1=1
            AND status_code = 'Temporarily Unavailable'
    )
    
    /* Count number of facilities */
    
    SELECT
        status_code
        , LOWER(REPLACE(facility_type, '_', ' ')) AS facility_type
        , COUNT(*) AS n_size
    
    FROM cte_basepop
    GROUP BY 1, 2
    ORDER BY n_size DESC
    LIMIT 15
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
