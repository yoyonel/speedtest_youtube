# List 4k/8k videos on youtube
"8K HDR 60FPS"
longue durée (> 20min): https://www.youtube.com/results?search_query=8K+HDR+60FPS&sp=EgIYAg%253D%253D
courte durée (<  4min): https://www.youtube.com/results?search_query=8K+HDR+60FPS&sp=EgIYAQ%253D%253D

Peru 8K HDR 60FPS (FUHD)
2017
https://youtu.be/1La4QzGeaaQ
[download] 100% of 79.36MiB in 00:02

10 Incredible 4K (Ultra HD) Videos
https://youtu.be/6pxRHBw-k8M
[download] 100% of 35.29MiB in 00:01

The Beauty of 8K (FUHD 4320p)
https://youtu.be/TvWcU3aztmo
[download] 100% of 17.26MiB in 00:00

8k video ultra hd Aerial view of Modern city for 8k hdr tv
https://youtu.be/8cOJhLM66D4
[download] 100% of 150.37MiB in 00:04

Collection Of Animals 8K HDR 60FPS
https://youtu.be/egSvdEJZRBk

2020 LG OLED 8K l The Wild 8K HDR 60fps
https://youtu.be/FrKNa3hruBw

# Shell Script: Speedtest on youtube

```shell
sudo apt install gnuplot-x11

sudo -H pip3 install --upgrade youtube-dl

# https://www.gnu.org/software/coreutils/manual/html_node/numfmt-invocation.html
# https://stackoverflow.com/questions/13570327/how-to-delete-a-substring-using-shell-script
# https://superuser.com/questions/1107680/how-to-use-sed-with-piping
# https://unix.stackexchange.com/questions/190337/how-can-i-make-a-graphical-plot-of-a-sequence-of-numbers-from-the-standard-input
# https://unix.stackexchange.com/questions/145978/replace-multiple-spaces-with-one-using-tr-only
YOUTUBE_URI=6pxRHBw-k8M; \
youtube-dl \
    -f best --no-part --no-cache-dir \
    -o /dev/null \
    --newline \
    --geo-bypass-country FR \
    "https://youtu.be/${YOUTUBE_URI}" | \
grep "[download].*B/s" | \
tr -s " " | \cut -d' ' -f2,6 | sed 's/B\/s//g' | \
numfmt --from=iec-i | numfmt --to=iec | \
gnuplot -p -e 'set title "Youtube SpeedTest"; set xlabel "Time (s)"; set ylabel "Download rate (MBi/s)"; plot "/dev/stdin"'
```

# Run with script shell

```sh
[debian] in ~/PycharmProjects/youtube_speedtest is 📦 v0.1.0 via 🐍 v3.7.3 (youtube-speedtest-RBxHy8ti-py3.7) via 🐏 45%|0% 
🕙[ 12:33:40 ] ➜ /usr/bin/zsh [...]/youtube_speedtest/run_speedtest_youtube.sh

                                                                                                                        
                                                               Youtube SpeedTest                                        
                                                                                                                        
                       35 +-----------------------------------------------------------------------------------------+   
                          |                 +           **    +     ****************              +         **    **|   
                          |                    *********  **********           "/tmp/speedtest_youtube.plt" ******* |   
                       30 |-+            ******                                                                   +-|   
                          |         ******                                                                          |   
                       25 |-+     **                                                                              +-|   
                          |      *                                                                                  |   
                          |     *                                                                                   |   
                       20 |-+  *                                                                                  +-|   
                          |   **                                                                                    |   
                          |  *                                                                                      |   
                       15 |-*                                                                                     +-|   
                          | *                                                                                       |   
                          | *                                                                                       |   
                       10 |*+                                                                                     +-|   
                          |*                                                                                        |   
                        5 |*+                                                                                     +-|   
                          |*                                                                                        |   
                          |                 +                 +                 +                 +                 |   
                        0 +-----------------------------------------------------------------------------------------+   
                          0                 20                40                60                80               100  
                                                              % of dl completion
```