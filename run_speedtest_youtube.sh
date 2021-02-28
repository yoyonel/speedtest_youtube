#sudo apt install gnuplot-x11

# sudo -H pip3 install --upgrade youtube-dl

# https://www.gnu.org/software/coreutils/manual/html_node/numfmt-invocation.html
# https://stackoverflow.com/questions/13570327/how-to-delete-a-substring-using-shell-script
# https://superuser.com/questions/1107680/how-to-use-sed-with-piping
# https://unix.stackexchange.com/questions/190337/how-can-i-make-a-graphical-plot-of-a-sequence-of-numbers-from-the-standard-input
# https://unix.stackexchange.com/questions/145978/replace-multiple-spaces-with-one-using-tr-only
#YOUTUBE_URI=6pxRHBw-k8M; \
#youtube-dl \
#    -f best --no-part --no-cache-dir \
#    -o /dev/null \
#    --newline \
#    --geo-bypass-country FR \
#    "https://youtu.be/${YOUTUBE_URI}" | \
#grep "[download].*B/s" | \
#tr -s " " | \cut -d' ' -f2,6 | sed 's/B\/s//g' | \
#numfmt --from=iec-i | numfmt --to=iec | \
#gnuplot -p -e 'set title "Youtube SpeedTest"; set xlabel "Time (s)"; set ylabel "Download rate (MBi/s)"; plot "/dev/stdin"'

rm -f /tmp/speedtest_youtube.plt
poetry run python app.py > /tmp/speedtest_youtube.plt
gnuplot -p -e 'set term dumb 120 26; set title "Youtube SpeedTest"; set xlabel "% of dl completion"; set ylabel "Download rate (MBi/s)"; plot "/tmp/speedtest_youtube.plt" with linespoints smooth csplines ls 1'
