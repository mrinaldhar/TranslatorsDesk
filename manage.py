#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()
import os
import sys
import subprocess
from flask import Flask, render_template, session, request
from flask_script import Manager, Shell, Server
from flask_migrate import MigrateCommand
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect
from translatorsdesk.app import create_app
from translatorsdesk.user.models import User
from translatorsdesk.settings import DevConfig, ProdConfig
from translatorsdesk.database import db
from translatorsdesk.spellchecker import dictionaries as spellcheckers
import random, hashlib, json

import logging
logging.basicConfig()

if os.environ.get("TRANSLATORSDESK_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)
app.debug = True
socketio = SocketIO(app)
HERE = os.path.abspath(os.path.dirname(__file__))


"""
    Handles Socket.IO events 
    TODO : Move this block of code to a more appropriate location
"""
@socketio.on('translanslators_desk_echo', namespace='/td')
def test_message(message):
    emit('translanslators_desk_echo_response', message)

@socketio.on('translanslators_desk_get_word_suggesstion', namespace='/td')
def translanslators_desk_get_word_suggesstion(message):
    word = message['data'].encode('utf-8')
    lang = message['lang']
    # Check if its a supported language
    if lang in ['hi', 'en', 'te', 'ta', 'pa']:
        # suggestions = spellcheckers[lang].suggest(word)
        suggestions = spellcheckers[lang].suggest( unicode(word, 'utf-8').encode(spellcheckers["encodings"][lang]) )
        emit("translanslators_desk_get_word_suggesstion_" \
            + hashlib.md5(word.lower()).hexdigest(), \
            json.dumps(suggestions))


@socketio.on('connect', namespace='/td')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/td')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, use_reloader=True)
