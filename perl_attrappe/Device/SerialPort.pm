package Device::SerialPort;

# Attrappe des Debian-Pakets libdevice-serialport-perl.
#
# WOFUER SIE TAUGT UND WOFUER NICHT
#
# Sie taugt fuer "perl -c". Ohne sie liess sich bin/sm_logger.pl des
# Smartmeter-Plugins auf diesem Rechner nicht uebersetzen - 1742 Zeilen, die
# damit von keiner Syntaxpruefung erreicht wurden.
#
# Sie taugt NICHT fuer einen Lauf, und das ist keine Nachlaessigkeit,
# sondern Absicht: eine Attrappe, die eine serielle Schnittstelle
# NACHBILDET, wuerde einen Zaehler nachbilden, den niemand gemessen hat.
# read() liefert deshalb NICHTS und new() gibt undef zurueck, sobald das
# Geraet nicht existiert - wer damit misst, bekommt sofort ein Ergebnis, das
# offensichtlich keines ist, statt eines plausiblen Unsinns.
#
# Die Namen sind aus der Anleitung des Originals uebernommen. Ein Aufruf,
# den das Original nicht kennt, gehoert hier NICHT hinein: eine Attrappe,
# die lockerer ist als das Original, verschweigt Fehler.

use strict;
use warnings;

our $VERSION = '0.1-attrappe';

sub new
{
	my ($class, $device) = @_;
	# Kein Geraet, kein Objekt - genau wie das Original.
	return undef if !defined $device || !-e $device;
	my $self = { device => $device, offen => 1 };
	return bless $self, $class;
}

# Die Einstellungen. Alle geben den gesetzten Wert zurueck, wie im Original.
for my $name (qw(baudrate databits stopbits parity handshake
                 dtr_active rts_active read_char_time read_const_time)) {
	no strict 'refs';
	*{$name} = sub {
		my ($self, $wert) = @_;
		$self->{$name} = $wert if defined $wert;
		return $self->{$name};
	};
}

sub write_settings { return 1; }
sub purge_all      { return 1; }

sub write
{
	my ($self, $daten) = @_;
	return defined $daten ? length($daten) : 0;
}

# Absichtlich stumm: (Anzahl, Daten). Ein Nachbau, der Telegramme
# erfindet, waere die teuerste Art von Attrappe.
sub read
{
	return (0, '');
}

sub close
{
	my ($self) = @_;
	$self->{offen} = 0;
	return 1;
}

1;
