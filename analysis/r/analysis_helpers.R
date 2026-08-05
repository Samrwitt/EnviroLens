# EnviroLens epidemiological analysis helpers
# Requires: tidyverse, ggplot2, sf (optional)

suppressPackageStartupMessages({
  library(tidyverse)
})

#' Load exported analysis CSVs written by Python export step
load_exports <- function(dir = "analysis/r/exports") {
  list(
    risk = read_csv(file.path(dir, "risk_scores.csv"), show_col_types = FALSE),
    env = read_csv(file.path(dir, "environmental_pm25.csv"), show_col_types = FALSE),
    health = read_csv(file.path(dir, "health_resp.csv"), show_col_types = FALSE),
    dq = read_csv(file.path(dir, "data_quality.csv"), show_col_types = FALSE)
  )
}

describe_risk <- function(risk_df) {
  risk_df %>%
    group_by(risk_band) %>%
    summarise(n = n(), mean_score = mean(score, na.rm = TRUE), .groups = "drop")
}

correlate_pm_resp <- function(env_df, health_df) {
  joined <- env_df %>%
    inner_join(health_df, by = c("community_code", "period_code"))
  if (nrow(joined) < 3) return(NULL)
  cor.test(joined$mean_pm25, joined$mean_resp, use = "complete.obs")
}

simple_regression <- function(env_df, health_df) {
  joined <- env_df %>%
    inner_join(health_df, by = c("community_code", "period_code"))
  if (nrow(joined) < 5) return(NULL)
  lm(mean_resp ~ mean_pm25, data = joined)
}

missing_summary <- function(df) {
  tibble(
    column = names(df),
    missing = map_dbl(df, ~ mean(is.na(.x)))
  ) %>% arrange(desc(missing))
}
