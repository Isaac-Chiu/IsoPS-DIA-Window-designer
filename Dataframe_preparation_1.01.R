library(tidyverse)


setwd("your_workplace")
getwd()

df_raw <- read_delim(file = "./your_skyline_output_file.csv")

df_raw

df <- df_raw %>% 
        mutate(MZ = as.numeric(sub("^(\\d+\\.\\d+).*", "\\1", Precursor))) %>% 
        mutate(Types = ifelse(grepl("(heavy)", Precursor), "Heavy", "Light")) %>% 
        select(Name = Peptide, MZ, Types, Charge = `Precursor Charge`, RT = `Peptide Retention Time`) %>% 
        mutate(MZp1 = MZ + (1 / Charge),
               MZp2 = MZ + (1 / Charge) * 2) %>%
        group_by(Name) %>%
        mutate(
                has_pair = n() == 2,
                min_MZ = min(MZ)  # Identify the smallest MZ in the group
        ) %>%
        ungroup() %>%
        arrange(min_MZ) %>%  # Order groups by their smallest MZ
        mutate(
                pair_number = if_else(has_pair, 
                                      paste0("pair_", dense_rank(min_MZ)),
                                      NA_character_)
        ) %>%
        select(-min_MZ)  # Drop the temporary column if not needed

Window_df <- df %>% 
        mutate(Win_start = round((MZ - 0.5), 1))

# Create the hybrid plot
ggplot(Window_df, aes(color = pair_number)) +
        # Add points for MZ, MZp1, and MZp2
        geom_point(aes(x = MZ, y = RT), size = 3, shape = 16) +
        geom_point(aes(x = MZp1, y = RT), size = 3, shape = 17) +
        geom_point(aes(x = MZp2, y = RT), size = 3, shape = 18) +
        # Add vertical lines for Win_start
        geom_vline(aes(xintercept = Win_start), linetype = "dashed") +
        # Set axis limits
        xlim(300, 1000) +
        # Set axis labels and title
        labs(
                x = "MZ and Win_start",
                y = "Retention Time (RT)",
                color = "Pair Number",
                title = "Hybrid Plot with Points and Vertical Lines"
        ) +
        # Customize the theme
        theme_minimal() +
        theme(
                legend.position = "right",
                plot.title = element_text(hjust = 0.5, face = "bold")
        )

write.csv(Window_df,"win_df_1.csv", row.names = FALSE)
