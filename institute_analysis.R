############################################################
# INSTITUTE ANALYSIS PROJECT - FINAL WORKING CODE
############################################################

# -------------------------------
# 1. Install Packages (Run once)
# -------------------------------
install.packages("ggplot2")
install.packages("dplyr")
install.packages("readr")

# -------------------------------
# 2. Load Libraries
# -------------------------------
library(ggplot2)
library(dplyr)
library(readr)

# -------------------------------
# 3. Load Dataset
# -------------------------------
# CHANGE THIS PATH TO YOUR FILE LOCATION

institutes <- read.csv("V:/my-first-java-repo/institutes.csv",
                       stringsAsFactors = FALSE)

# Check dataset
print("Dataset Loaded:")
print(head(institutes))

# -------------------------------
# 4. Clean Column Names
# (Automatically removes spaces)
# -------------------------------
colnames(institutes) <- make.names(colnames(institutes))

print("Column Names:")
print(colnames(institutes))

# -------------------------------------------------
# IMPORTANT:
# Your CSV must contain columns similar to:
# Institute
# Teacher_Experience
# Infrastructure
# Placements
# Student_Reviews
# -------------------------------------------------

# Rename columns safely (edit if needed)
colnames(institutes) <- c(
  "Institute",
  "Teacher_Experience",
  "Infrastructure",
  "Placements",
  "Student_Reviews"
)

# -------------------------------
# 5. Data Cleaning
# -------------------------------
institutes <- na.omit(institutes)

institutes$Teacher_Experience <- as.numeric(institutes$Teacher_Experience)
institutes$Infrastructure <- as.numeric(institutes$Infrastructure)
institutes$Placements <- as.numeric(institutes$Placements)
institutes$Student_Reviews <- as.numeric(institutes$Student_Reviews)

# -------------------------------
# 6. Calculate Final Score
# -------------------------------
institutes <- institutes %>%
  mutate(
    Final_Score =
      (Teacher_Experience * 0.30) +
      (Infrastructure * 0.20) +
      (Placements * 0.30) +
      (Student_Reviews * 0.20)
  )

# -------------------------------
# 7. Assign Grades
# -------------------------------
institutes <- institutes %>%
  mutate(
    Grade = case_when(
      Final_Score >= 90 ~ "A+",
      Final_Score >= 80 ~ "A",
      Final_Score >= 70 ~ "B",
      Final_Score >= 60 ~ "C",
      TRUE ~ "D"
    )
  )

# -------------------------------
# 8. Sort by Score
# -------------------------------
institutes <- institutes %>%
  arrange(desc(Final_Score))

print("Final Analysis Table:")
print(institutes)

# -------------------------------
# 9. BAR CHART ANALYSIS (MAIN OUTPUT)
# -------------------------------
plot1 <- ggplot(institutes,
                aes(x = reorder(Institute, Final_Score),
                    y = Final_Score,
                    fill = Grade)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  labs(
    title = "Institute Performance Analysis",
    subtitle = "Based on Experience, Infrastructure, Placements & Reviews",
    x = "Institutes",
    y = "Final Score"
  ) +
  theme_minimal()

# FORCE DISPLAY GRAPH
print(plot1)

# -------------------------------
# 10. Save Chart as Image
# -------------------------------
ggsave("Institute_Analysis_BarChart.png",
       plot = plot1,
       width = 10,
       height = 6)

############################################################
# PROGRAM COMPLETED
############################################################