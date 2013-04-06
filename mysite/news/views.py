# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from operator import itemgetter
import redis
import json

def index(request):
    r = RSS_Storage()
    link_map = {}

    latest_news_list = [] 
    data = r.get_list_data(0, 500) 
    for d in data :
        jd = json.loads(d)
        if False == link_map.has_key(jd['link']) :
            latest_news_list.append(jd)
            link_map[jd['link']] = True

    latest_news_list = sorted(latest_news_list, key=itemgetter('published_parsed'), reverse=True)

    template = loader.get_template('news/index.html') 
    context = Context({
        'latest_news_list' : latest_news_list,
    })
    return HttpResponse(template.render(context))


class RSS_Storage :
    _redis = None 
    
    def __init__(self) :
        self._redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    def get_list_data(self, start=0, num=10) :
        return self._redis.lrange("list", start, num)
