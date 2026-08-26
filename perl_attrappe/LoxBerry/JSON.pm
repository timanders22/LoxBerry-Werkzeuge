package LoxBerry::JSON;

# Attrappe des LoxBerry-Kernmoduls LoxBerry::JSON.
#
# WOFUER SIE TAUGT UND WOFUER NICHT
#
# Sie taugt fuer "perl -c", also fuer die Frage, ob ein Plugin-Skript
# syntaktisch in Ordnung ist. Bis zum 26.08.2026 gab es sie nicht, und
# deshalb liess sich kein Plugin, das LoxBerry::JSON einbindet, ueberhaupt
# uebersetzen - die Pflichtpruefung fiel fuer diese Linien stillschweigend
# aus.
#
# Sie taugt NICHT als Gegenstelle fuer einen Lauf. open() liest die Datei
# wirklich und gibt die Struktur zurueck, write() schreibt sie zurueck -
# aber ohne die Sperren, die Zwischenspeicher und das Verhalten des
# Originals bei beschaedigten Dateien. Wer damit einen Durchlauf misst,
# misst die Attrappe.
#
# Die Richtung, in der eine Attrappe abweichen darf, ist nicht beliebig:
# nachsichtiger als das Original nur bei der UMGEBUNG, nie bei der
# SCHNITTSTELLE. Deshalb kennt sie genau die vier Aufrufe, die der Bestand
# benutzt, und keinen erfundenen fuenften.

use strict;
use warnings;

our $VERSION = '0.1-attrappe';

sub new
{
	my ($class, %args) = @_;
	my $self = { datei => undef, daten => undef, readonly => 0, %args };
	return bless $self, $class;
}

# open(filename => ..., readonly => 0|1) - gibt eine Referenz auf die
# gelesene Struktur zurueck, oder undef.
sub open
{
	my ($self, %args) = @_;
	$self->{datei}    = $args{filename};
	$self->{readonly} = $args{readonly} ? 1 : 0;
	return undef if !defined $self->{datei} || !-e $self->{datei};

	my $roh = '';
	if ( CORE::open(my $fh, '<', $self->{datei}) ) {
		local $/;
		$roh = <$fh>;
		CORE::close($fh);
	}
	return undef if !defined $roh || $roh eq '';

	require JSON::PP;
	my $d = eval { JSON::PP::decode_json($roh) };
	return undef if !$d;
	$self->{daten} = $d;
	return $d;
}

sub write
{
	my ($self) = @_;
	return 0 if $self->{readonly} || !defined $self->{datei} || !defined $self->{daten};
	require JSON::PP;
	my $roh = eval { JSON::PP::encode_json($self->{daten}) };
	return 0 if !defined $roh;
	if ( CORE::open(my $fh, '>', $self->{datei}) ) {
		print $fh $roh;
		CORE::close($fh);
		return 1;
	}
	return 0;
}

sub filename
{
	my ($self) = @_;
	return $self->{datei};
}

1;
