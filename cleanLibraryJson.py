import json


def cleanLibraryJson(input_filename, output_filename):
    # Read the original JSON data
    with open(input_filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract only the 'tracks' part
    cleaned_data = data.get('tracks', [])

    # Save the cleaned data back to a new JSON file
    with open(output_filename, 'w', encoding='utf-8') as file:
        # Here, we're ensuring the JSON data is formatted with indentations for readability.
        json.dump(cleaned_data, file, indent=4)

    print(f"Cleaned JSON saved to {output_filename}.")

    return 0
