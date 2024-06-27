# Apple Music Metadata Grabber (ammg)

ammg  is a  tool for  appending metadata  to music
files  from Apple  Music. Mainly  files downloaded
from Youtube Music  (not youtube), because Youtube
Music (albums/singles/ep) and Apple Music (albums)
holds the same song info...

With ammg you choose your youtube music songs, and
you choose which metadata.

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

__Command Process:__ Download the music using `yt-dlp` (make sure you download yt-dlp first).

- For  `android`  (VLC,  Metro...),  and  `linux`
  (MPD...) `.opus` files will work. (Supported)
- If you want to be able to sync to the __Itunes__
  application  on Apple  devices, `.opus`  files are
  not supported  in the Itunes  windows application,
  so `m4a` will be supported in future versions.

__Downloading__ `.opus` file using `yt-dlp`:

```sh
yt-dlp -cw -o "music/%(title)s.%(ext)s" -x --audio-quality "0" "https://music.youtube.com/playlist?list=OLAK5uy_kVIMiCrxX4gmnZI-IufqRvJte6Hk3NTbY"
```

This  will  download  `Careless  Whisper`  in  the
`music` folder.  So the path  of the song  will be
`music/Careless Whisper (feat. Dave Koz).opus`.


__Adding__ the metadata using `ammg`:

```sh
ammg get -i 1681177202 -o Ordered_Music music
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
    ammg get -i "$2" -o Ordered_Music music;
}
```
