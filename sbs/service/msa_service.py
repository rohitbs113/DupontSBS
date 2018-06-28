"""
EXAMPLE USAGE: python msa_service.py --start 400 --end 700 --sample AB7280002
"""

import logging
import os
import re
import tempfile
from collections import OrderedDict
from multiprocessing.dummy import Pool as ThreadPool
from os.path import join
from subprocess import check_output

import requests

from sbs import config as cfg
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# Configuration parameters
BUCKET = cfg.s3_bucket
# The minimum number of times a sequence must appear to be returned
# (Used to filter out noisy reads)
MINIMUM_READS = 2


# Function to export credentials to the system to Samtools can directly call S3
def get_credentials():
    # Get the credential URL
    url = '{}/{}'.format(cfg.aws_credential_url, cfg.role_name)

    # Retrieve AWS credentials
    credentials = requests.get(url).json()
    AccessKeyId = credentials['AccessKeyId']
    SecretAccessKey = credentials['SecretAccessKey']
    Token = credentials['Token']

    # Export Credentials to Environment
    os.environ["AWS_ACCESS_KEY_ID"] = AccessKeyId
    os.environ["AWS_SECRET_ACCESS_KEY"] = SecretAccessKey
    os.environ["AWS_SESSION_TOKEN"] = Token

def get_msa_view_data(path, start, end, bamfile_type):

    start = int(start)
    end = int(end)
    path = path.rstrip("/")

    # For MSA Integrity Page
    if start == end:
        end = start + 150
        start = start - 150

    sample_id, analysis_id, construct_id = path.split("/")
    fasta_file_dir = ""
    request_id = sample_id[:5]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    samtools_path = join(os.path.split(dir_path)[0], cfg.samtools_path)
    # Change to /tmp so that Samtools can download the .bai file
    os.chdir(tempfile.gettempdir())
    if bamfile_type == "junction":
        file_name = '{}.{}.softclip.bam'.format(sample_id, construct_id)
    else:
        file_name = '{}.{}.{}.bam'.format(sample_id, construct_id, bamfile_type)

    construct_len = len(construct_id.split("."))
    if construct_len > 1:
        (sample_id, seq_id, sample_id, _, file_type, ext) = file_name.split('.')
        seq_id = construct_id
        fasta_file_dir = "observed"
    else:
        (sample_id, seq_id, file_type, ext) = file_name.split('.')
        fasta_file_dir = "output"
    range_key = '{}:{}-{}'.format(seq_id, start, end)
    cmds = []
    # Command to retrieve the FASTA file contents
    s3_path = 's3://{}/{}/{}/{}/{}/{}/{}.fa'.format(BUCKET, cfg.s3_samples_key,\
                                                request_id, sample_id, analysis_id,\
                                                fasta_file_dir, seq_id)
    cmds.append('{} faidx {} {}'.format(samtools_path, s3_path, seq_id))

    # Command to retrieve the BAM file contents
    s3_path = 's3://{}/{}/{}/{}/{}/{}/{}'.format(BUCKET, cfg.s3_samples_key,\
                                                request_id, sample_id, analysis_id,\
                                                fasta_file_dir, file_name)
    cmds.append('{} view {} {}'.format(samtools_path, s3_path, range_key))

    # Create the Pool of workers
    pool = ThreadPool(2)

    # Retrieve the BAM and FASTA data from Samtools
    results = pool.map(lambda cmd: check_output(cmd, shell=True).decode('UTF-8').strip().split('\n'), cmds)

    # Close the pool and wait for the work to finish
    pool.close()
    pool.join()

    # Build the Expected Sequence string
    expected_sequence = ''
    for line in results[0]:
        if line[0] != '>':
            expected_sequence += line.strip()

    # If the boundary falls entirely within the Expected Sequence, take the slice we need
    if (start >= 1) and (end <= len(expected_sequence)):
        expected_sequence = expected_sequence[start-1:end]
    # Otherwise append '*' characters to denote the parts that fall outside the Expected Sequence
    elif start < 1:
        missing_seq = '*'*(1 - start)
        expected_sequence = missing_seq + expected_sequence[0:end]
    elif end > len(expected_sequence):
        missing_seq = '*' * (end - len(expected_sequence))
        expected_sequence = expected_sequence[start-1:] + missing_seq

    # Iterate over the SAM file and build a dictionary of maximum insertion lengths at each insert position
    insert_positions = {}
    for line in results[1]:
        parts = line.split('\t')

        # This occurs when the BAM file contains no data in the range requested
        if len(parts) == 1:
            break

        # Get the sequence
        seq_start = int(parts[3])
        cigar = parts[5]
        seq = parts[9]
        seq_end = seq_start + len(seq) - 1

        # Split the CIGAR string into parts
        sections = re.findall(r'([0-9]+)([MIDNSHPX=])', cigar)

        # Get the offset of the sequence start from the first item that consumes the Expected Sequence
        offset = 0
        for section in sections:
            # If the first item is not Soft Clipping or Insert, don't adjust offset value
            if section[1] in ('M', 'D', 'N', '=', 'X'):
                break
            else:
                offset -= int(section[0])

        # Adjust the sequence start position relative to the Expected Sequence based on the offset value
        seq_start += offset
        seq_end += offset

        index = 0
        for section in sections:
            if section[1] in ('M', '=', 'X', 'S'):
                index += int(section[0])
            elif section[1] == 'D':
                # Deletions consume the Expected Sequence, so increment the sequence counter
                seq_start += int(section[0])
            else:
                if (section[1] == 'I') and (seq_start >= start) and (seq_end <= end):
                    # Record the length of the longest insertion at each position
                    insert_pos = seq_start + index - 1

                    # If an insert record already exists for the locus, update if this insert is longer than the existing one
                    if (insert_pos in insert_positions) and (int(section[0]) > insert_positions[insert_pos]):
                        insert_positions[insert_pos] = int(section[0])
                    elif insert_pos not in insert_positions:
                        insert_positions[insert_pos] = int(section[0])


    # Build the position header (including Insertions) and
    # calculate offsets for the coverage header
    row1 = ''
    first_value_offset = 20 - start % 20
    if first_value_offset == 20:
        first_value_offset = 0

    for step in range(0, first_value_offset):
        row1 += ' '
    coverage_calculation_positions = []
    for step in range(start + first_value_offset, end + 1):
        if step % 20 == 0:
            justification_offset = 20
            for pos in range(step, step + 20):
                if pos in insert_positions:
                    justification_offset += insert_positions[pos]
            row1 += str(step).ljust(justification_offset)
            coverage_calculation_positions.append(step)

    # Remove any trailing whitespace characters from the position header
    row1 = row1.rstrip()

    # Build the scale header (including Insertions)
    exploded_row2 = []
    for step in range(start, end + 1):
        # Scale
        if step % 10 == 0:
            exploded_row2.append('|')
        else:
            exploded_row2.append('.')

    # Build the Expected Sequence header (including Insertions)
    exploded_seq = [str(x) for x in expected_sequence]
    for pos in insert_positions:
        read_insert_string = ''
        scale_insert_string = ''
        for item in range(0, insert_positions[pos]):
            read_insert_string += '-'
            scale_insert_string += ' '

        exploded_seq[pos - start] += read_insert_string
        exploded_row2[pos - start] += scale_insert_string

    expected_sequence = ''.join(exploded_seq)
    row2 = ''.join(exploded_row2)


    # Iterate over the SAM file and build a list of sequences for the MSA view, incorporating INDELs
    sequences = []
    for line in results[1]:
        parts = line.split('\t')

        # This occurs when the BAM file contains no data in the range requested
        if len(parts) == 1:
            break

        # Get the sequence
        seq_start = int(parts[3])
        cigar = parts[5]
        seq = parts[9]
        seq_end = seq_start + len(seq) - 1

        # Split the CIGAR string into parts
        sections = re.findall(r'([0-9]+)([MIDNSHPX=])', cigar)

        # Get the offset for the first item that consumes the Expected Sequence
        offset = 0
        for section in sections:
            if section[1] in ('M', 'D', 'N', '=', 'X'):
                break
            else:
                offset -= int(section[0])

        # Adjust the start/end positions of the sequence based on the CIGAR string
        seq_start += offset
        seq_end += offset

        # Add sequences where entire sequence is within the bounding coordinates
        if (seq_start >= start) and (seq_end <= end):
            # Generate a list of the INDEL and Soft-Clipping positions
            exploded_sequence = []

            # Fill the initial positions with dashes
            for pos in range(start, seq_start):
                base = '-'
                if pos in insert_positions:
                    # Add in placeholders for Insertions if they exist at this locus
                    for extra_base in range(0,insert_positions[pos]):
                        base += '-'

                exploded_sequence.append(base)

            # Add in the sequence values, accounting for INDELs
            sequence_index = 0
            for section in sections:
                steps = int(section[0])

                # Append matched bases
                if section[1] == 'M':
                    for step in range(0, steps):
                        base = seq[sequence_index]
                        exploded_sequence.append(str(base))
                        sequence_index += 1
                # Append lower-cased Soft Clipping bases
                elif section[1] == 'S':
                    for step in range(0, steps):
                        base = str(seq[sequence_index]).lower()
                        exploded_sequence.append(base)
                        sequence_index += 1
                # Deletions don't consume the sequence, so don't increment the counter
                elif section[1] == 'D':
                    for step in range(0, steps):
                        exploded_sequence.append('*')
                        # Increment the sequence end value, so that we don't print unneeded '-' symbols
                        seq_end += 1
                # Insertions don't consume the Expected Sequence, so multiple bases are present at a single Expected Sequence position
                elif section[1] == 'I':
                    # Append insertions on to the last item written
                    base = ''
                    for step in range(0, steps):
                        base += str(seq[sequence_index])
                        sequence_index += 1
                        # Decrement the sequence end value, since inserts don't consume the sequence
                        seq_end -= 1

                    exploded_sequence[-1] += base

            # Fill the final positions with dashes
            for pos in range(seq_end, end + 1):
                base = '-'
                # Add in extra '-' for Insertions
                if pos in insert_positions:
                    for extra_base in range(0,insert_positions[pos]):
                        base += '-'

                exploded_sequence.append(base)

            # For locations with insertions, pad with additional '-' symbols if necessary
            for position in insert_positions:
                index = position - start
                insert_length = insert_positions[position]
                # Insert positions include the Expected Sequence allele, so we need to add one to get the total length
                if len(exploded_sequence[index]) < insert_length + 1:
                    length_differential = insert_length - len(exploded_sequence[index]) + 1
                    for step in range(0, length_differential):
                        exploded_sequence[index] += '-'

            # Join the sequence into a string and append to the list of sequences
            sequences.append(''.join(exploded_sequence))


        """
        # Case where sequence overlaps the start
        elif (seq_start <= start) and (seq_end >= start):
            index = start - seq_start
            seq_str = seq[index:]
            for step in range(seq_end, end):
                seq_str += '-'

        # Case where sequence overlaps the end
        elif (seq_start < end) and (seq_end >= end):
            for step in range(start, seq_start):
                seq_str += '-'

            index = end - seq_start
            seq_str += seq[:index]
        """


    # Create an ordered dictionary with the counts of unique sequences
    seq_out = OrderedDict()
    for sequence in sequences:
        if sequence in seq_out:
            seq_out[sequence] += 1
        else:
            seq_out[sequence] = 1

    # Get a count of the total and unique reads
    total_coverage = len(sequences)
    unique_coverage = len(seq_out)

    # Create a list of the unique reads and counts
    reads_list = []
    deletes_list = []
    for seq in seq_out:
        # Apply read count filter
        if seq_out[seq] >= MINIMUM_READS:
            # Look for SNPs in each unique sequence
            snp_locs = []
            read = ''
            for index, (s, r) in enumerate(zip(seq, expected_sequence)):
                if (s != '-') and (s != r):
                    if s.lower() == 'a':
                        snp_locs.append({index: 'red'})
                    elif s.lower() == 'c':
                        snp_locs.append({index: 'orange'})
                    elif s.lower() == 't':
                        snp_locs.append({index: 'green'})
                    elif s.lower() == 'g':
                        snp_locs.append({index: 'blue'})

                    # Convert the SNP/INDEL basecalls to lower case
                    read += s.lower()
                else:
                    read += s

            reads_list.append({'read': read, 'read_count': seq_out[seq], 'snp_locs': snp_locs})
        else:
            deletes_list.append(seq)

    # Delete reads that don't meet the threshold from the dictionary
    for seq in deletes_list:
        del seq_out[seq]

    # Calculate coverage values
    coverage_position_indices, coverage = [], []
    for pos in coverage_calculation_positions:
        # Get the index of the calculated positions in the string
        matches = [m.start() for m in re.finditer(str(pos), row1)]
        if len(matches) == 1:
            coverage_position_indices += matches
        else:
            str_len = len(str(pos))
            for index in matches:
                if (index > 0) and (index + str_len < len(row1)) and (row1[index-1] == ' ') and (row1[index + str_len] == ' '):
                    coverage_position_indices.append(index)
                elif (index == 0) and (index + str_len < len(row1)) and (row1[index + str_len] == ' '):
                    coverage_position_indices.append(index)
                elif (index > 0) and (index + str_len == len(row1)) and (row1[index-1] == ' '):
                    coverage_position_indices.append(index)

    # For each index, calculate the total coverage
    for index in coverage_position_indices:
        position_coverage = 0
        for seq in seq_out:
            if seq[index] != '-':
                position_coverage += seq_out[seq]

        coverage.append(position_coverage)

    # Write the coverage string
    coverage_string = ''
    for step in range(0, coverage_position_indices[0]):
        coverage_string += ' '
    coverage_count = len(coverage)
    for index, coverage in enumerate(coverage):
        if index < coverage_count - 1:
            justification_offset = coverage_position_indices[index + 1] - coverage_position_indices[index]
            coverage_string += str(coverage).ljust(justification_offset)
        else:
            coverage_string += str(coverage)

    #bam_type dictionary
    bam_type_dictionary = {
                            "softclip" : "BowtieCoverage",
                            "integrity": "IntegrityCoverage",
                            "HC": "HaplotypeCoverage",
                            "junction": "JunctionCoverage"
                        }
    # Create the output dictionary
    output = {
        'header_row_1': row1,
        'header_row_2': row2,
        'header_row_3': expected_sequence,
        'header_row_4': coverage_string,
        'reads': reads_list,
        'total_read_count': total_coverage,
        'unique_read_count': unique_coverage,
        'coverage_type': bam_type_dictionary[bamfile_type],
        'start': start,
        'end': end
    }

    # Delete BAI file
    try:
        os.remove('{}.bai'.format(file_name))
    except:
        logger.error('BAI file could not be found')

    """
    # Diagnostic output for displaying the results
    print('\n    {} ({:,} reads of total coverage)'.format(range_key, total_coverage))
    print('    {}'.format(row1))
    print('    {}'.format(row2))
    print('    {}'.format(expected_sequence))
    print('    {}\n'.format(coverage_string))

    for key in seq_out:
        print('{} {}'.format(str(seq_out[key]).rjust(3), key))
    """
    return output
