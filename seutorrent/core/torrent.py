"""
torrent.py

This module drives parsing and handling torrent metadata.

"""

import bencode
import hashlib
import requests
import urllib

from collections import defaultdict

from peer import Peer
from seutorrent import core


class TorrentMeta:
    """A read-only wrapper around a parsed .torrent file"""
    def __init__(self, bdecoded):
        torrent_dict = defaultdict(lambda: None)
        for i in bdecoded:
            torrent_dict[i] = bdecoded[i]

        # Make no assumptions about keys in infodict
        self._info = defaultdict(lambda: None)
        partial_infodict = torrent_dict['info']
        for i in partial_infodict:
            self._info[i] = partial_infodict[i]

        # infohash is calculated when needed and cached
        self._info_hash_gen = partial_infodict
        self._info_hash = None

        self._announce = torrent_dict['announce']
        self._announce_list = torrent_dict['annouce-list']
        self._creation_date = torrent_dict['creation data']
        self._comment = torrent_dict['comment']
        self._created_by = torrent_dict['created by']
        self._encoding = torrent_dict['encoding']

        # Operational Information
        self._peer_list = []
        self._tracker_id = None
        self._interval = None
        self._min_interval = None

    @property
    def info(self):
        return self._info

    @property
    def info_hash(self):
        if self._info_hash is None:
            bencoded = bencode.bencode(self._info_hash_gen)
            self._info_hash = hashlib.sha1(bencoded).digest()
        return self._info_hash

    @property
    def urlencoded_info_hash(self):
        return urllib.quote(self.info_hash, '~')

    @property
    def announce_url(self):
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

    @property
    def total_length(self):
        if self.is_single_file:
            return self.info['length']
        else:
            return sum((x['length'] for x in self.info['files']))

    @property
    def peer_list(self):
        return self._peer_list

    @property
    def tracker_id(self):
        return self._tracker_id

    def is_single_file(self):
        """Returns true if single file or false if multi-file torrent"""
        return 'length' in self._info


class Torrent:
    def __init__(self, torrent_meta, uploaded, downloaded, left, state):
        self.meta = torrent_meta

        self.uploaded = uploaded
        self.downloaded = downloaded
        self.left = left
        self.state = state

        # Acquired from tracker
        self.peer_list = []
        self.tracker_id = None
        self.interval = None
        self.min_interval = None

    @classmethod
    def parse_compact_peers(cls, peers_string):
        #TODO
        pass

    def _announce(self, peer_id, port, event):
        """Announce inclusion in swarm to tracker"""
        headers = {
            'User-Agent': 'Seutorrent-core version %s' % (core.version)
        }
        #TODO compact should be 1, use 0 for now for code ease
        get_params = {
            'info_hash': self.meta.info_hash,
            'peer_id': peer_id,
            'port': port,
            'uploaded': str(self.uploaded),
            'downloaded': str(self.downloaded),
            'left': str(self.left),
            'compact': '0',
            'event': event
        }

        if self.tracker_id is not None:
            get_params['trackerid'] = self.tracker_id

        resp = requests.get(self.announce_url, params=get_params,
                            headers=headers)

        if resp.ok:
            # Convert response to default dict to avoid repetitive checks
            decoded = bencode.bdecode(resp.text)
            announce_response = defaultdict(lambda: None)
            for i in decoded:
                announce_response[i] = decoded[i]

            self.tracker_id = announce_response['tracker id']
            self.interval = announce_response['interval']
            self.min_interval = announce_response['min interval']
            self.peer_list = [Peer(p['ip'], p['port']) for p in
                              announce_response['peers']]
            return announce_response
        else:
            raise RuntimeError("Failed to make HTTP request to tracker")

    def start_or_resume(self):
        pass

    def stop(self):
        pass


def parse_torrent_file(filename):
    """Reads a torrent file at filename, returning a torrent object"""
    with file(filename) as torrent_file:
        bencoded_torrent = torrent_file.read()
    return TorrentMeta(bencode.bdecode(bencoded_torrent))
