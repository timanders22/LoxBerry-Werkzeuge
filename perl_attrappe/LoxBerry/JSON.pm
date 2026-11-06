#!/usr/bin/perl
# "use JSON;" STEHT HIER OBEN, VOR DER package-ZEILE - das ist kein
# Schoenheitsfehler, sondern der Nachbau des Originals.
#
# /opt/loxberry/libs/perllib/LoxBerry/JSON.pm hat in Zeile 2 "use JSON;",
# waehrend "package LoxBerry::JSON;" erst in Zeile 6 kommt (am 07.09.2026
# an der Anlage gelesen). Zum Zeitpunkt des Imports ist das laufende Paket
# also noch MAIN - JSON.pm setzt encode_json und decode_json mit dem
# Prototyp ($) unmittelbar in den Namensraum des AUFRUFERS.
#
# Genau daran haengt ein Fehler, der acht Fassungen lang durchging: ein
# Plugin, das nach LoxBerry::JSON noch "use JSON::PP qw(decode_json)"
# einband, bekam auf der Anlage bei JEDEM Lauf
#
#     Prototype mismatch: sub main::decode_json ($) vs none
#
# Gegen diese Attrappe kam die Meldung nie, weil hier weder "use JSON;"
# noch ein Prototyp stand. Beides ist am 07.09.2026 nachgetragen und in
# beide Richtungen geeicht (Smartmeter classic 2.7.2 meldet, 2.8.0 nicht).
# Eine Attrappe darf nachsichtiger sein als das Original bei der UMGEBUNG,
# nie bei der SCHNITTSTELLE - und ein Prototyp gehoert zur Schnittstelle.
use JSON;

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
