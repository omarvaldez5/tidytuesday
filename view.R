# ============================================================================ #
# START
# ============================================================================ #

# Packages
library(readr)
library(skimr)

# Read data
colony <- readr::read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-11/colony.csv')
stressor <- readr::read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-11/stressor.csv')

View(colony)
View(stressor)


# Skim
skimr::skim(colony)
skimr::skim(stressor)

# ============================================================================ #
# END
# ============================================================================ #
