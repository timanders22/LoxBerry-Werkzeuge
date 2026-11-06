# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
# Werkzeug-P2 (02.10.2026): fehlte; `perl -c WOLF-ISM-NG/bin/wolf_ism8i.pl` brach unter
# einer Perl ohne HTML::Parser (WSL) mit "Can't locate HTML/Entities.pm" ab.
# Schnittstelle wie das Original (HTML::Entities 3.86, gemessen an Git-Perl 02.10.2026):
# @EXPORT encode_entities decode_entities _decode_entities, @EXPORT_OK
# encode_entities_numeric %entity2char %char2entity; keine Prototypen.
package HTML::Entities;
use strict;
require Exporter; our @ISA = ('Exporter');
our $VERSION = '0.00_attrappe';
our @EXPORT = qw(encode_entities decode_entities _decode_entities);
our @EXPORT_OK = qw(%entity2char %char2entity encode_entities_numeric);
our (%entity2char, %char2entity);
sub encode_entities         { return $_[0] }
sub encode_entities_numeric { return $_[0] }
sub decode_entities         { return wantarray ? @_ : $_[0] }
sub _decode_entities        { return }
1;
