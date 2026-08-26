package LoxBerry::Log; use strict; use warnings;
require Exporter; our @ISA=('Exporter');
our @EXPORT = qw(LOGSTART LOGEND LOGDEB LOGINF LOGOK LOGWARN LOGERR LOGCRIT LOGALERT LOGEMERGE LOGTITLE);
sub new { bless {}, shift } sub LOGSTART($) {} sub LOGEND(;$) {} sub LOGDEB($) {}
sub LOGINF($) {} sub LOGOK($) {} sub LOGWARN($) {} sub LOGERR($) {} sub LOGCRIT($) {}
sub LOGALERT($) {} sub LOGEMERGE($) {} sub LOGTITLE($) {}
1;
