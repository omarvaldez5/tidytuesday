# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load Packages and data

# Import libraries
import pandas as pd
import janitor as jr
import valdezds as vds
import plotnine as p9

# Read data
chocolate = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-18/chocolate.csv')

# Make copy and clean names from janitor package
df = chocolate.copy()
df = df.clean_names()

# Quick EDA
df.info()
df.shape
df.isnull().sum()
vds.view_index(df)

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=1).to_clipboard(index=False)


# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python


# Bean origin with count and average percent
dta_pct = (df
           .assign(cocoa_percent = lambda x: x["cocoa_percent"].str.strip("%").astype(float))
           .groupby(["country_of_bean_origin"])
           .agg(
               n_count = ("ref", "count"),
               avg_pct = ("cocoa_percent", "mean")
           )
           .reset_index()
           .sort_values("n_count", ascending=False)
        )

# Save to csv (Tableau)
dta_pct.to_csv("2022/W03_chocolate/data_chocolate.csv", index=False)

# ============================================================================ #
# 2.2 SQL

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """    
    SELECT
        country_of_bean_origin
        , COUNT(ref) AS n_count
        , AVG(REPLACE(cocoa_percent, '%', '')) AS cocoa_percent
    
    FROM df
        GROUP BY 1
        ORDER BY n_count DESC
    ;
    """

pysqldf(q)


# ============================================================================ #
# 3.0 Plot

# Source heatmap in plotnine:
# https://stackoverflow.com/questions/64410412/hourly-heatmap-graph-using-python-s-ggplot2-implementation-plotnine

# Heatmap
(p9.ggplot(dta_pct)
 + p9.aes(x = "n_count", y = "country_of_bean_origin", fill = "avg_pct")
 + p9.geom_tile(stat = "identity")
 + p9.watermark("./vdicon.png", xo=25, yo=15)
)

# No geom_treemap available (Package treemapify in R)

# Tableau:
# https://public.tableau.com/views/TidyTuesdayW03_chocolate/W03_chocolate?:language=en-US&:display_count=n&:origin=viz_share_link

# ============================================================================ #
# END
# ============================================================================ #

