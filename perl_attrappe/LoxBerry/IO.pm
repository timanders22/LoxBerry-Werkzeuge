package LoxBerry::IO; use strict; use warnings;
require Exporter; our @ISA=('Exporter');
our @EXPORT = qw(mshttp_send mshttp_send_mem mshttp_get msudp_send mqtt_connectiondetails);
sub mshttp_send {} sub mshttp_send_mem {} sub mshttp_get {} sub msudp_send {} sub mqtt_connectiondetails {}
1;
