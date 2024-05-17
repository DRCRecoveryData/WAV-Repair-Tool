use strict;
use warnings;
use File::Path qw(make_path);
use File::Copy;
use File::Basename;

sub cut_wav_header {
    my ($input_path) = @_;
    open(my $fh, '<:raw', $input_path) or die "Cannot open file $input_path: $!";
    read($fh, my $header, 44);
    close($fh);
    return $header;
}

sub load_encrypted_wav {
    my ($input_path, $offset) = @_;
    open(my $fh, '<:raw', $input_path) or die "Cannot open file $input_path: $!";
    seek($fh, $offset, 0);
    read($fh, my $encrypted_data, -s $fh - 334);  # Read until end of file minus 334 bytes
    close($fh);
    return $encrypted_data;
}

sub merge_wav_files {
    my ($reference_header, $encrypted_data) = @_;
    return $reference_header . $encrypted_data;
}

sub save_repaired_wav {
    my ($input_path, $repaired_data, $riff_chunk_size, $data_chunk_size, $output_folder) = @_;

    make_path($output_folder);

    my ($input_filename, $input_dirs, $suffix) = fileparse($input_path, qr/\.[^.]*/);
    my $output_full_path = "$output_folder/$input_filename.wav";

    my $header = substr($repaired_data, 0, 44);
    substr($header, 4, 4) = pack('V', $riff_chunk_size);
    substr($header, 40, 4) = pack('V', $data_chunk_size);

    open(my $fh, '>:raw', $output_full_path) or die "Cannot create file $output_full_path: $!";
    print $fh $header . substr($repaired_data, 44);
    close($fh);

    print "File saved to $output_full_path\n";
}

sub calculate_first_complete_frame_position {
    my ($bits_per_sample, $num_channels) = @_;
    my $frame_size = int($bits_per_sample / 8) * $num_channels;
    my $first_complete_frame_number = int((153605 - 44) / $frame_size) + 1;
    return 44 + ($first_complete_frame_number * $frame_size);
}

sub is_double_extension_wav {
    my ($file_name) = @_;
    my ($name_without_ext, $first_ext) = fileparse($file_name, qr/\.[^.]*/);
    my ($second_name, $second_ext) = fileparse($name_without_ext, qr/\.[^.]*/);
    return lc($second_ext) eq '.wav';
}

sub main {
    print "Current working directory: " . `cd`;
    print "Enter the path to the reference WAV file: ";
    my $reference_wav_path = <STDIN>;
    chomp($reference_wav_path);

    my $start_time = time();

    my $reference_header = cut_wav_header($reference_wav_path);
    my $bits_per_sample = unpack('v', substr($reference_header, 34, 2));
    my $num_channels = unpack('v', substr($reference_header, 22, 2));
    my $position = calculate_first_complete_frame_position($bits_per_sample, $num_channels);
    print "Position of the first complete frame: $position\n";

    print "Enter the path to the folder containing encrypted WAV files: ";
    my $encrypted_wav_folder = <STDIN>;
    chomp($encrypted_wav_folder);

    my $corrupted_files_folder = dirname($encrypted_wav_folder);
    my $output_folder = "$corrupted_files_folder/Repaired";

    opendir(my $dh, $encrypted_wav_folder) or die "Cannot open directory $encrypted_wav_folder: $!";
    while (my $file = readdir($dh)) {
        next if $file =~ /^\./;
        print "Checking file: $file\n";
        if (is_double_extension_wav($file)) {
            my $encrypted_wav_path = "$encrypted_wav_folder/$file";
            my $offset = $position;
            my $encrypted_data = load_encrypted_wav($encrypted_wav_path, $offset);

            my $file_size = length($encrypted_data) + 44;
            my $riff_chunk_size = $file_size - 8;
            my $data_chunk_size = $file_size - 44;

            my $repaired_wav_data = merge_wav_files($reference_header, $encrypted_data);

            save_repaired_wav($encrypted_wav_path, $repaired_wav_data, $riff_chunk_size, $data_chunk_size, $output_folder);
        }
    }
    closedir($dh);

    my $end_time = time();
    my $execution_time = $end_time - $start_time;
    printf "Execution time: %.2f seconds\n", $execution_time;
}

main();
