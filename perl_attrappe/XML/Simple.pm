# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
package XML::Simple;
require Exporter; our @ISA = ('Exporter');
our @EXPORT    = qw(XMLin XMLout);
our @EXPORT_OK = qw(XMLin XMLout);
our $VERSION = '0.00_attrappe';
sub new { my $c = shift; return bless {}, ref($c) || $c }
sub XMLin  { return {} }
sub XMLout { return '' }
1;
