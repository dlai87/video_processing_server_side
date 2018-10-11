ffmpeg-2.1.3-64bit-static/ffmpeg -i video/2016-01-30-blur.flv-dec.flv -vcodec copy -acodec copy video/2016-01-30-mux.flv
ffmpeg-2.1.3-64bit-static/ffmpeg -i video/2016-01-30-blur.flv-dec.flv -vcodec libvpx -acodec libvorbis video/2016-01-30-mux.webm
ffmpeg-2.1.3-64bit-static/ffmpeg -i video/2016-01-30-blur.flv-dec.flv -vcodec h264 -acodec libvorbis video/2016-01-30-mux.mp4
ffmpeg-2.1.3-64bit-static/ffmpeg -i video/2016-01-30-blur.flv-dec.flv -vcodec copy -acodec copy video/2016-01-30-blur-mux.flv
ffmpeg-2.1.3-64bit-static/ffmpeg -i video/2016-01-30-blur.flv-dec.flv -vcodec libvpx -acodec libvorbis video/2016-01-30-blur-mux.webm
ffmpeg-2.1.3-64bit-static/ffmpeg -i video/2016-01-30-blur.flv-dec.flv -vcodec h264 -acodec libvorbis video/2016-01-30-blur-mux.mp4
