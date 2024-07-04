import json

def main(input_file, output_file):
    with open(input_file) as f:
        lines = f.readlines()

    # Remove any leading/trailing whitespace characters from each line
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]

    # Convert the list of lines to JSON format and write to the output file
    with open(output_file, 'w') as json_file:
        json.dump(lines, json_file, indent=4)

if __name__ == "__main__":
    input_file = "NoPower2Duplex_demo.txt"
    output_file = "NoPower2Duplex_demo.json"
    main(input_file, output_file)