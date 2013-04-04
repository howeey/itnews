#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from news import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
    )
