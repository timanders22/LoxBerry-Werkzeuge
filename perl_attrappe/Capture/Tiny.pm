# Attrappe: nur damit `perl -c` laden kann. Kein Verhalten, keine Pruefung.
package Capture::Tiny;
require Exporter; our @ISA = ('Exporter');
our @EXPORT_OK = qw(capture capture_stdout capture_stderr capture_merged
                    tee tee_stdout tee_stderr tee_merged);
our @EXPORT    = @EXPORT_OK;
our $VERSION = '0.00_attrappe';
sub capture (&;@) { return ('', '', 0) }
sub capture_stdout (&;@) { return ('', 0) }
sub capture_stderr (&;@) { return ('', 0) }
sub capture_merged (&;@) { return ('', 0) }
sub tee (&;@) { return ('', '', 0) }
sub tee_stdout (&;@) { return ('', 0) }
sub tee_stderr (&;@) { return ('', 0) }
sub tee_merged (&;@) { return ('', 0) }
1;
