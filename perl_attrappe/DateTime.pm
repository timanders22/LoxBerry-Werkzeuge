package DateTime;

# Attrappe des Debian-Pakets libdatetime-perl, so weit der Bestand es
# benutzt.
#
# WOFUER SIE TAUGT
#
# Fuer "perl -c" und fuer die Zeitrechnung, die bin/sm_logger.pl des
# Smartmeter-Plugins braucht. Ohne sie liess sich diese Datei auf diesem
# Rechner nicht uebersetzen - 1742 Zeilen ohne Syntaxpruefung.
#
# Anders als die Attrappe der seriellen Schnittstelle RECHNET diese hier
# wirklich, und das ist kein Widerspruch zur Regel "eine Attrappe erfindet
# nichts": eine Epochensekunde ist Arithmetik ueber Time::Local (Kernmodul)
# und laesst sich nachpruefen, ein Zaehlertelegramm nicht.
#
# Sie kennt GENAU die Aufrufe, die der Bestand benutzt:
#     DateTime->new(year =>, month =>, day =>, hour =>, minute =>,
#                   second =>, nanosecond =>, time_zone =>)
#     ->epoch
# Ein Aufruf, den das Original kennt und diese Datei nicht, soll hier
# abstuerzen - eine Attrappe, die lockerer ist als das Original,
# verschweigt Fehler.

use strict;
use warnings;
use Time::Local ();

our $VERSION = '0.1-attrappe';

sub new
{
	my ($class, %a) = @_;
	my $self = {
		year   => defined $a{year}   ? $a{year}   : 1970,
		month  => defined $a{month}  ? $a{month}  : 1,
		day    => defined $a{day}    ? $a{day}    : 1,
		hour   => defined $a{hour}   ? $a{hour}   : 0,
		minute => defined $a{minute} ? $a{minute} : 0,
		second => defined $a{second} ? $a{second} : 0,
		time_zone => defined $a{time_zone} ? $a{time_zone} : 'floating',
	};
	return bless $self, $class;
}

sub epoch
{
	my ($self) = @_;
	# 'local' rechnet in der Zeitzone des Rechners, alles andere in UTC -
	# genau die beiden Faelle, die der Bestand benutzt.
	if ( $self->{time_zone} eq 'local' ) {
		return Time::Local::timelocal(
			$self->{second}, $self->{minute}, $self->{hour},
			$self->{day}, $self->{month} - 1, $self->{year});
	}
	return Time::Local::timegm(
		$self->{second}, $self->{minute}, $self->{hour},
		$self->{day}, $self->{month} - 1, $self->{year});
}

sub year   { return $_[0]->{year}; }
sub month  { return $_[0]->{month}; }
sub day    { return $_[0]->{day}; }
sub hour   { return $_[0]->{hour}; }
sub minute { return $_[0]->{minute}; }
sub second { return $_[0]->{second}; }

1;
