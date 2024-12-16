import struct

def convert_to_binedgelist(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'wb') as outfile:
        for line in infile:
            src, dst = map(int, line.strip().split())
            # Pack as two int32 (source, destination)
            outfile.write(struct.pack('ii', src, dst))

# Replace 'subset_graph.txt' with your actual input file name
convert_to_binedgelist('brock400_4.txt', 'brock400_4.binedgelist')
convert_to_binedgelist('brock800_4.txt', 'brock800_4.binedgelist')

