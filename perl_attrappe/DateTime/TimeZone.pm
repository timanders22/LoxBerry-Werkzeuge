package DateTime::TimeZone;

# Attrappe, so weit der Bestand sie benutzt:
#     DateTime::TimeZone->new(name => 'local')
#     ->offset_for_datetime($dt)
#
# Der Versatz wird gerechnet, nicht erfunden: timegm(localtime(t)) - t ist
# der Abstand der Ortszeit zu UTC in Sekunden, mit Sommerzeit. Beide
# Funktionen stammen aus Kernmodulen.
#
# Ein Name ausser 'local' ist hier NICHT nachgebildet und gibt 0 zurueck -
# das ist sichtbar falsch und damit besser als ein plausibler Versatz, den
# niemand gemessen hat. Der Bestand ruft ausschliesslich 'local'.

use strict;
use warnings;
use Time::Local ();

our $VERSION = '0.1-attrappe';

sub new
{
	my ($class, %a) = @_;
	my $self = { name => defined $a{name} ? $a{name} : 'local' };
	return bless $self, $class;
}

sub name { return $_[0]->{name}; }

sub offset_for_datetime
{
	my ($self, $dt) = @_;
	return 0 if $self->{name} ne 'local';
	my $t = ( defined $dt && ref($dt) && $dt->can('epoch') ) ? $dt->epoch : time();
	return Time::Local::timegm(localtime($t)) - $t;
}

1;
