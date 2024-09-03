df = all_df

# Create the same df, but with a different formatting
# Step 1: Split 'ROI' column into 'Side' and 'Region'
df[['Side', 'Region']] = df['ROI'].str.split(': ', expand=True)

# Step 2: Separate data by 'Side'
left_df = df[df['Side'] == 'Left'].drop(columns=['Side'])
right_df = df[df['Side'] == 'Right'].drop(columns=['Side'])

# Save orignal order
order = left_df["Region"]
print(order)

# Step 3: Rename columns to prepare for merging
left_df = left_df.rename(columns={'Synapses': 'Synapses_Left', 'Area': 'Area_Left', "Cell Density": "Cell Density Left"})
right_df = right_df.rename(columns={'Synapses': 'Synapses_Right', 'Area': 'Area_Right', "Cell Density": "Cell Density Right"})

# Select only specific columns
removed_col_df = left_df.drop(columns=["Synapses_Left", "Area_Left", "Cell Density Left"])
left_df = left_df[["Region", "Synapses_Left", "Area_Left", "Cell Density Left"]]
right_df = right_df[["Region", "Synapses_Right", "Area_Right","Cell Density Right"]]

# Step 4: Merge the left and right DataFrames on 'Region'
combined_df = pd.merge(left_df, right_df, on='Region', how='outer') # ATTENTION: due to same col in the 2

# Step 4: Merge the combined_df with the missing col
combined_df = pd.merge(combined_df, removed_col_df, on='Region', how='outer')

# Reorder df
df.set_index('Region', inplace=True)
df = df.reindex(order)
df.reset_index(inplace=True)

print(combined_df)

# Step 5: Rename the 'Region' column to 'ROI'
#combined_df = combined_df.rename(columns={'Region': 'ROI'})

# Step 6: subsample columns
combined_df = combined_df[["Region", "Brain ID", "Region Injection", "Side Injection", "Side Lesion", "TimePoint",
                           "Synapses_Left", "Area_Left", "Cell Density Left",
                           "Synapses_Right", "Area_Right","Cell Density Right"]]

# Saving
path_csv = output_folder + "/all_brains_LR.csv"
print(f"\nSaving final csv as {path_csv}\n")
combined_df.to_csv(path_csv, index=False)