def convert_clq_to_txt(input_file, output_file):
    """
    Convert a DIMACS .clq file to a plain text edge list file.

    Parameters:
        input_file (str): Path to the input .clq file.
        output_file (str): Path to the output edge list .txt file.
    """
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            if line.startswith("e"):  # Only process edge lines
                _, v1, v2 = line.split()
                outfile.write(f"{v1} {v2}\n")  # Write edges in plain text format
    print(f"Converted {input_file} to {output_file} with edge list format.")

# Example usage
input_clq_file = "brock800_4.clq"  
output_txt_file = "brock800_4.txt"

convert_clq_to_txt(input_clq_file, output_txt_file)
