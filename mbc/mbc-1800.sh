cd /home/yslee/kbs-ebs-streaming
$pid_player

ffmpeg -i $(curl -s https://sminiplay.imbc.com/aacplay.ashx?agent=webapp&channel=mfm | head -2 | tail -1 | cut -d= -f2-) -acodec mp3 mbc-test.mp3 > /dev/null 2>&1  &
pid_player=$!
sleep 7200

kill $pid_player

today=`date +%y%m%d%H%M`
mv mbc-test.mp3 mbc-$today.mp3
id3tool -r mbcradio mbc-$today.mp3
mv mbc-$today.mp3 /home/yslee/Dropbox/mbc
