import os
import re
from pathlib import Path

def process_gsd_file(input_file_path, csv_file):
    """
    Process a single GSD file and write its data to the combined CSV file
    """
    current_block = []
    format_pattern = re.compile(r'\[(\d+,\d{4}-\d{2}-\d{2}:\d{2}:\d{2}:\d{2})\]')
    
    # Header is written by main() only when the output file is empty
    
    with open(input_file_path, 'r') as infile:
        for line in infile:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            # Check if line contains the format pattern
            match = format_pattern.match(line)
            if match:
                # If we have a previous block, write it
                if current_block:
                    write_block(current_block, csv_file)
                # Start new block with the format value
                current_block = [match.group(1)]
            elif current_block:  # If we're in a block, add processed line
                if '=' in line:  # Only process lines with equal signs
                    processed_line = line.replace('=', ',')
                    current_block.append(processed_line)
        
        # Write the last block if exists
        if current_block:
            write_block(current_block, csv_file)

def write_block(block, csv_file):
    """
    Write a block of data to the CSV file
    """
    format_value = block[0]
    # Write each line in the block
    for line in block[1:]:  # Skip the format value itself
        # Split the line into columns
        columns = line.split(',')
        # The values start from TRAIL_ID, so columns[1] is Y_COORDINA, columns[3] is TIME_ORIGINAL
        if len(columns) > 4:
            # Calculate Y_WGS84 from Y_COORDINA (columns[1])
            y_coordina = columns[1]
            y_wgs84 = ''
            if y_coordina.isdigit() and len(y_coordina) >= 4:
                deg = int(y_coordina[:2])
                min_dec = float(y_coordina[2:]) / 10000 if len(y_coordina) > 4 else float(y_coordina[2:])
                if len(y_coordina) > 4:
                    min_dec = float(y_coordina[2:]) / 10000
                else:
                    min_dec = float(y_coordina[2:])
                y_wgs84_val = deg + (min_dec / 60)
                y_wgs84 = f"{y_wgs84_val:.7f}"
            columns.insert(2, y_wgs84)

            # Calculate X_WGS84 from X_COORDINA (columns[3] after Y_WGS84 inserted)
            x_coordina = columns[3]
            x_wgs84 = ''
            if x_coordina.isdigit() and len(x_coordina) >= 4:
                deg = int(x_coordina[:2])
                min_dec = float(x_coordina[2:]) / 10000 if len(x_coordina) > 4 else float(x_coordina[2:])
                if len(x_coordina) > 4:
                    min_dec = float(x_coordina[2:]) / 10000
                else:
                    min_dec = float(x_coordina[2:])
                x_wgs84_val = deg + (min_dec / 60)
                x_wgs84 = f"{x_wgs84_val:.7f}"
            columns.insert(4, x_wgs84)

            # TIME_ORIGINAL to TIME
            time_original = columns[5]
            if time_original.isdigit() and len(time_original) in [5,6]:
                time_original_padded = time_original.zfill(6)
                time_value = f"{time_original_padded[0:2]}:{time_original_padded[2:4]}:{time_original_padded[4:6]}"
            else:
                time_value = ''
            columns.insert(7, time_value)
            # SPEED is now at index 10 after all previous insertions
            if len(columns) >= 9:
                speed = columns[8]
                try:
                    speed_val = float(speed) / 100
                    columns[8] = f"{speed_val:.2f}"
                except Exception:
                    pass
            csv_file.write(f"{format_value},{','.join(columns)}\n")
        else:
            csv_file.write(f"{format_value},{line}\n")

def main():
    data_dir = Path('data')
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Create a single CSV file for all data
    output_file = output_dir / 'combined_data.csv'
    
    # Open the output file in append mode and write header only if empty
    header = 'TP_ID,DATA_TRANSFER_DATE,TRAIL_ID,Y_COORDINA,Y_WGS84,X_COORDINA,X_WGS84,TIME_ORIGINAL,DATE_ORIGINAL,TIME,SPEED,HEIGHT\n'
    with open(output_file, 'w') as csv_file:
        csv_file.seek(0, os.SEEK_END)
        if csv_file.tell() == 0:
            csv_file.write(header)
        # Process each .gsd file in the data directory
        for gsd_file in sorted(data_dir.glob('*.gsd')):
            print(f"Processing {gsd_file}")
            process_gsd_file(gsd_file, csv_file)
            print(f"Completed processing {gsd_file}")
    
    print(f"\nAll data has been combined into {output_file}")

if __name__ == '__main__':
    main()
