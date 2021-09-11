# https://stackoverflow.com/questions/123378/command-line-unix-ascii-based-charting-plotting-tool
# set term dumb 120 40;
poetry run python main.py | \
gnuplot -p -e '
set title "Youtube SpeedTest";
set xlabel "% of dl completion";
set ylabel "Download rate (MBi/s)";
plot "/dev/stdin" with linespoints smooth csplines'