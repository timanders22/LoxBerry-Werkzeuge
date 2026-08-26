# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
package File::HomeDir;
require Exporter; our @ISA = ('Exporter');
our @EXPORT_OK = qw(home my_home my_data my_desktop my_documents);
our $VERSION = '0.00_attrappe';
sub home { '' } sub my_home { '' } sub my_data { '' }
sub my_desktop { '' } sub my_documents { '' } sub my_dist_data { '' }
1;
