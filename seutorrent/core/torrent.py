import bencode

from collections import defaultdict


class Torrent:
    def __init__(self, bdecoded):
        torrent_dict = defaultdict(lambda: None)
        for i in bdecoded:
            torrent_dict[i] = bdecoded[i]

        # Make no assumptions about keys in infodict
        self._info = defaultdict(lambda: None)
        partial_infodict = torrent_dict['info']
        for i in partial_infodict:
            self._info[i] = partial_infodict[i]

        self._announce = torrent_dict['announce']
        self._announce_list = torrent_dict['annouce-list']
        self._creation_date = torrent_dict['creation data']
        self._comment = torrent_dict['comment']
        self._created_by = torrent_dict['created by']
        self._encoding = torrent_dict['encoding']

    @property
    def info(self):
        return self._info

    @property
    def announce(self):
        return self._announce

    @property
    def announce_list(self):
        return self._announce_list

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def comment(self):
        return self._comment

    @property
    def created_by(self):
        return self._created_by

    @property
    def encoding(self):
        return self._encoding

    def is_single_file(self):
        """Returns true if single file or false if multi-file torrent"""
        return 'length' in self._info


def parse_torrent_file(filename):
    with file(filename) as torrent_file:
        bencoded_torrent = torrent_file.read()   
    return Torrent(bencode.bdecode(bencoded_torrent))
