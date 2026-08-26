# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
package JSON;
require Exporter; our @ISA = ('Exporter');
our @EXPORT    = qw(encode_json decode_json to_json from_json);
our @EXPORT_OK = qw(encode_json decode_json to_json from_json);
our $VERSION = '0.00_attrappe';
sub new { my $c = shift; return bless {}, ref($c) || $c }
sub encode_json { '' } sub decode_json { {} }
sub to_json { '' }     sub from_json { {} }
sub encode { '' }      sub decode { {} }
sub utf8 { $_[0] } sub pretty { $_[0] } sub canonical { $_[0] }
sub allow_nonref { $_[0] } sub allow_blessed { $_[0] } sub convert_blessed { $_[0] }
1;
