#!/usr/bin/perl
use strict;
use warnings;
use Bio::SeqIO;
use Bio::AlignIO;
use Bio::Tools::Run::Alignment::Clustalw;
use GD::Graph::bars;
use GD::Graph::lines;
use Bio::DB::GenBank;
use PDL;

# This script demonstrates various bioinformatics tasks using Perl libraries
# mentioned in the document: BioPerl, PDL, and GD::Graph

# Part 1: Using BioPerl to process sequence data
print "PART 1: BioPerl Sequence Processing\n";

# Create a new sequence object
my $seq_in = Bio::SeqIO->new(
    -file   => "<sample.fasta",
    -format => "fasta"
);

# Process each sequence in the file
my @sequences;
my %nucleotide_counts;
while (my $seq = $seq_in->next_seq) {
    push @sequences, $seq;
    
    # Count nucleotides
    my $sequence_string = $seq->seq;
    my %counts = (
        'A' => ($sequence_string =~ tr/A/A/),
        'C' => ($sequence_string =~ tr/C/C/),
        'G' => ($sequence_string =~ tr/G/G/),
        'T' => ($sequence_string =~ tr/T/T/)
    );
    
    # Add to overall counts
    foreach my $nucleotide (keys %counts) {
        $nucleotide_counts{$nucleotide} += $counts{$nucleotide};
    }
    
    # Print sequence info
    print "Sequence ID: ", $seq->id, "\n";
    print "Description: ", $seq->desc, "\n";
    print "Length: ", $seq->length, " bp\n";
    print "Nucleotide counts: ", join(", ", map { "$_ = $counts{$_}" } sort keys %counts), "\n\n";
}

# Part 2: Using PDL for data analysis
print "PART 2: PDL Data Analysis\n";

# Create a PDL object from nucleotide counts
my @nucleotides = sort keys %nucleotide_counts;
my @counts = map { $nucleotide_counts{$_} } @nucleotides;
my $pdl_data = pdl(@counts);

# Calculate basic statistics
print "Nucleotide statistics:\n";
print "Total counts: ", sum($pdl_data), "\n";
print "Mean count: ", average($pdl_data), "\n";
print "Max count: ", max($pdl_data), " (", $nucleotides[maximum_ind($pdl_data)], ")\n";
print "Min count: ", min($pdl_data), " (", $nucleotides[minimum_ind($pdl_data)], ")\n\n";

# Part 3: Using GD::Graph for visualization
print "PART 3: GD::Graph Visualization\n";

# Create a bar chart of nucleotide frequencies
my $width = 400;
my $height = 300;
my $graph = GD::Graph::bars->new($width, $height);

$graph->set(
    x_label           => 'Nucleotide',
    y_label           => 'Frequency',
    title             => 'Nucleotide Distribution',
    bar_spacing       => 4,
    shadow_depth      => 4,
    bar_width         => 20,
    transparent       => 0,
    dclrs             => ['blue', 'green', 'red', 'yellow'],
) or die $graph->error;

my @data = (
    \@nucleotides,
    \@counts
);

my $gd_image = $graph->plot(\@data) or die $graph->error;

# Save the image
open(my $fh, '>', 'nucleotide_distribution.png') or die "Cannot open file: $!";
binmode $fh;
print $fh $gd_image->png;
close $fh;

print "Generated nucleotide distribution chart: nucleotide_distribution.png\n\n";

# Part 4: Multiple sequence alignment with ClustalW
print "PART 4: Sequence Alignment with ClustalW\n";

# Skip this part if no sequences were loaded
if (@sequences > 1) {
    # Create a temporary file for the sequences
    my $seq_out = Bio::SeqIO->new(
        -file   => ">temp_seqs.fasta",
        -format => "fasta"
    );
    
    foreach my $seq (@sequences) {
        $seq_out->write_seq($seq);
    }
    
    # Perform alignment
    my $factory = Bio::Tools::Run::Alignment::Clustalw->new(
        -quiet => 1
    );
    
    my $aln = $factory->align("temp_seqs.fasta");
    
    # Write alignment to file
    my $aln_out = Bio::AlignIO->new(
        -file   => ">alignment.aln",
        -format => "clustalw"
    );
    
    $aln_out->write_aln($aln);
    print "Generated multiple sequence alignment: alignment.aln\n";
}

# Part 5: Using Bio::DB::GenBank to fetch sequences
print "PART 5: Fetching Sequences from GenBank\n";

# Create a GenBank database handle
my $gb = Bio::DB::GenBank->new(-delay => 1, -retrieval_type => 'tempfile');

# Fetch a sequence by accession number
my $acc = "NM_001126114"; # Example accession number (human p53)
eval {
    my $seq = $gb->get_Seq_by_acc($acc);
    print "Retrieved sequence: ", $acc, "\n";
    print "Description: ", $seq->desc, "\n";
    print "Length: ", $seq->length, " bp\n\n";
    
    # Save the sequence
    my $out = Bio::SeqIO->new(-file => ">genbank_seq.gb", -format => 'genbank');
    $out->write_seq($seq);
    print "Saved sequence to: genbank_seq.gb\n";
} or do {
    print "Error fetching sequence: $@\n";
};

print "\nScript completed successfully.\n";

__END__

=head1 NAME

bioperl_visualization.pl - Demonstrates BioPerl, PDL, and GD::Graph for bioinformatics

=head1 DESCRIPTION

This script demonstrates how to use various Perl libraries for bioinformatics 
data processing and visualization, including:

1. BioPerl for sequence manipulation and analysis
2. PDL (Perl Data Language) for numerical data processing
3. GD::Graph for creating visualizations
4. Bio::Tools::Run::Alignment::Clustalw for sequence alignment

=head1 PREREQUISITES

The following Perl modules need to be installed:

- Bio::SeqIO (part of BioPerl)
- Bio::AlignIO (part of BioPerl)
- Bio::Tools::Run::Alignment::Clustalw (part of BioPerl)
- GD::Graph
- PDL
- Bio::DB::GenBank (part of BioPerl)

Install them using CPAN:

  cpan Bio::Perl GD::Graph PDL

=head1 USAGE

Before running the script, ensure you have a sample FASTA file named 'sample.fasta'
in the same directory. Then run:

  perl bioperl_visualization.pl

The script will generate several output files including a nucleotide distribution chart.

=head1 AUTHOR

Created as a demonstration of Perl libraries for bioinformatics visualization.

=cut