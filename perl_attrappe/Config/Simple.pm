# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
package Config::Simple;
require Exporter; our @ISA = ('Exporter');
our $VERSION = '0.00_attrappe';
sub new     { my $c = shift; return bless {}, ref($c) || $c }
sub import_from { }
sub param   { }
sub vars    { return () }
sub get_block { return {} }
sub set_block { }
sub write   { 1 }
sub save    { 1 }
sub error   { '' }
1;
