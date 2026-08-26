# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
package CGI;
require Exporter; our @ISA = ('Exporter');
our @EXPORT_OK = qw(param header start_html end_html escapeHTML url redirect cookie);
our @EXPORT    = @EXPORT_OK;
our $VERSION = '0.00_attrappe';
sub new { my $c = shift; return bless {}, ref($c) || $c }
sub param { } sub header { '' } sub start_html { '' } sub end_html { '' }
sub escapeHTML { $_[-1] } sub url { '' } sub redirect { '' } sub cookie { }
sub Vars { return {} } sub multi_param { } sub upload { } sub charset { }
1;
