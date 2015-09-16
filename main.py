# -*- coding: utf-8 -*-
import StringIO
import json
import logging
import random
import urllib
import urllib2
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '87689261:AAHTxPjkJawUDj6csNE3eEwGWLSWHWBDeDc'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
	sticker = message.get('sticker')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.decode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)
	var = 2
	if var == 2:
		if sticker:
	        	reply('من ایموجی بات هستم :) بنابراین نظری در مورد استیکر شما ندارم :)')
			var = var -1
			return
	if True:			
	    if text == '/start':
		reply('بات روشن شد.لطفا برای به دست آوردن لیست اسامی ایموجی ها دستور /help رو برام بفرستید :)')
		setEnabled(chat_id, True)
		return
	    if text == '/help':
		reply('شما میتونید اسم ایموجی مورد نظر خودتونو از لیست انتخاب کنید و برام بفرستید تا من بهتون جواب بدم: پوزخند,شادی,شکلک,خندان,خنده-شیرین,خنده,چشمک,لپ-گلی,چشمک,خوش-مزه,پکر,چشم-عاشق,لبخند-مغرورانه,بی-توجه,افسرده,سردرگم,بوس-فرستادن,فریاد-ترس,متعجب,سرخ,ماسکی,کسل,گربه-عاشق,دعا,گربه-ترسان,موشک,قطار,اتوبوس,کشتی,زمین,ماه,ستاره,حلزون,مار,اسب,میمون,هشت-پا,ناامید,عرق-سرد,عصبانی,گریه,رضایت,واقع-بین,مشت,دیس-لایک,لایک,دست-زدن,روح,قلب-تیرخورده,ادم-فضایی,قلب,حاله,خنده-شیطانی,بمب,عینک-افتابی,خنثی,گیج,زبان-درازی,نگران,قهقه,تفنگ.   ترکیبی ها: خودکشی,قدم-زدن,و...')
		return
	    if text == '/about':
		reply('من ایموجی بات هستم و شما میتونید اسم ایموجی مورد نظرتون رو از لیست انتخاب کنید :) برای ارتباط با سازندم هم میتونید به @farbodgame پیام بدید :) سورس من هم روی گیتهاب منتشر شده و میتونید ازش استفاده کنید و لذت ببرید :) https://github.com/farbodgame/emoji-bot/')
		return
	
        # CUSTOMIZE FROM HERE
	if text == 'سلام'.strip():
		reply('سلام :)')
		return
	if text == 'خداحافظ'.strip():
		reply('خداحافظ')
		return       
	if text == 'پوزخند'.strip():
		reply(u'\U0001f601')
		return
	if text == 'شادی'.strip():
		reply(u'\U0001f602')
		return
	if text == 'شکلک'.strip():
		reply(u'\U0001f603')
		return
	if text == 'خندان'.strip():
		reply(u'\U0001f604')
		return
	if text == 'خنده-شیرین'.strip():
		reply(u'\U0001f605')
		return
	if text == 'خنده'.strip():
		reply(u'\U0001f606')
		return
	if text == 'چشمک'.strip():
		reply(u'\U0001f609')
		return
	if text == 'لپ-گلی'.strip():
		reply(u'\U0001f60A')
		return
	if text == 'خوشمزه'.strip():
		reply(u'\U0001f60B')
		return
	if text == 'پکر'.strip():
		reply(u'\U0001f60C')
		return
	if text == 'چشم-عاشق'.strip():
		reply(u'\U0001f60D')
		return
	if text == 'لبخند-مغرورانه'.strip():
		reply(u'\U0001f60F')
		return
	if text == 'افسرده'.strip():
		reply(u'\U0001f614')
		return
	if text == 'بی-توجه'.strip():
		reply(u'\U0001f612')
		return
	if text == 'سردرگم'.strip():
		reply(u'\U0001f616')
		return
	if text == 'بوس-فرستادن'.strip():
		reply(u'\U0001f618')
		return
	if text == 'سرخ'.strip():
		reply(u'\U0001f633')
		return
	if text == 'فریاد-ترس'.strip():
		reply(u'\U0001f631')
		return
	if text == 'متعجب'.strip():
		reply(u'\U0001f632')
		return
	if text == 'ماسک'.strip():
		reply(u'\U0001f637')
		return
	if text == 'کسل'.strip():
		reply(u'\U0001f629')
		return
	if text == 'گربه-عاشق'.strip():
		reply(u'\U0001f63B')
		return
	if text == 'دعا'.strip():
		reply(u'\U0001f64F')
		return
	if text == 'گربه-ترسان'.strip():
		reply(u'\U0001f640')
		return
	if text == 'موشک'.strip():
		reply(u'\U0001f680')
		return
	if text == 'قطار'.strip():
		reply(u'\U0001f684')
		return
	if text == 'اتوبوس'.strip():
		reply(u'\U0001f68C')
		return
	if text == 'کشتی'.strip():
		reply(u'\U0001f6A2')
		return
	if text == 'زمین'.strip():
		reply(u'\U0001f30f')
		return
	if text == 'ماه'.strip():
		reply(u'\U0001f319')
		return
	if text == 'ستاره'.strip():
		reply(u'\U0001f31F')
		return
	if text == 'حلزون'.strip():
		reply(u'\U0001f40C')
		return
	if text == 'مار'.strip():
		reply(u'\U0001f40D')
		return
	if text == 'اسب'.strip():
		reply(u'\U0001f40E')
		return
	if text == 'میمون'.strip():
		reply(u'\U0001f412')
		return
	if text == 'هشت-پا'.strip():
		reply(u'\U0001f419')
		return
	if text == 'ناامید'.strip():
		reply(u'\U0001f61E')
		return
	if text == 'عرق-سرد'.strip():
		reply(u'\U0001f630')
		return
	if text == 'عصبانی'.strip():
		reply(u'\U0001f621')
		return
	if text == 'گریه'.strip():
		reply(u'\U0001f622')
		return
	if text == 'رضایت'.strip():
		reply(u'\U0001f623')
		return
	if text == 'واقع-بین'.strip():
		reply(u'\U0001f625')
		return
	if text == 'مشت'.strip():
		reply(u'\U0001f44A')
		return
	if text == 'دیس-لایک'.strip():
		reply(u'\U0001f44E')
		return
	if text == 'لایک'.strip():
		reply(u'\U0001f44D')
		return
	if text == 'دست-زدن'.strip():
		reply(u'\U0001f44F')
		return
	if text == 'روح'.strip():
		reply(u'\U0001f47B')
		return
	if text == 'قلب-تیرخورده'.strip():
		reply(u'\U0001f498')
		return
	if text == 'قلب'.strip():
		reply(u'\U0001f493')
		return
	if text == 'ادم-فضایی'.strip():
		reply(u'\U0001f47D')
		return
	if text == 'حاله'.strip():
		reply(u'\U0001f607')
		return
	if text == 'خنده-شیطانی'.strip():
		reply(u'\U0001f608')
		return
	if text == 'بمب'.strip():
		reply(u'\U0001f4A3')
		return
	if text == 'عینک-افتابی'.strip():
		reply(u'\U0001f60E')
		return
	if text == 'ترسان'.strip():
		reply(u'\U0001f628')
		return
	if text == 'خنثی'.strip():
		reply(u'\U0001f610')
		return
	if text == 'گیج'.strip():
		reply(u'\U0001f615')
		return
	if text == 'زبان-درازی'.strip():
		reply(u'\U0001f61B')
		return
	if text == 'نگران'.strip():
		reply(u'\U0001f61F')
		return
	if text == 'قهقه'.strip():
		reply(u'\U0001f62D')
		return
	if text == 'تفنگ'.strip():
		reply(u'\U0001f52B')
		return
	if text == 'خودکشی'.strip():
		reply(u'\U0001f610'u'\U0001f52B')
		return
	if text == 'قدم-زدن'.strip():
		reply(u'\U0001f60e\u2615\ufe0f\U0001f463')
		return								
	else:
		reply('لطفا نام ایموجی بعدی مورد نظر خود را درست وارد کنید.')
				


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
