# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
package Data::Validate::IP;
require Exporter; our @ISA = ('Exporter');
our @EXPORT_OK = qw(is_ipv4 is_ipv6 is_private_ipv4 is_public_ipv4 is_loopback_ipv4);
our @EXPORT    = @EXPORT_OK;
our $VERSION = '0.00_attrappe';
sub is_ipv4 { } sub is_ipv6 { } sub is_private_ipv4 { }
sub is_public_ipv4 { } sub is_loopback_ipv4 { }
1;
