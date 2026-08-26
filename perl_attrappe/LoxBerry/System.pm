package LoxBerry::System; use strict; use warnings;
require Exporter; our @ISA=('Exporter');
our ($lbhomedir,$lbpplugindir,$lbpconfigdir,$lbpdatadir,$lbplogdir,$lbptemplatedir,$lbpbindir,$lbphtmlauthdir,$lbphtmldir,$lbsconfigdir,$lbstemplatedir);
our @EXPORT = qw($lbhomedir $lbpplugindir $lbpconfigdir $lbpdatadir $lbplogdir $lbptemplatedir $lbpbindir $lbphtmlauthdir $lbphtmldir $lbsconfigdir $lbstemplatedir);
sub get_miniservers {} sub pluginversion {} sub lbhostname {} sub is_enabled {} sub is_disabled {}
1;
