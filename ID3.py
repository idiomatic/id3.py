#!/usr/bin/env python
# -*- mode: python -*-

import re
import struct
import types

def items_in_order(dict, order=[]):
    """return all items of dict, but starting in the specified order."""
    done = { }
    items = [ ]
    for key in order + dict.keys():
        if not done.has_key(key) and dict.has_key(key):
            done[key] = None
            items.append((key, dict[key]))
    return items


class UnsupportedID3:
    pass

class InvalidMP3:
    pass

genres = [
    'Blues', 'Classic Rock', 'Country', 'Dance', 'Disco', 'Funk',
    'Grunge', 'Hip-Hop', 'Jazz', 'Metal', 'New Age', 'Oldies', 'Other',
    'Pop', 'R&B', 'Rap', 'Reggae', 'Rock', 'Techno', 'Industrial',
    'Alternative', 'Ska', 'Death Metal', 'Pranks', 'Soundtrack',
    'Euro-Techno', 'Ambient', 'Trip-Hop', 'Vocal', 'Jazz+Funk', 'Fusion',
    'Trance', 'Classical', 'Instrumental', 'Acid', 'House', 'Game',
    'Sound Clip', 'Gospel', 'Noise', 'Alt. Rock', 'Bass', 'Soul',
    'Punk', 'Space', 'Meditative', 'Instrum. Pop', 'Instrum. Rock',
    'Ethnic', 'Gothic', 'Darkwave', 'Techno-Indust.', 'Electronic',
    'Pop-Folk', 'Eurodance', 'Dream', 'Southern Rock', 'Comedy',
    'Cult', 'Gangsta', 'Top 40', 'Christian Rap', 'Pop/Funk', 'Jungle',
    'Native American', 'Cabaret', 'New Wave', 'Psychadelic', 'Rave',
    'Showtunes', 'Trailer', 'Lo-Fi', 'Tribal', 'Acid Punk', 'Acid Jazz',
    'Polka', 'Retro', 'Musical', 'Rock & Roll', 'Hard Rock', 'Folk',
    'Folk/Rock', 'National Folk', 'Swing', 'Fusion', 'Bebob', 'Latin',
    'Revival', 'Celtic', 'Bluegrass', 'Avantgarde', 'Gothic Rock',
    'Progress. Rock', 'Psychadel. Rock', 'Symphonic Rock', 'Slow Rock',
    'Big Band', 'Chorus', 'Easy Listening', 'Acoustic', 'Humour',
    'Speech', 'Chanson', 'Opera', 'Chamber Music', 'Sonata', 'Symphony',
    'Booty Bass', 'Primus', 'Porn Groove', 'Satire', 'Slow Jam',
    'Club', 'Tango', 'Samba', 'Folklore', 'Ballad', 'Power Ballad',
    'Rhythmic Soul', 'Freestyle', 'Duet', 'Punk Rock', 'Drum Solo',
    'A Capella', 'Euro-House', 'Dance Hall', 'Goa', 'Drum & Bass',
    'Club-House', 'Hardcore', 'Terror', 'Indie', 'BritPop', 'Negerpunk',
    'Polsk Punk', 'Beat', 'Christian Gangsta Rap', 'Heavy Metal',
    'Black Metal', 'Crossover', 'Contemporary Christian', 'Christian Rock',
    'Merengue', 'Salsa', 'Thrash Metal', 'Anime', 'Jpop', 'Synthpop',
    ]

frame_id_names = {
    'BUF' : 'Recommended buffer size',
    'CNT' : 'Play counter',
    'COM' : 'Comments',
    'CRA' : 'Audio encryption',
    'CRM' : 'Encrypted meta frame',
    'ETC' : 'Event timing codes',
    'EQU' : 'Equalization',
    'GEO' : 'General encapsulated object',
    'IPL' : 'Involved people list',
    'LNK' : 'Linked information',
    'MCI' : 'Music CD Identifier',
    'MLL' : 'MPEG location lookup table',
    'PIC' : 'Attached picture',
    'POP' : 'Popularimeter',
    'REV' : 'Reverb',
    'RVA' : 'Relative volume adjustment',
    'SLT' : 'Synchronized lyric/text',
    'STC' : 'Synced tempo codes',
    'TAL' : 'Title',
    'TBP' : 'Beats per minute',
    'TCM' : 'Composer',
    'TCO' : 'Content type',
    'TCR' : 'Copyright message',
    'TDA' : 'Date',
    'TDY' : 'Playlist delay',
    'TEN' : 'Encoded by',
    'TFT' : 'File type',
    'TIM' : 'Time',
    'TKE' : 'Initial key',
    'TLA' : 'Language(s)',
    'TLE' : 'Length',
    'TMT' : 'Media type',
    'TOA' : 'Original artist(s)/performer(s)',
    'TOF' : 'Original filename',
    'TOL' : 'Original Lyricist(s)/text writer(s)',
    'TOR' : 'Original release year',
    'TOT' : 'Original album/Movie/Show title',
    'TP1' : 'Lead artist(s)/Lead performer(s)/Soloist(s)/Performing group',
    'TP2' : 'Band/Orchestra/Accompaniment',
    'TP3' : 'Conductor/Performer refinement',
    'TP4' : 'Interpreted, remixed, or otherwise modified by',
    'TPA' : 'Part of a set',
    'TPB' : 'Publisher',
    'TRC' : 'ISRC (International Standard Recording Code)',
    'TRD' : 'Recording dates',
    'TRK' : 'Track number/Position in set',
    'TSI' : 'Size',
    'TSS' : 'Software/hardware and settings used for encoding',
    'TT1' : 'Content group description',
    'TT2' : 'Title/Songname/Content description',
    'TT3' : 'Subtitle/Description refinement',
    'TXT' : 'Lyricist/text writer',
    'TXX' : 'User defined text information frame',
    'TYE' : 'Year',
    'UFI' : 'Unique file identifier',
    'ULT' : 'Unsychronized lyric/text transcription',
    'WAF' : 'Official audio file webpage',
    'WAR' : 'Official artist/performer webpage',
    'WAS' : 'Official audio source webpage',
    'WCM' : 'Commercial information',
    'WCP' : 'Copyright/Legal information',
    'WPB' : 'Publishers official webpage',
    'WXX' : 'User defined URL link frame',
    }

text_frame_ids = ( 'TT1', 'TT2', 'TT3', 'TP1', 'TP2', 'TP3', 'TP4',
                   'TCM', 'TXT', 'TLA', 'TCO', 'TAL', 'TPA', 'TRK',
                   'TRC', 'TYE', 'TDA', 'TIM', 'TRD', 'TMT', 'TFT',
                   'TBP', 'TCR', 'TPB', 'TEN', 'TSS', 'TOF', 'TLE',
                   'TSI', 'TDY', 'TKE', 'TOT', 'TOA', 'TOL', 'TOR',
                   'IPL' )

_genre_number_re = re.compile("^\((\d+)\)$")
_track_re        = re.compile("^(\d+)/(\d+)$")

def _nts(s):
    null = s.find('\0')
    if null:
        return s[:null]
    return s

def _unpack_non_negative_octet_28_bit_int(n):
    return (((n & 0x7f000000) >> 3)
            + ((n & 0x7f0000) >> 2)
            + ((n & 0x7f00) >> 1)
            + (n & 0x7f))

def _pack_non_negative_ocket_28_bit_int(n):
    return (((n & 0xfe00000) << 3)
            + ((n & 0x1fc000) << 2)
            + ((n & 0x3f80) << 1)
            + (n & 0x7f))

def _unpack_genre(s):
    m = _genre_number_re.match(s)
    if m:
        return genres[int(m.group(1))]
    return s

def _pack_genre(s):
    s = s.lower()
    for i in range(len(genres)):
        if s == genres[i].lower():
            return "(%d)" % (i,)
    return s

def _unpack_track(s):
    m = _track_re.match(s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return (int(track), 0)

def _pack_track(track, tracks):
    return "%d/%d" % (track, tracks)

def _unpack_str(s):
    if s[0] == "\0":
        return s[1:]
    raise UnsupportedID3

def _pack_str(s):
    if type(s) is types.StringType:
        return "\0" + s
    raise UnsupportedID3

class id3_file:

    def __init__(self, f):
        self._f = f
        self._order = [ ]
        self._version = None
        self._read_length = 0
        self._write_length = 0

    def _read(self, length):
        self._read_length += length
        return self._f.read(length)

    def _read_unpack(self, format, exception=InvalidMP3):
        data = self._read(struct.calcsize(format))
        if not data:
            raise exception
        data = struct.unpack(format, data)
        if len(data) == 1:
            return data[0]
        return data

    def _read_id3_v1(self):
        id3 = self._read_unpack('30s30s30s4s30sB')
        title, artist, album, year, comment, genre = id3
        track = ord(comment[-1])
        if track and ord(comment[-2]) == 0:
            comment = comment[:-2]
        else:
            track = None
        self.title   = _nts(title)
        self.artist  = _nts(artist)
        self.album   = _nts(album)
        self.year    = _nts(year)
        self.genre   = genres[genre]
        self.comment = _nts(comment)
        if track is None:
            self.version = self._version = "1.0"
        else:
            self.version = self._version = "1.1"
            self.track = track

    def _read_id3_v2(self):
        major_version, minor_version, flags = self._read_unpack('>BBB')

        self._version = "2.%d.%d" % (major_version, minor_version)
        self.version = self._version
    
        if flags & 0x20:
            # extended header
            raise UnsupportedID3
    
        if major_version == 2:
            return self._read_id3_v2_2()
        elif major_version == 3:
            return self._read_id3_v2_3()
        else:
            raise UnsupportedID3
    
    def _read_id3_v2_3(self):
        self.raw = raw = { }
        self._order = order = [ ]
        size = self._read_unpack('>L')
        size = _unpack_non_negative_octet_28_bit_int(size)
        #print "size", size
        while size > 0:
            id, frame_size, flags = self._read_unpack('>4sLH')
            size -= 10
            if flags:
                raise UnsupportedID3
            if frame_size:
                size -= frame_size
                data = self._read(frame_size)
                if id == "\0\0\0\0":
                    continue
                if raw.has_key(id):
                    # duplicates?
                    raise UnsupportedID3
                raw[id] = data
                order.append(id)

        self.title   = _unpack_str(raw.get('TIT2', "\0"))
        self.artist  = _unpack_str(raw.get('TPE1', "\0"))
        self.album   = _unpack_str(raw.get('TALB', "\0"))
        self.year    = _unpack_str(raw.get('TYER', "\0"))
        self.comment = _unpack_str(raw.get('COMM', "\0"))
        self.genre   = _unpack_genre(_unpack_str(raw.get('TCON', "\0")))
        track        = _unpack_str(raw.get('TRCK', "\0000"))
        self.track, self.tracks = _unpack_track(track)

    def _read_id3_v2_2(self):
        self.raw = raw = { }
        size = self._read_unpack('>L')
        size = _unpack_non_negative_octet_28_bit_int(size)
        # frames
        while size > 0:
            id, frame_size = self._read_unpack('>3s3s')
            frame_size = (struct.unpack('>L', '\0' + frame_size))[0]
            size -= 6
            if frame_size:
                size -= frame_size
                data = self._read(frame_size)
                if raw.has_key(id):
                    # duplicates?
                    raise UnsupportedID3
                raw[id] = data

        if raw.has_key('UFI'):
            raw['UFI'] = (raw['UFI'][0], raw['UFI'][1:])
        for id in text_frame_ids:
            if raw.has_key(id):
                raw[id] = _unpack_str(raw[id])
        if raw.has_key('TXX'):
            raw['TXX'] = (_unpack_str(raw['TXX']).split('\0', 1))
        if raw.has_key('COM'):
            raw['COM'] = (_unpack_str(raw['COM']).split('\0'))

        self.title   = raw.get('TT2', '')
        self.artist  = raw.get('TP1', '')
        self.album   = raw.get('TAL', '')
        self.year    = raw.get('TYE', '')
        self.comment = raw.get('COM', '')
        self.genre   = _unpack_genre(raw.get('TCO', ''))
        track        = raw.get('TRK', '0')
        self.track, self.tracks = _unpack_track(track)

    def read(self):
        magic = self._read_unpack('>3s')
        if magic == 'ID3':
            self._read_id3_v2()
            return self

        self._f.seek(128, 2)         # last 128 bytes
        tag = self._read_unpack('3s')
        if tag == 'TAG':
            self._read_id3_v1()
            return self

        raise InvalidMP3


    def _write(self, data):
        self._write_length += len(data)
        self._f.write(data)

    def _pad(self):
        self._write("\0" * (self._read_length - self._write_length))
        self._write_length = 0

    def _write_pack(self, format, *values):
        data = apply(struct.pack, [ format ] + list(values))
        return self._write(data)

    def _write_id3_v2_3(self):
        self._f.seek(0)
        raw = self.raw.copy()

        if self.title:
            raw['TIT2'] = _pack_str(self.title)
        if self.artist:
            raw['TPE1'] = _pack_str(self.artist)
        if self.album:
            raw['TALB'] = _pack_str(self.album)
        if self.year:
            raw['TYER'] = _pack_str(self.year)
        if self.comment:
            raw['COMM'] = _pack_str(self.comment)
        if self.genre:
            raw['TCON'] = _pack_str(_pack_genre(self.genre))
        if self.track:
            raw['TRCK'] = _pack_str(_pack_track(self.track, self.tracks))

        # order of:
        # 1) original key order
        # 2) title, artist, album, year, comment, genre, tracks
        # 3) anything else added since read()
        front_keys = [ 'TIT2', 'TPE1', 'TALB', 'TYER', 'COMM', 'TCON', 'TRCK' ]
        data = [ ]
        for k,v in items_in_order(raw, self._order + front_keys):
            data.append(struct.pack('>4sLH', k, len(v), 0x0) + v)
        data = "".join(data)
        if len(data) > self._read_length:
            raise InvalidMP3
        length = max(len(data), self._read_length - 10)

        self._write('ID3')
        self._write_pack('>BBB', 3, 0, 0x0)
        self._write_pack('>L', _pack_non_negative_ocket_28_bit_int(length))
        self._write(data)
        self._pad()

    def _write_id3_v2_2(self):
        raise UnsupportedID3
        self._f.seek(0)
        pass

    def _write_id3_v1(self):
        raise UnsupportedID3
        self._f.seek(128, 2)
        pass

    def write(self):
        version = (getattr(self, '_version', None)
                   or getattr(self, 'version', None))
        if version == "2.3.0":
            self._write_id3_v2_3()
        elif version == "2.2.0":
            self._write_id3_v2_2()
        elif version == "1.1":
            self._write_id3_v1()
        elif version == "1.0":
            self._write_id3_v1()


#def info(filename):
#    f = open(filename, 'rb')
#    try:
#        return id3().read(f).attributes()
#    finally:
#        f.close()

# composer
# disc
# part_of_a_compilation
# volume_adjustment
# equalizer_preset
# my_rating
# start_time
# stop_time

def test(filename="2_3.mp3"):
    import StringIO
    f = open(filename)
    i = id3_file(f)
    i.read()
    i._f = StringIO.StringIO()
    i.write()
    v = i._f.getvalue()
    f.seek(0)
    v2 = f.read(len(v))
    f.close()
    return v == v2

def scan():
    import os
    def walkfn(arg, dir, files):
        for filename in files:
            if filename[-4:] == '.mp3':
                filename = os.path.join(dir, filename)
                if not test(filename):
                    print filename
    os.path.walk('.', walkfn, 0)

if __name__ == '__main__':
    scan()
