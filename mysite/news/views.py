# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
import redis
import json

def index(request):
    r = RSS_Storage()

    latest_news_list = [] 
    data = r.get_list_data(0, 100) 
    for d in data :
        latest_news_list.append(json.loads(d))

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
