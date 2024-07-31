import json
import pandas as pd
import os

"""
Module to find the leaf ROIs (regions of interest) of the "Adult Mouse Brain - Allen Brain Atlas V3p1-Ontology".

This module reads a JSON file containing a hierarchical representation of brain regions,
identifies regions with no child nodes (leaf nodes), and exports these regions to a CSV file.
"""

def process_atlas_json(json_file):
    """
    Process the atlas JSON file to extract leaf node data and save it as a CSV file.

    Args:
        json_file (str): The path to the JSON file containing the atlas data.

    Returns:
        str: The path to the generated CSV file containing leaf node data.
    """

    # Read the JSON file
    directory_path = os.path.dirname(json_file)

    with open(json_file, 'r') as file:
        data = json.load(file)

    # Function to recursively find data of nodes with no children
    def find_leaf_nodes(node):
        """
        Recursively find nodes that have no children in the hierarchy.

        Args:
            node (dict): A dictionary representing a node in the hierarchy.

        Returns:
            list: A list of dictionaries containing data of leaf nodes.
        """
        leaf_nodes = []
        if 'children' in node and not node['children']:
            # Node with no children found, store its data
            leaf_nodes.append({
                'Acronym': node['data']['acronym'],
                'Name': node['data']['name'],
                'Hemisphere ID': node['data']['hemisphere_id']
            })
        elif 'children' in node:
            # Recursively search for leaf nodes in each child
            for child in node['children']:
                leaf_nodes.extend(find_leaf_nodes(child))
        return leaf_nodes

    # Find data of nodes with no children starting from the root
    nodes_without_children_data = find_leaf_nodes(data['root'])

    # Initialize lists to store final data
    final_data = []

    # Process each node data to create left and right hemisphere entries
    for node_data in nodes_without_children_data:
        acronym = node_data['Acronym']
        name = node_data['Name']
        hemisphere_id = node_data['Hemisphere ID']

        #Attention: add "Left: " "Rigth: " to create 2 copies or each region
        
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
    csv_file = os.path.join(directory_path, 'leaves_regions_atlas.csv')
    print("Saving csv as:", csv_file)
    df.to_csv(csv_file, index=False)

    return csv_file

#process_atlas_json("assets/Adult Mouse Brain - Allen Brain Atlas V3p1-Ontology.json")