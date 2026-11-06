package LoxBerry::System; use strict; use warnings;
require Exporter; our @ISA=('Exporter');
our ($lbhomedir,$lbpplugindir,$lbpconfigdir,$lbpdatadir,$lbplogdir,$lbptemplatedir,$lbpbindir,$lbphtmlauthdir,$lbphtmldir,$lbsconfigdir,$lbstemplatedir);
our @EXPORT = qw($lbhomedir $lbpplugindir $lbpconfigdir $lbpdatadir $lbplogdir $lbptemplatedir $lbpbindir $lbphtmlauthdir $lbphtmldir $lbsconfigdir $lbstemplatedir
                 trim ltrim rtrim begins_with is_enabled is_disabled);
sub get_miniservers {} sub pluginversion {} sub lbhostname {}

# ---------------------------------------------------------------------------
# Ab hier NACHGEBAUT, nicht leer gelassen.
#
# ANLASS (28.08.2026): begins_with und trim fehlten ganz - ein Helfer, der sie
# benutzt, starb mit "Undefined subroutine". Schlimmer war is_enabled: es stand
# als `sub is_enabled {}` da und lieferte damit IMMER undef. Ein Pruefstand, der
# so misst, sieht jeden Schalter als ausgeschaltet und meldet trotzdem gruen.
#
# Die Antworten folgen dem echten LoxBerry::System (LoxBerry/System/General.pm),
# nicht dem Gefuehl: "check", "checked", "selected" sind dort ebenfalls wahr,
# weil HTML-Formulare sie so liefern.
# ---------------------------------------------------------------------------
sub trim  { my $s = shift; return undef if !defined $s; $s =~ s/^\s+|\s+$//g; return $s; }
sub ltrim { my $s = shift; return undef if !defined $s; $s =~ s/^\s+//;       return $s; }
sub rtrim { my $s = shift; return undef if !defined $s; $s =~ s/\s+$//;       return $s; }

sub begins_with { my ($s, $p) = @_; return 0 if !defined $s || !defined $p;
                  return substr($s, 0, length($p)) eq $p; }

sub is_enabled {
	my $t = shift; return undef if !defined $t;
	$t = lc trim($t);
	return 1 if grep { $_ eq $t } qw(true yes on enabled enable 1 check checked select selected);
	return undef;
}
sub is_disabled {
	my $t = shift; return undef if !defined $t;
	$t = lc trim($t);
	return 1 if grep { $_ eq $t } qw(false no off disabled disable 0);
	return undef;
}
1;
