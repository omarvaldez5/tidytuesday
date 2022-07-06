# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
import pandas as pd
import janitor as jr
import valdezds as vds
import plotnine as p9

vds.getwd() # Confirm working directory

# Display set for terminal
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Read data
df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-03-15/cran.csv").clean_names()

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=9432).to_clipboard(index=False)

# EDA
df.info()
jr.get_dupes(df)
df.isnull().sum()


# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python
# ============================================================================ #

gg_data = (df.query("date.notnull() and date.str.contains('^[0-9][^a-zA-Z_]')")
           .deconcatenate_column("date", sep=" ", autoname="col")
           .query("package.str.contains('ggplot')")
           .rename_column(old_column_name="col1", new_column_name="new_date")
           .filter(["package", "new_date"])
           .to_datetime("new_date")
           )

gg_data["year"] = gg_data["new_date"].dt.year  # Add year column
gg_data = gg_data.groupby(["year"]).size().rename("n").reset_index() # GroupBy year


# ============================================================================ #
# 2.1.1 Save to CSV
gg_data.to_csv("2022/W11_cran/data_cran.csv")


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """
    SELECT
        *
    
    FROM df
    WHERE 1=1
        AND date IS NOT NULL
        AND LOWER(TRIM(package)) LIKE '%ggplot%'
        AND date REGEXP LIKE '^[0-9][^a-zA-Z_]'
    ;
    """

pysqldf(q)

# REGEXP
# (Background on this error at: https://sqlalche.me/e/14/e3q8)


# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# ============================================================================ #
# 3.1 Plotnine
# ============================================================================ #

(
    p9.ggplot(
        data=gg_data
    ) +
    
    # geoms
    p9.geom_point(p9.aes(x="year", y="n")) +
    p9.geom_line(p9.aes(x="year", y="n")) +
    
    # labs
    p9.labs(x="",
            y="Quantity",
            title="Number of versions released by year - ggplot2") +
     
    # theme
    p9.theme_minimal() +
    
    # watermark
    p9.watermark("./vdicon.png", xo=25, yo=15)
)


# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #

# Link:
# https://public.tableau.com/app/profile/omar.valdez/viz/TidyTuesdayW11_cran/Sheet1



# ============================================================================ #
# END
# ============================================================================ #
