import pandas as pd
import json
import ast
import argparse

def process_data_record(record_dict):
    """
    Flatten a dictionary from the 'data' list.
    If the dictionary has a 'metricData' key (which is a list),
    extract each metric as a new key using the metricCode.
    """
    flattened = {}
    for key, value in record_dict.items():
        if key == "metricData" and isinstance(value, list):
            for metric in value:
                metric_code = metric.get("metricCode")
                if metric_code:
                    flattened[metric_code] = metric.get("metricValue")
        else:
            flattened[key] = value
    return flattened

def flatten_json_data(input_file, output_file):
    # Attempt to load the JSON file.
    try:
        with open(input_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file '{input_file}': {e}")
        return

    print(f"Loaded JSON with {len(data)} records.")

    output_records = []

    # Process each record in the JSON array.
    for idx, record in enumerate(data):
        try:
            # Get common columns (adjust keys as needed).
            cbsa_code = record.get("cbsa_code")
            status = record.get("status")
            
            # Get the 'data' field, which should be a list.
            data_list = record.get("data", [])
            # In case data_list is not already a list (e.g., a string),
            # try to evaluate it using ast.literal_eval.
            if not isinstance(data_list, list):
                try:
                    data_list = ast.literal_eval(data_list)
                except Exception as e:
                    print(f"Error evaluating 'data' for record {idx}: {e}")
                    continue

            # Only process if the list is non-empty.
            if data_list:
                for i, item in enumerate(data_list):
                    try:
                        flat_item = process_data_record(item)
                    except Exception as e:
                        print(f"Error processing a dictionary in record {idx}, item {i}: {e}")
                        continue

                    # Use the index (position in the list) as the value in a new column.
                    flat_item["data_index"] = i
                    # Carry over the extra columns.
                    flat_item["cbsa_code"] = cbsa_code
                    flat_item["status"] = status
                    output_records.append(flat_item)
            else:
                # If data_list is empty, optionally you can output a row indicating so.
                # For now, we'll skip records with empty data.
                continue

        except Exception as e:
            print(f"Error processing record {idx}: {e}")
            continue

    if not output_records:
        print("No records were processed successfully; nothing to output.")
        return

    # Create a DataFrame from the flattened records.
    df = pd.DataFrame(output_records)

    try:
        df.to_csv(output_file, index=False)
        print(f"Flattened CSV file has been created at '{output_file}'.")
    except Exception as e:
        print(f"Error writing CSV file: {e}")

# Main program
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flatten a JSON file (even if named with .csv) with a 'data' field (a list of dicts) into a CSV table."
    )
    parser.add_argument("input_file", help="Path to the input JSON file")
    parser.add_argument("output_file", help="Path to the output CSV file")
    args = parser.parse_args()

    flatten_json_data(args.input_file, args.output_file)