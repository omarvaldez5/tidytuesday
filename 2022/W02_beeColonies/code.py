# ============================================================================ #
# START
# ============================================================================ #


# ============================================================================ #
# 1.0 Load Packages and data

# Import libraries
import pandas as pd
from janitor import *
import valdezds as vds
from plotnine import *

# Read data
colony = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-11/colony.csv')
stressor = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-11/stressor.csv')

# Work with colony only, so store it in df variable
df = colony.copy()

# Quick EDA
df.info()
df.shape
df.isnull().sum()
vds.view_index(df)


# ============================================================================ #
# 2.0 Data Wrangling

# Top 10
state_tbl = (df.pipe(vds.select_by_number, 2, 5)
                .groupby(["state"])
                .agg(bee_mean = ("colony_lost", "mean"))
                .reset_index()
                .sort_values("bee_mean", ascending=False)
                .query("~state.str.contains('United States')")
                .head(10)
                .assign(state = lambda x: x["state"].astype("category"))
            )


# ============================================================================ #
# 3.0 Plot

(ggplot(state_tbl)
 + aes(x = "reorder(state, bee_mean)", y = "bee_mean")
 + geom_col(alpha = 0.8)
 + coord_flip()
 + watermark("./iconvaldezdata.png")
 + labs(
     x = "",
     y = "",
     title = "Mean Colony Lost - First time using plotnine"
 )
)

# Seems there's no captions or subtitles for plotnine

# ============================================================================ #
# END
# ============================================================================ #
