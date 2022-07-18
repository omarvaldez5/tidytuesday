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
import patchworklib as pw

vds.getwd() # Confirm working directory

# Display set for terminal
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Read data
df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-03-29/sports.csv").clean_names()

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=398).to_clipboard(index=False)

# EDA
df.info()
df.shape
df.isnull().sum()


# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python
# ============================================================================ #

# Filter men and women
men = (df.filter(["year", "rev_men", "exp_men"]).dropna()
       .groupby(["year"])
       .agg(revenue_men=("rev_men", "sum"),
            expenditure_men=("exp_men", "sum"))
       .reset_index()
       .pivot_longer(
            index="year",
            column_names=["revenue_men", "expenditure_men"],
            names_to="type",
            values_to="value"
        )
)

women = (df.filter(["year", "rev_women", "exp_women"]).dropna()
       .groupby(["year"])
       .agg(revenue_women=("rev_women", "sum"),
            expenditure_women=("exp_women", "sum"))
       .reset_index()
       .pivot_longer(
            index="year",
            column_names=["revenue_women", "expenditure_women"],
            names_to="type",
            values_to="value"
        )
)

# ============================================================================ #
# 2.1.1 Save to CSV
men.to_csv("2022/W13_collegiateSports/data_men.csv", index=False)
women.to_csv("2022/W13_collegiateSports/data.women.csv", index=False)


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """
    SELECT
        year
        , rev_men
        , exp_men
    
    FROM df
    WHERE 1=1
        AND year IS NOT NULL
        AND rev_men IS NOT NULL
        AND exp_men IS NOT NULL
    ;
    """

pysqldf(q)

# Not complete


# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# ============================================================================ #
# 3.1 Plotnine
# ============================================================================ #

p1 = (
    p9.ggplot(
        mapping=p9.aes(x="year", y="value", fill="type"),
        data=men
    ) +
    
    # geoms
    p9.geom_col(position="dodge") +
    p9.scale_fill_manual(["red", "blue"]) +
    
    # labs
    p9.labs(
        x="",
        y="",
        title="Revenue & Expenditure by Men in College Sports"
    ) +
    
    # theme
    p9.theme(
        figure_size=(10,6),
        subplots_adjust={'hspace': 0.25}
    )
)

p1.save("2022/W13_collegiateSports/plot.png")

p2 = (
    p9.ggplot(
        mapping=p9.aes(x="year", y="value", fill="type"),
        data=women
    ) +
    
    # geoms
    p9.geom_col(position="dodge") +
    p9.scale_fill_manual(["gray", "darkgreen"]) +
    
    # labs
    p9.labs(
        x="",
        y="",
        title="Revenue & Expenditure by Women in College Sports"
    ) +
    
    # theme
    p9.theme(
        figure_size=(10,6),
        subplots_adjust={'hspace': 0.25}
    )
)

p2.save("2022/W13_collegiateSports/plot2.png")

# Two plots, same figure
g1 = pw.load_ggplot(p1, figsize=(7,2))
g2 = pw.load_ggplot(p2, figsize=(7,2))

g12 = g1 / g2

# Error verify patchworklib

# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #

# Link
#

# ============================================================================ #
# END
# ============================================================================ #
