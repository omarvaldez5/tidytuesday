# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
import pandas as pd
import janitor as jr
import valdezds as vds
import plotnine as gg

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
    gg.ggplot(
        mapping=gg.aes(x="year", y="value", fill="type"),
        data=men
    ) +
    
    # geoms
    gg.geom_col(position="dodge") +
    gg.scale_fill_manual(["red", "blue"]) +
    
    # labs
    gg.labs(
        x="",
        y="",
        title="Revenue & Expenditure by Men in College Sports"
    ) +
    
    # theme
    gg.theme(
        figure_size=(10,6),
        subplots_adjust={'hspace': 0.25}
    )
)

p1.save("2022/W13_collegiateSports/plot1.png")

p2 = (
    gg.ggplot(
        mapping=gg.aes(x="year", y="value", fill="type"),
        data=women
    ) +
    
    # geoms
    gg.geom_col(position="dodge") +
    gg.scale_fill_manual(["gray", "darkgreen"]) +
    
    # labs
    gg.labs(
        x="",
        y="",
        title="Revenue & Expenditure by Women in College Sports"
    ) +
    
    # theme
    gg.theme(
        figure_size=(10,6),
        subplots_adjust={'hspace': 0.25}
    )
)

p2.save("2022/W13_collegiateSports/plot2.png")

# ============================================================================ #
# 3.2 Work Around Images

# From:
# https://stackoverflow.com/questions/52331622/plotnine-any-work-around-to-have-two-plots-in-the-same-figure-and-print-it

import matplotlib.pyplot as plt
import matplotlib.image as img
import os
import numpy as np

def check_plotnine_grid(plots_list, figsize):
    if not type(plots_list) == list:
        raise ValueError('Input plots_list is not a list')
    if (not type(figsize) == tuple) or (not len(figsize) == 2):
        raise ValueError('Input figsize should be a tuple of length 2')


def plotnine_grid(plots_list, row=None, col=1, height=None, width=None, dpi=500, ratio=None, pixels=10000,
                  figsize=(12, 8)):

    """
    Create a grid of plotnine plots.


    Function input
    ----------
    plots_list      : a list of plotnine.ggplots
    row, col        : numerics to indicate in how many rows and columns the plots should be ordered in the grid
                defaults: row -> length of plots_list; col -> 1
    height, width   : the height and width of the individual subplots created by plotnine
                    can be automatically determined by a combination of dpi, ratio and pixels
    dpi             : the density of pixels in the image. Default: 500. Higher numbers could lead to crisper output,
                    depending on exact situation
    ratio           : the ratio of heigth to width in the output. Standard value is 1.5 x col/row.
                    Not used if height & width are given.
    pixels          : the total number of pixels used, default 10000. Not used if height & width are given.
    figsize         : tuple containing the size of the final output after making a grid, in pixels (default: (1200,800))



    Function output
    ----------
    A matplotlib figure that can be directly saved with output.savefig().
    """

    check_plotnine_grid(plots_list, figsize)  # Check the input

    # Assign values that have not been provided based on others. In the end, height and width should be provided.
    if row is None:
        row = len(plots_list)

    if ratio is None:
        ratio = 1.5 * col / row

    if height is None and width is not None:
        height = ratio * width

    if height is not None and width is None:
        width = height / ratio

    if height is None and width is None:
        area = pixels / dpi
        width = np.sqrt(area/ratio)
        height = ratio * width

    # Do actual subplot creation and plot output.
    i = 1
    fig = plt.figure(figsize=figsize)
    plt.autoscale(tight=True)
    for image_sel in plots_list:  # image_sel = plots_list[i]
        image_sel.save('image' + str(i) + '.png', height=height, width=width, dpi=500, verbose=False)
    fig.add_subplot(row, col, i)
    plt.imshow(img.imread('image' + str(i) + '.png'), aspect='auto')
    fig.tight_layout()
    fig.get_axes()[i-1].axis('off')
    i = i + 1
    os.unlink('image' + str(i - 1) + '.png')  # os.unlink is basically os.remove but in some cases quicker
    fig.patch.set_visible(False)
    
    return fig


# Use function
plot_list = [p1, p2]
grid_plots = plotnine_grid(plot_list, row=2, figsize=(40, 28))
grid_plots.savefig("2022/W13_collegiateSports/plot.png")

# Not completely working, need to figure out

# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #

# Link
#

# ============================================================================ #
# END
# ============================================================================ #
