import json
import pandas as pd
import os

def f(json_file): # where the atlas file is stored

    # Read the JSON file
    directory_path = os.path.dirname(json_file)

    with open(json_file, 'r') as f:
        data = json.load(f)

    # Function to recursively find data of nodes with no children
    def find_node_data(node):
        node_data = []
        if 'children' in node and not node['children']:
            node_data.append({
                'Acronym': node['data']['acronym'],
                'Name': node['data']['name'],
                'Hemisphere ID': node['data']['hemisphere_id']
            })
        elif 'children' in node:
            for child in node['children']:
                node_data.extend(find_node_data(child))
        return node_data

    # Find data of nodes with no children starting from the root
    nodes_without_children_data = find_node_data(data['root'])

    # Initialize lists to store final data
    final_data = []

    # Process each node data to create left and right hemisphere entries
    for node_data in nodes_without_children_data:
        acronym = node_data['Acronym']
        name = node_data['Name']
        hemisphere_id = node_data['Hemisphere ID']
        
        # Create left hemisphere entry
        left_entry = {
            'Acronym': f"Left: {acronym}",
            'Name': name,
            'Hemisphere ID': hemisphere_id
        }
        
        # Create right hemisphere entry
        right_entry = {
            'Acronym': f"Right: {acronym}",
            'Name': name,
            'Hemisphere ID': hemisphere_id
        }
        
        # Append entries to final data list
        final_data.append(left_entry)
        final_data.append(right_entry)

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(final_data)

    # Write DataFrame to CSV file
    csv_file = directory_path + '/leaves_regions_atlas.csv'
    print("Saving csv as: " + csv_file)
    df.to_csv(csv_file, index=False)

    return csv_file


