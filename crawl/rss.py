#!/usr/bin/env python
# -*- coding: utf-8 -*-

import feedparser
import redis
import logging
import time
import json
logging.basicConfig(level=logging.DEBUG)


class RSS :

    _RSS_SOURCE = {
        '36kr' : {
            'RSS_URL' : "http://feed.36kr.com/c/33346/f/566026/index.rss"
        },
        'tech2ipo' : {
            'RSS_URL' : "http://tech2ipo.feedsportal.com/c/34822/f/641707/index.rss"
        }
    }

    _redis = None

    def __init__(self):
        self._redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)


    def rss_reader(self) :
        for (k,v) in self._RSS_SOURCE.items() :
            self._cl_rss(k)


    def _cl_rss(self, rss_name):
        """
        crawl and parse the rss
        """
        d = feedparser.parse(self._RSS_SOURCE[rss_name]['RSS_URL']) 
        newtime = int(time.mktime(d.feed.published_parsed))
        oldtime = 0
        # get the older rss header from redis
        hn = self.__redis_name_header(rss_name)
        hres = self._redis.get(hn)
        if None == hres :
            header = d.feed
            header['published_parsed'] = int(time.mktime(header['published_parsed']))
            header['updated_parsed'] = int(time.mktime(header['updated_parsed']))
            self._redis.set(hn, json.dumps(header))
        else :
            old_json = json.loads(hres)
            oldtime = old_json['published_parsed']
        
        if newtime >= oldtime :
            # need update
            for entries in d.entries :
                hash_flag = "%s" % entries['id']
                hash_flag_name = self.__redis_name_hash_flag(rss_name)

                res = self._redis.hget(hash_flag_name, hash_flag)
                if None == res :
                    # need insert list
                    entries['rss_type'] = rss_name
                    entries['published_parsed'] = int(time.mktime(entries['published_parsed']))
                    entries_json = json.dumps(entries)
                    self._redis.rpush("list", entries_json)
                    self._redis.hset(hash_flag_name, hash_flag, "1")
                    # insert the data, key is id
                    name_rss_data = self.__redis_name_rss_data(rss_name, hash_flag)
                    entries['rss_supported_num'] = 0
                    entries['rss_unsupported_num'] = 0
                    entries_json = json.dumps(entries)
                    flag = self._redis.set(name_rss_data, entries_json)
                    if flag > 0 :
                        logging.info("store rss data success! key[%s]" % name_rss_data)
                    else :
                        logging.info("store rss data failed! key[%s]" % name_rss_data)
        return True

    def __redis_name_header(self, rss_name) :
        return "header_%s" % rss_name
    
    def __redis_name_hash_flag(self, rss_name) :
        return "hash_flag_%s" % rss_name

    def __redis_name_rss_data(self, rss_name, rss_id) :
        return "rss_name_%s_%s" % (rss_name, rss_id) 


if __name__ == "__main__" :
    r = RSS()
    r.rss_reader()
