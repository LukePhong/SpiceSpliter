import argparse
import os
import re
import shutil
import subprocess
# import tempfile

# Create argument parser
parser = argparse.ArgumentParser(description="Process SPI files")
parser.add_argument("filename", help="Input file name")
parser.add_argument("-k", "--keep", action="store_true", help="Keep temporary files")
parser.add_argument("-c", "--command", help="Command to execute after processing. Please use ${filename} in your command if you want splited files to be used in it.")
args = parser.parse_args()

# Define pattern for .subckt and .end
pattern = re.compile(r'(\.subckt|\.SUBCKT)\s+(\S+)\s+(.*?)(\.end|\.END)', re.DOTALL)

# Read input file
with open(args.filename) as f:
    text = f.read()

# Find all .subckt sections
sections = pattern.findall(text)

# Create temporary directory
basename = os.path.splitext(args.filename)[0]
# tmp_dir = tempfile.mkdtemp(prefix=basename[0], dir=dirname)
if not os.path.exists(basename):
    os.mkdir(basename)

# Create dictionary to store sections
section_dict = {}

# Process each section
for section in sections:
    # Get the index from the first word after .subckt
    index = section[1]
    section_dict[index] = section

# Make temp file and process
for section, text in section_dict.items():
    # Create a temporary file for the section
    temp_file = os.path.join(basename, section + ".spi")
    text_string = " ".join(text)
    with open(temp_file, "w") as f:
        # Get all indices mentioned in the section
        indices = set(re.findall(r"\b\w+\b", text_string))
        # Write the sections mentioned by the current section
        for idx in indices:
            if idx != section and idx in section_dict:
                f.write(" ".join(section_dict[idx]))
                f.write(os.linesep)
        # Write the section to the file
        f.write(text_string)
    # Execute command if specified
    if args.command:
        command = args.command.replace("${filename}", temp_file)
        subprocess.run(command, shell=True)

# Remove temporary directory
if not args.keep:
    shutil.rmtree(basename)
