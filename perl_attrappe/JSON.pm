# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
#
# EINE AUSNAHME: die PROTOTYPEN von encode_json und decode_json sind echt.
# Am 07.09.2026 an der Anlage gemessen (JSON.pm 4.10, aarch64):
#
#     prototype(\&JSON::decode_json) = ($)
#     prototype(\&JSON::encode_json) = ($)
#
# Sie stehen hier, weil ihr Fehlen einen echten Fehler acht Fassungen lang
# verdeckt hat. fetch_vzlogger.pl band nach LoxBerry::JSON zusaetzlich
# "use JSON::PP qw(decode_json)" ein - JSON::PP exportiert ohne Prototyp,
# und Exporter meldete deshalb bei JEDEM Lauf auf der Anlage:
#
#     Prototype mismatch: sub main::decode_json ($) vs none
#
# Gegen diese Attrappe kam die Meldung nie, weil hier kein Prototyp stand.
# Eine Attrappe darf nachsichtiger sein als das Original bei der UMGEBUNG,
# nie bei der SCHNITTSTELLE - und ein Prototyp gehoert zur Schnittstelle.
package JSON;
require Exporter; our @ISA = ('Exporter');
our @EXPORT    = qw(encode_json decode_json to_json from_json);
our @EXPORT_OK = qw(encode_json decode_json to_json from_json);
our $VERSION = '0.00_attrappe';
sub new { my $c = shift; return bless {}, ref($c) || $c }
sub encode_json ($) { '' } sub decode_json ($) { {} }
sub to_json { '' }     sub from_json { {} }
sub encode { '' }      sub decode { {} }
sub utf8 { $_[0] } sub pretty { $_[0] } sub canonical { $_[0] }
sub allow_nonref { $_[0] } sub allow_blessed { $_[0] } sub convert_blessed { $_[0] }
1;
