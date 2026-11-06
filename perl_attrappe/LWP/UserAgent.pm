# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
# Werkzeug-P1 (02.10.2026): fehlte; `perl -c WiFi-Scanner-NG/bin/check.pl` brach unter
# einer Perl ohne libwww (WSL) mit "Can't locate LWP/UserAgent.pm" ab, bevor es eine
# Zeile beurteilt hatte. Schnittstelle wie das Original (libwww-perl): exportiert
# nichts, keine Prototypen; die Methoden stehen nur da, damit eine Unterklasse
# (`our @ISA = ('LWP::UserAgent')`) sich laden laesst.
package LWP::UserAgent;
use strict;
our $VERSION = '0.00_attrappe';
sub new             { my $c = shift; return bless {}, ref($c) || $c }
sub get             { return LWP::UserAgent::_Antwort->new }
sub post            { return LWP::UserAgent::_Antwort->new }
sub put             { return LWP::UserAgent::_Antwort->new }
sub head            { return LWP::UserAgent::_Antwort->new }
sub delete          { return LWP::UserAgent::_Antwort->new }
sub request         { return LWP::UserAgent::_Antwort->new }
sub simple_request  { return LWP::UserAgent::_Antwort->new }
sub timeout         { }
sub agent           { }
sub env_proxy       { }
sub ssl_opts        { }
sub credentials     { }
sub default_header  { }
sub default_headers { }
sub max_redirect    { }
sub get_basic_credentials { return (undef, undef) }

package LWP::UserAgent::_Antwort;
sub new             { my $c = shift; return bless {}, ref($c) || $c }
sub is_success      { 0 }
sub is_error        { 1 }
sub code            { 500 }
sub status_line     { '500 Attrappe' }
sub message         { 'Attrappe' }
sub content         { '' }
sub decoded_content { '' }
sub header          { }
1;
