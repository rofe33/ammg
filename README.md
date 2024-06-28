# Apple Music Metadata Grabber (ammg)

ammg  is a  tool for  appending metadata  to music
files  from Apple  Music. Mainly  files downloaded
from Youtube Music  (not youtube), because Youtube
Music (albums/singles/ep) and Apple Music (albums)
holds the same song info...

With ammg you choose your youtube music songs, and
you choose which metadata.

__Note:__  Supported file  types  are __m4a__  and
__opus__.  Using __opus__  is better  than __m4a__
because the  best quality available on  youtube is
__opus__.

However __m4a__  is used if  you want to  open the
files in iTunes and sync them to your iPhone/iPad.

## Usage

- __First:__ Choose your song, album, or single.
- __Second:__ Download the __album playlist__ from Youtube Music.
- __Third:__ Copy the __album ID__ from the search bar from Apple Music.

__Example:__   We  will   be  downloading   `Scary
Pockets,  Elise Trouw  -  Careless Whisper  (feat.
Dave Koz)`.

- Apple Music link: https://music.apple.com/us/album/careless-whisper-feat-dave-koz-single/1681177202
    - Album ID: 1681177202
- Youtube Music link: https://music.youtube.com/playlist?list=OLAK5uy_kVIMiCrxX4gmnZI-IufqRvJte6Hk3NTbY

>   Notice:   the   Youtube  Music   link   is   a
> __playlist__. By downloading  using the __playlist
> (album link)__,  you will be able  to add metadata
> without manual intervetion.

__Command  Process:__  Download  the  music  using
[yt-dlp](https://github.com/yt-dlp/yt-dlp)   (make
sure you download yt-dlp first).

- __Downloading__ `.opus` file using `yt-dlp`:

```sh
yt-dlp -cw -o "music/%(title)s.%(ext)s" -x --audio-quality "0" "https://music.youtube.com/playlist?list=OLAK5uy_kVIMiCrxX4gmnZI-IufqRvJte6Hk3NTbY"
```

- __Downloading__ `.m4a` file using `yt-dlp`:

```sh
yt-dlp -cw -o "music/%(title)s.%(ext)s" -x --audio-format m4a --audio-quality "0" "https://music.youtube.com/playlist?list=OLAK5uy_kVIMiCrxX4gmnZI-IufqRvJte6Hk3NTbY"
```

This  will  download  `Careless  Whisper`  in  the
`music`  folder. So  the  path  of the  downloaded
song will  be `music/Careless Whisper  (feat. Dave
Koz).opus`.


__Adding__ the metadata using `ammg`:

__Required__ arguments:

- `-i`: Apple album id.
- `-o`: Output directory.
    - The directory where the file will be once it is saved.
- `positional argument`: here `music` where the downloaded song is.

```sh
ammg get -i 1681177202 -o Ordered_Music music
```

If you are querying a lot of songs in one session,
it is adviced to use `--do-not-check-token`.

```sh
ammg get --do-not-check-token -i 1681177202 -o Ordered_Music music
```

After  embedding   metadata,  the  file   will  be
moved  to `Ordered_Music/S/Scary  Pockets &  Elise
Trouw/Careless   Whisper   (feat.  Dave   Koz)   -
Single/`. That  way we will have  an ordered music
library.

## Simplifying our work

We can using `bash` scripting on Linux, to created
alias  or functions  that simplify  our work,  and
make the process faster.

Alias `domus` to download music:

```sh
alias domus='yt-dlp -cw -o "music/%(title)s.%(ext)s" -x --audio-quality "0"'
```

A shell function that accepts a link and album id:

```sh
domuspp() {
    domus "$1";
    ammg get --do-not-check-token -i "$2" -o Ordered_Music music;
}
```
