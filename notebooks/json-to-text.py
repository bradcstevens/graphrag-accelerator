import json

def json_to_text(json_file, output_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Ensure data is a list for consistent processing
    if isinstance(data, dict):
        data = [data]

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            # Write the title
            if 'title' in item:
                f.write(f"{item['title']}\n")
            
            # Write the blobUri
            if 'blobUri' in item:
                f.write(f"{item['blobUri']}\n\n")
            
            # Extract and write the content from ImageDetails
            if 'metadata' in item and 'ImageDetails' in item['metadata']:
                image_details_str = item['metadata']['ImageDetails']
                try:
                    # Parse the JSON string inside ImageDetails
                    image_details = json.loads(image_details_str)
                    # Get 'choices' and extract 'message' content
                    if 'choices' in image_details:
                        for choice in image_details['choices']:
                            if 'message' in choice and 'content' in choice['message']:
                                content = choice['message']['content']
                                f.write(f"{content}\n\n")
                except json.JSONDecodeError:
                    f.write("Invalid JSON in ImageDetails.\n\n")
            
            # Separator between items
            f.write("\n--------------------------------------\n\n")

if __name__ == "__main__":
    json_file = 'response_1726859158967.json'      # Replace with your JSON file name
    output_file = 'response_1726859158967.txt'    # Replace with your desired output file name
    json_to_text(json_file, output_file)