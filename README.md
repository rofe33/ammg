# Download Music with yt-dlp

First download your album using yt-dlp from youtube music.

```sh
# For short create an alias
yt-dlp -cw -o "%(title)s.%(ext)s" -x --audio-quality "0"
```

```sh
alias domus='yt-dlp -cw -o "music/%(title)s.%(ext)s" -x --audio-quality "0"'
```

Then using ammg embed the metadata from apple.

```sh
ammg get -i <album_id> -o Music music
```

A bash function:

```sh
domuspp() {
    domus "$1";
    ammg get -i "$2" -o Music music | less;
}
```
