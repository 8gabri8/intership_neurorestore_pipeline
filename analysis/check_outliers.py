import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


"""
This script is used to manage the outliers in the final csv file.

Strategy:
1) Check if any otliers is present
2) Change its value with a specific valu
"""

##############################################
### MANDATORY INPUTS #########################
##############################################

# path big csv
path_csv = "/home/gabri/Downloads/all_brains.csv"
#thr_z_score over which a ROI is considered an outlier
thr_z_score = 4

df_original = pd.read_csv(path_csv)
df = df_original.copy()

# ATTENTION: just for now slect only real data
df = df[df["TimePoint"] == "Uninjured"]
# ATTENTION: just for now slect only leaf
df = df[df["IsLeaf"] == True]

##############################################
### SEARCH OUTLIERS ##########################
##############################################

##########################
### DENSITY VALUES

# Calculate z-score
mean = np.mean(df["Cell Density"])
std = np.std(df["Cell Density"])
df["z-score"] = ( df["Cell Density"] - mean ) / std
out = df[np.abs(df["z-score"]) > thr_z_score][["ROI", "Brain ID", "z-score"]]
out = out.sort_values(by="z-score")
print(f"\n\nOutliers based on |z-score| > {thr_z_score} (tot={len(out)}): \n {out.to_string()} \n Unique regions {out['ROI'].unique()}")

fig, ax = plt.subplots(figsize=(20, 6))
ax.bar(x = range(len(df["z-score"])), height=df["z-score"])
plt.title("Z-score")


# Scatter Plot Synapses Vs Area
fig, ax = plt.subplots(figsize=(20, 6))
sns.scatterplot(x='Area', y='Synapses', data=df, hue='Cell Density', palette='viridis', size='Cell Density', sizes=(50, 200))
ax.set_title('Synapses vs Area')
ax.set_xlabel('Area')
ax.set_ylabel('Synapses')
ax.grid(True)
ax.set_xscale('log')
ax.set_yscale('log')


## Scatter Plot Synapses Vs Area --> With Names
fig, ax = plt.subplots(figsize=(10, 6))
scatter = sns.scatterplot(
    x='Area', y='Synapses', data=df, hue='Cell Density', palette='viridis', size='Cell Density', sizes=(50, 200)
)
ax.set_title('Synapses vs Area')
ax.set_xlabel('Area')
ax.set_ylabel('Synapses')
ax.grid(True)
ax.set_xscale('log')
ax.set_yscale('log')

# Label each point with 'ROI-Brain ID'
for i, row in df.iterrows():
    label = f"{row['ROI']}-{row['Brain ID']}"  # Construct the label text
    ax.text(
        row['Area'],  # X coordinate
        row['Synapses'],  # Y coordinate
        label,  # Text label
        fontsize=9,  # Font size of the label
        ha='right',  # Horizontal alignment
        va='bottom',  # Vertical alignment
        color='black'  # Text color
    )

# Show the plot
plt.show()


# Using Quartiles --> not very usefule as I have only few samples (even 2)
Q1 = df['Cell Density'].quantile(0.25)
Q3 = df['Cell Density'].quantile(0.75)
IQR = Q3 - Q1
# Define outlier thresholds
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
outliers = df[(df['Cell Density'] < lower_bound) | (df['Cell Density'] > upper_bound)] # Identify outliers

print("\n\nOutliers Density based on quartiles:")
print(outliers)

##########################
### SYNAPSES COUNTS

# In this case, because we do not normalize by the are as in density, we can only fidn outliers within the SAME ROI

# Function to calculate Z-scores and identify outliers
def find_outliers_z_score(group, threshold=thr_z_score):
    mean = group['Synapses'].mean()
    std = group['Synapses'].std()
    group['z-score'] = (group['Synapses'] - mean) / std
    return group[np.abs(group['z-score']) > threshold]

# Group by ROI and apply the outlier detection function
outliers = df.groupby('ROI').apply(find_outliers_z_score).reset_index(drop=True)

# Display the outliers
print(f"\n\nOutliers Synapses count within each ROI based on Z-score (tot={len(outliers)}):")
print(outliers)


##############################################
### MANAGE OUTLIERS ##########################
##############################################

# Write down the outliers
roi_out = ["Left: ISN"],
brainID_out = ["589"]


# Strategy I° : put 0
# Strategy II° : put NaN

value = 0

for roi, id in zip(roi_out, brainID_out):
    df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Synapses"]] = value
    df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Cell Density"]] = value


# Save results
#pd.write_csv(df_original, path_csv)
