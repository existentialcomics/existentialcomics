#!/usr/bin/perl

my $LWEBPATH='/var/www/existentialcomics/';
my $LSTATICPATH='/var/www/static/';
my $LDB='/var/www/comic.db';
my $RWEBPATH='/home/thebalrog/webapps/flask/htdocs/existentialcomics/';
#my $RSTATICPATH='/home/thebalrog/webapps/flask/htdocs/static/';
my $RSTATICPATH='/home/thebalrog/webapps/htdocs/';
my $RDB='/home/thebalrog/comic.db';
my $RSYNC='rsync -r -e "ssh -i /home/corey/.ssh/id_dsa" --exclude "*settings.py"';

my $all = shift;
my $test = shift;

my $cmdStatic = "$RSYNC $LSTATICPATH thebalrog\@existentialcomics.com:$RSTATICPATH";
my $cmdDb = "$RSYNC $LDB thebalrog\@existentialcomics.com:$RDB";

my $cmdWeb = "$RSYNC $LWEBPATH thebalrog\@existentialcomics.com:$RWEBPATH";
my $cmdRestart = "ssh -i /home/corey/.ssh/id_dsa thebalrog\@existentialcomics.com \"/home/thebalrog/webapps/flask/apache2/bin/restart\"";

if ($test){
    print "$cmdStatic\n";
    print "$cmdDb\n";
    if ($all eq 'all'){
        print "$cmdWeb\n";
        print "$cmdRestart\n";
    }
} else {
    system($cmdStatic);
    system($cmdDb);
    if ($all eq 'all'){
        system($cmdWeb);
        system($cmdRestart);
    }
}
