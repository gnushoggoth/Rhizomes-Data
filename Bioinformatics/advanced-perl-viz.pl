#!/usr/bin/perl
use strict;
use warnings;
use Chart::Gnuplot;
use Bio::SeqIO;
use File::Temp qw(tempfile tempdir);
use Bio::Phylo::IO;
use Bio::Phylo::Treedrawer;
use File::Basename;

# This script demonstrates advanced bioinformatics visualization with Perl,
# focusing on Chart::Gnuplot and Circos configuration generation

# Part 1: Gene Expression Heat Map with Chart::Gnuplot
print "PART 1: Gene Expression Heat Map with Chart::Gnuplot\n";

# Create sample gene expression data
my @genes = ('Gene1', 'Gene2', 'Gene3', 'Gene4', 'Gene5', 'Gene6', 'Gene7', 'Gene8');
my @conditions = ('Condition1', 'Condition2', 'Condition3', 'Condition4');

# Generate random expression values matrix
my @expression_data;
foreach my $gene (@genes) {
    my @row;
    foreach my $condition (@conditions) {
        # Generate random expression value between -2 and 2
        push @row, -2 + rand(4);
    }
    push @expression_data, [@row];
}

# Create a temporary data file for the heat map
my ($fh, $data_file) = tempfile("heatmap_XXXX", SUFFIX => ".dat");
foreach my $i (0..$#genes) {
    foreach my $j (0..$#conditions) {
        print $fh "$j $i $expression_data[$i][$j]\n";
    }
    print $fh "\n"; # Add a blank line between rows to create a proper pm3d map
}
close $fh;

# Create a new Gnuplot chart
my $chart = Chart::Gnuplot->new(
    output => "gene_expression_heatmap.png",
    title  => "Gene Expression Heat Map",
    xlabel => "Conditions",
    ylabel => "Genes",
    grid   => "off",
    imagesize => "800, 600",
);

# Configure the chart for heat map visualization
$chart->set(
    pm3d     => "map",
    palette  => "defined (-2 'blue', 0 'white', 2 'red')",
    cbrange  => "[-2:2]",
    cblabel  => "Expression Level (log2)",
    xtics    => "(" . join(", ", map { "\"$conditions[$_]\" $_" } (0..$#conditions)) . ")",
    ytics    => "(" . join(", ", map { "\"$genes[$_]\" $_" } (0..$#genes)) . ")",
    xrange   => "[-0.5:" . ($#conditions + 0.5) . "]",
    yrange   => "[-0.5:" . ($#genes + 0.5) . "]",
    border   => "0",
    view     => "map",
);

# Add the data to the chart
my $dataSet = Chart::Gnuplot::DataSet->new(
    datafile => $data_file,
    style    => "pm3d",
    using    => "1:2:3",
);

# Plot the chart
$chart->plot2d($dataSet);

print "Generated gene expression heat map: gene_expression_heatmap.png\n\n";

# Part 2: Genome Browser Style Plot with Chart::Gnuplot
print "PART 2: Genome Browser Style Plot\n";

# Create sample genomic features
my @features = (
    { type => 'gene', start => 100, end => 500, name => 'geneA', strand => '+' },
    { type => 'gene', start => 700, end => 1200, name => 'geneB', strand => '-' },
    { type => 'CDS', start => 150, end => 400, name => 'CDS1', strand => '+' },
    { type => 'CDS', start => 800, end => 1100, name => 'CDS2', strand => '-' },
    { type => 'repeat', start => 300, end => 350, name => 'repeat1', strand => '+' },
    { type => 'repeat', start => 900, end => 950, name => 'repeat2', strand => '-' },
);

# Create a temporary data file for each feature type
my %type_files;
my %type_colors = (
    'gene' => 'blue',
    'CDS' => 'red',
    'repeat' => 'green',
);

foreach my $type (keys %type_colors) {
    my ($fh, $file) = tempfile("${type}_XXXX", SUFFIX => ".dat");
    $type_files{$type} = $file;
    
    # Write feature data
    foreach my $feature (@features) {
        next unless $feature->{type} eq $type;
        
        my $y_pos = ($feature->{strand} eq '+') ? 1 : 0;
        print $fh "$feature->{start} $y_pos\n";
        print $fh "$feature->{end} $y_pos\n\n";
    }
    close $fh;
}

# Create a new Gnuplot chart for genome browser
my $genome_chart = Chart::Gnuplot->new(
    output => "genome_browser.png",
    title  => "Genome Browser Style Plot",
    xlabel => "Genome Position",
    ylabel => "Strand",
    grid   => "off",
    imagesize => "800, 300",
);

# Configure the chart
$genome_chart->set(
    xrange => "[0:1500]",
    yrange => "[-0.5:1.5]",
    ytics  => "('- strand' 0, '+ strand' 1)",
    key    => "outside right",
);

# Add each feature type as a dataset
my @datasets;
foreach my $type (keys %type_files) {
    push @datasets, Chart::Gnuplot::DataSet->new(
        datafile => $type_files{$type},
        title    => $type,
        style    => "lines",
        width    => 10,
        color    => $type_colors{$type},
    );
}

# Plot the chart
$genome_chart->plot2d(@datasets);

print "Generated genome browser plot: genome_browser.png\n\n";

# Part 3: Generating a Circos Configuration File
print "PART 3: Circos Configuration Generation\n";

# Create a directory for Circos files
my $circos_dir = tempdir(CLEANUP => 0);
print "Created Circos directory: $circos_dir\n";

# Generate a simple karyotype file
my $karyotype_file = "$circos_dir/karyotype.txt";
open(my $kfh, '>', $karyotype_file) or die "Cannot open file: $!";
print $kfh "chr - chr1 1 0 1000 green\n";
print $kfh "chr - chr2 2 0 800 blue\n";
print $kfh "chr - chr3 3 0 600 red\n";
close $kfh;

# Generate a links file for connections between chromosomes
my $links_file = "$circos_dir/links.txt";
open(my $lfh, '>', $links_file) or die "Cannot open file: $!";
print $lfh "chr1 100 200 chr2 300 400 color=green\n";
print $lfh "chr1 500 600 chr3 100 200 color=blue\n";
print $lfh "chr2 500 600 chr3 300 400 color=red\n";
close $lfh;

# Generate GC content data
my $gc_file = "$circos_dir/gc_content.txt";
open(my $gcfh, '>', $gc_file) or die "Cannot open file: $!";
# Generate random GC content values
for my $chr (1..3) {
    my $chr_len = $chr == 1 ? 1000 : ($chr == 2 ? 800 : 600);
    my $window = 50;
    for (my $pos = 0; $pos < $chr_len; $pos += $window) {
        my $gc = 30 + rand(40); # Random GC content between 30% and 70%
        print $gcfh "chr$chr $pos " . ($pos + $window) . " $gc\n";
    }
}
close $gcfh;

# Generate the main Circos configuration file
my $conf_file = "$circos_dir/circos.conf";
open(my $cfh, '>', $conf_file) or die "Cannot open file: $!";

# Write Circos configuration
print $cfh <<'EOT';
# Circos configuration file
karyotype = karyotype.txt

# Define image size and basic parameters
<image>
dir = .
file = circos_plot.png
png = yes
svg = yes
radius = 1500p
angle_offset = -90
</image>

# Define chromosome ideograms
<ideogram>
<spacing>
default = 0.005r
</spacing>

radius = 0.9r
thickness = 20p
fill = yes
stroke_thickness = 2
stroke_color = black
show_label = yes
label_font = default
label_radius = 1.1r
label_size = 30
label_parallel = yes
</ideogram>

# Links between ideograms
<links>
<link>
file = links.txt
radius = 0.85r
color = black
thickness = 2
</link>
</links>

# GC content plot
<plots>
<plot>
type = line
file = gc_content.txt
r0 = 0.7r
r1 = 0.8r
color = black
thickness = 2
max = 70
min = 30

<rules>
<rule>
condition = 1
color = vdred
fill_color = red
</rule>
</rules>

</plot>
</plots>

# Ticks configuration
<ticks>
radius = 1r
color = black
thickness = 2p

<tick>
spacing = 100u
size = 10p
</tick>

<tick>
spacing = 500u
size = 15p
show_label = yes
label_size = 20p
label_offset = 10p
format = %d
</tick>
</ticks>

# Default housekeeping options
<housekeeping>
appending = no
</housekeeping>
EOT

close $cfh;

print "Generated Circos configuration files in $circos_dir\n";
print "To run Circos, execute: cd $circos_dir && circos -conf circos.conf\n\n";

# Part 4: Bio::Phylo for phylogenetic tree visualization
print "PART 4: Phylogenetic Tree Visualization\n";

# Sample Newick tree format
my $newick_tree = "(((Human:0.1,Chimp:0.2):0.3,Gorilla:0.4):0.5,(Mouse:0.6,Rat:0.7):0.8);";
my $tree_file = "phylo_tree.nwk";
open(my $tfh, '>', $tree_file) or die "Cannot open file: $!";
print $tfh $newick_tree;
close $tfh;

# Read the tree using Bio::Phylo
eval {
    my $tree = Bio::Phylo::IO->parse(
        -file => $tree_file,
        -format => 'newick'
    )->first;
    
    # Create a treedrawer object
    my $treedrawer = Bio::Phylo::Treedrawer->new(
        -width  => 800,
        -height => 600,
        -format => 'svg',
        -file   => 'phylogenetic_tree.svg'
    );
    
    # Apply the tree to the treedrawer
    $treedrawer->set_tree($tree);
    
    # Draw the tree
    $treedrawer->draw;
    
    print "Generated phylogenetic tree: phylogenetic_tree.svg\n";
} or do {
    print "Error creating phylogenetic tree: $@\nBio::Phylo may not be properly installed.\n";
};

# Part 5: GBrowse configuration generator
print "PART 5: GBrowse Configuration Generator\n";

# Create a sample GBrowse configuration file
my $gbrowse_file = "gbrowse.conf";
open(my $gbfh, '>', $gbrowse_file) or die "Cannot open file: $!";

print $gbfh <<'EOT';
[GENERAL]
description = Sample Genome Browser
database    = Bio::DB::SeqFeature::Store
db_adaptor  = DBI::mysql
db_args     = -dsn dbi:mysql:database=sample_genome;host=localhost
             -user gbrowse
             -pass gbrowse_passwd
search options = default

# Web site configuration
stylesheet  = /gbrowse/gbrowse.css
buttons     = /gbrowse/images/buttons
tmpimages   = /gbrowse/tmp

# Default glyph settings
glyph        = generic
height       = 10
bgcolor      = lightgrey
fgcolor      = black
label density = 25
bump density  = 100

reference class = Sequence

# where to link to when user clicks in detailed view
link          = AUTO

# what image widths to offer
image widths  = 450 640 800 1024

# default width of detailed view (pixels)
default width = 800
default features = Genes
                   ORFs
                   ESTs

# max and default segment sizes for detailed view
max segment     = 500000
default segment = 50000

# zoom levels
zoom levels    = 100 500 1000 2000 5000 10000 20000 40000 100000 200000 500000

# colors of the overview, detailed map and key
overview bgcolor = lightgrey
detailed bgcolor = lightgoldenrodyellow
key bgcolor      = beige

# examples to show in the introduction
examples = chr1:1000..5000
           gene:BRCA1

# "automatic" classes to try when an unqualified identifier is given
automatic classes = Symbol Gene Clone

# Plugin configuration
plugins = BatchDumper FastaDumper RestrictionAnnotator

#################################
# TRACK CONFIGURATION
#################################

[Genes]
feature      = gene
glyph        = gene
bgcolor      = peachpuff
height       = 10
description  = 1
key          = Protein-coding genes

[ORFs]
feature      = orf
glyph        = cds
bgcolor      = lavender
height       = 13
description  = 1
key          = Open reading frames

[ESTs]
feature      = EST
glyph        = segments
bgcolor      = yellow
connector    = solid
height       = 8
key          = ESTs
EOT

close $gbfh;

print "Generated GBrowse configuration file: $gbrowse_file\n";
print "\nAll visualization tasks completed successfully.\n";

__END__

=head1 NAME

advanced_bioinformatics_viz.pl - Advanced Perl-based bioinformatics visualization

=head1 DESCRIPTION

This script demonstrates advanced bioinformatics visualization techniques using Perl
libraries mentioned in the document, including:

1. Chart::Gnuplot for creating heat maps and genome browser plots
2. Circos configuration generation for circular genome visualization
3. Bio::Phylo for phylogenetic tree visualization
4. GBrowse configuration for genome browser setup

=head1 PREREQUISITES

The following Perl modules need to be installed:

- Chart::Gnuplot
- Bio::SeqIO (part of BioPerl)
- File::Temp
- Bio::Phylo
- File::Basename

Install them using CPAN:

  cpan Chart::Gnuplot Bio::Perl Bio::Phylo

Note: For Circos to work, you need to install it separately. This script only 
generates the configuration files.

=head1 USAGE

Run the script with:

  perl advanced_bioinformatics_viz.pl

This will generate several files:
- Heat map visualization: gene_expression_heatmap.png
- Genome browser plot: genome_browser.png
- Circos configuration files in a temporary directory
- Phylogenetic tree visualization: phylogenetic_tree.svg
- GBrowse configuration: gbrowse.conf

=head1 AUTHOR

Created as a demonstration of advanced Perl libraries for bioinformatics visualization.

=cut