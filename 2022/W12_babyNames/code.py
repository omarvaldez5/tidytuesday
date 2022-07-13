# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
import pandas as pd
import janitor as jr
import valdezds as vds
import numpy as np
import plydata.cat_tools as cat
import plotnine as p9

vds.getwd() # Confirm working directory

# Display set for terminal
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Read data
df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-03-22/babynames.csv").clean_names()

# EDA
df.info()
df.shape
df.isnull().sum()
df.pipe(vds.select_by_number, 1, 2).describe()

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=182).to_clipboard(index=False)
df.sample(frac=0.25).to_clipboard(index=False)


# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python
# ============================================================================ #
top_decades = (df.assign(decade=lambda x: 10 * np.floor(x["year"]/10))
               .assign(decade=lambda x: x["decade"].astype(str) + "s")
               .groupby(["decade"])["name"]
               .size()
               .rename("count")
               .reset_index()
               .sort_values("count", ascending=False)
               .sort_values("decade", ascending=True)
               .assign(decade=lambda x: cat.cat_inorder(x["decade"]))
               )

# ============================================================================ #
# 2.1.1 Save to CSV
top_decades.to_csv("2022/W12_babyNames/data_topDecades.csv", index=False)


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """
    SELECT
        10 * FLOOR(year/10) || 's' AS decade
        , COUNT(*) AS count
    
    FROM df
    GROUP BY 1
    ORDER BY decade ASC
    ;
    """
    
pysqldf(q)


# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# ============================================================================ #
# 3.1 Plotnine
# ============================================================================ #

plot = (
    p9.ggplot(
        mapping=p9.aes(x="decade", y="count"),
        data=top_decades
    ) +

    # geoms
    p9.geom_col(
        position="dodge",
        width=0.3,
        alpha=0.8
    ) +

    # labs
    p9.labs(
        x="Decade",
        y="Count",
        title="Total Count of baby names by decade"
    ) +

    # theme
    p9.theme(
        figure_size=(10, 6),
        subplots_adjust={'hspace': 0.25},
        axis_text_x=p9.element_text(angle=90, hjust=1)
    )
)

# Save image
plot.save(filename="2022/W12_babyNames/plot.png")


# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #

# Link:
# https://public.tableau.com/app/profile/omar.valdez/viz/TidyTuesdayW12_babyNames/Sheet1

# ============================================================================ #
# END
# ============================================================================ #
