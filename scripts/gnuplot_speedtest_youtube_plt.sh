#!/usr/bin/env sh
gnuplot -p -e '
set term dumb 120 26; 
set title "Youtube SpeedTest"; 
set xlabel "% of dl completion"; 
set ylabel "Download rate (MBi/s)"; 
plot "/tmp/speedtest_youtube.plt" with linespoints smooth csplines ls 1'