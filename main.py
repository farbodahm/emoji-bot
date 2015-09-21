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

TOKEN = 'Your Bot Token'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# start connecting to telegrom bot api

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# enable bot if user send /start

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# get userid,text and date for logging and reply

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
	#a loop that send the reply only once
	var = 2
	if var == 2:
		if sticker:
	        	reply('من ایموجی بات هستم :) بنابراین نظری در مورد استیکر شما ندارم :)')
			var = var -1
			return

	text2 = text.decode('utf-8')
	logging.info(text2)

	if True:			
	    if text == '/start':
		reply('بات روشن شد.لطفا برای به دست آوردن لیست اسامی ایموجی ها دستور /help رو برام بفرستید :)')
		setEnabled(chat_id, True)
		return
	    if text == '/list':
		reply(u"شما میتونید اسم ایموجی مورد نظرتونو از لیست انخاب کنید و برام بفرستید:\nپوزخند,شادی,شکلک,خندان\nخنده-شیرین,خنده,چشمک,لپ-گلی\nخوشمزه,پکر,چشم-عاشق,پول\nلبخند-مغرورانه,بی-توجه,افسرده,سردرگم\nبوس-فرستادن,فریاد-ترس,متعجب,سرخ\nماسکی,کسل,گربه-عاشق,دعا,گربه-ترسان\nموشک,قطار,اتوبوس,کشتی,زمین\nماه,ستاره,حلزون,مار,اسب,میمون,هشت-پا\nناامید,عرق-سرد,عصبانی,گریه,رضایت,واقع-بین\nمشت,دیس-لایک,لایک,دست-زدن,روح\nقلب-تیرخورده,ادم-فضایی,قلب,حاله\nخنده-شیطانی\nبمب,عینک-افتابی,خنثی,گیج\nزبان-درازی,قهقه,تفنگ\nبعضی ایموجی ها هم ترکیبی هستن:\nخودکشی,قدم-زدن")
		return
	    if text == '/about':
		reply('من ایموجی بات هستم و شما میتونید اسم ایموجی مورد نظرتون رو از لیست انتخاب کنید :) برای ارتباط با سازندم هم میتونید به @farbodgame پیام بدید :) سورس من هم روی گیتهاب منتشر شده و میتونید ازش استفاده کنید و لذت ببرید :) https://github.com/farbodgame/emoji-bot/')
		return
	    if text == '/help':
		reply('شما میتونید برای به دست آوردن لیست نام ایموجی ها دستور /list رو برام بفرستید.شما میتونید کلمه جک رو برام بفرستید تا براتون جک تعریف کنم.من به استیکر هایی که شما برام میفرستید حساسم و واکنش نشون میدم.امیدوارم لذت ببرید :)')
		return
	
        # CUSTOMIZE FROM HERE
	jokes = [u'مرده میخوره به نرده برمیگرده', u'به مگسه میگن سلام میگه سلام',u"انقدر هوا گرمه\nدیدم یه مگس با یه پرچم سفید چسبیده به پنجره\nروش نوشته\nدرو باز کن بی انصاف\nناموسن اذیتت نمیکنم\nفقط میخوام خنک شم :))", u"خدایا جوانانی را که\nبا پدر و مادرشون قهر می کنن\nبه راهی جز خوانندگی هدایت بفرم :))", u"تو مغازه رفته بودم چیزی بخرم\nیهو دختره اومد گفت ببخشید اقا سلام خدافظ دارین؟0_0\nهمه این شکلی شدن 0_o\nیهو دختره گفت ای بابا چرا هیشکی نمیفهمه من چی میگم ؟\nهای بای منظورمه دیگه …\nمیگن افق شلوغه\nمن برم شفق محو شم !", u"محصول جدید صحت\nشامپو سیب زمینی\nمخصوص موهای بی تفاوت :))", u"پیرمرده دم‌ عابر کارتشو‌ داده به من\nمیگه موجودی بگیر برام\nبراش گرفتم ، میگم ۵ هزار تومنه پدر جان\nگفت خاک بر اون سرت کنن با این موجودی گرفتنت و رفت :/", u"هیچ وقت کار امروز رو به فردا ننداز…\nفردا یه عالمه کار داری،\nقشنگ بندازش واسه دو سه هفته دیگه\nکه خیالــــــــــــــتم راحت باشه :))", u"به مامانم میگم چرا تو خونه همش دمپایی پات میکنی ؟\nمیگه: یه کابوی هیچوقت از اسلحه اش دور نمیمونه…\nمنم قانع شدم ، چون مسلح بود!!!", u"سلامتى همه سیکس پکاى اینستا\nکه هیچکدومشون سر ندارن! :))", u"تو خارج فقط اسکلا میزن مدرسه\n.\nواسه همین به مدرسه میگن school :))", u"الان یه پشه رو دیوار خوابیده\nمیخوام برم تو گوشش ویزز ویز کنم\nمن رفتم :))", u"بدترین شکستمو وقتی خوردم که…\nبا عشق و امید گره هندزفریمو باز کردم ولی…\nدیدم گوشیم شارژ نداره…\nهنوز کمر راست نکردم!!! ", u"بهترین و امیدوار کننده ترین\nچراغای زندگیم\nچراغای مودممه\nنباشن دق میکنم :))", u"دقت کردین به بعضیا که دست میدی انگار داری ماهی مرده رو تکون میدی ؟\nخو نمیخوای دست نده :/", u"یارو به جای عکس پروفایلش نوشته\ncoming soon ...\nاحتمالا تو این مدت میخواد فتوشاپ یاد بگیره", u"تو دانشگاه ما هر موقع چمنارو میزدن فرداش قرمه سبزی داشتیم!!!\nعایا این دوتا به هم ربط دارن؟؟؟", u"دختـر باس وختـى آقاش میگه لباسامـو اتـو کـن ؛ بگه :\nشلـوار لـى که اتـو نمیخـواد |:\nپاییـن پیرهنتـم که میره تو شلـوار |:\nآستینتـو هـم که میـدى بالا |:\nجلوشـم که صافـه |:\nیقتـ هـم که بازه |:\nپشتشـم که الان میرى تو ماشیـن لـم میدى به صندلـى صافـ میشه |:\nبقیشـو بده اتـو کنـم سایـه ســر !", u"دختر همسایمون اسمش طلاست\nتو نقره فروشی کار می کنه\nتازگیام رفته برنزه کرده…!!!\nفک کنم آخرش با مسی ازدواج کنه\nبچشم شکل استیلی بشه :))", u"دلیل اینکه من دکتر نشدم\n\nاینه که من از سبزی پلو خوشم نمیاد\nمیدونم ربطی نداره، ولی دلیل من اینه . . .\nبا منم بحث نکنید !!", u"میگن سود آورترین شغل در آمریکا دندون پزشکی هست\nاز بس ما مشت محکم بر دهان آمریکا میزنیم\nبیچاره ها دندون سالم ندارن خب", u"ﺍﻻﻥ ﺍﺧﺒﺎﺭ ﺍﻋﻼﻡ ﮐﺮﺩ ﺳﺎﻻﻧﻪ 800 ﻧﻔﺮ ﺩﺭ ﮐﺸﻮﺭﻣﺎﻥ\nﺩﺭ ﺍﺛﺮ ﮔﺎﺯ ﮔﺮﻓﺘﮕﯽ ﻣﯿﻤﯿﺮﻥ\nﺧﻮﺍﻫﺸﺎ ﮔﺎﺯ ﻧﮕﯿﺮﯾﻦ\nﺑﻮﺱ ﮐﻨﯿﺪ\nﻣﮕﻪ ﻫﺎﺭﯾﻦ", u"” خـــــــر نشو الاغ ”\nاوج نصحیت پسرا", u"پسرخالم رفته دستشویی ، آواز میخونه :\nحالا یارم بیاااا\nادرارم بیاااااا\nینی با این حرکتش موسیقی رو برد زیر سوال", u"اگه مامانم نصف راهکارهایی که موقع دیدن سریال\nبه هنرپیشه اول سریال نشون میده ، به من گفته بود\nالان کل مشکلات زندگیم حل شده بود !\nبه جون خودم . . .", u"هرکس به طریقی دل ما میشکند…\nخداروشکر تنوع بالاست\nحوصلمون سرنمیره", u"یه مرحله ای بالاتر از روشنفکری هست!…\n اونم اینه که کتاب نخری تا درخت های کمتری قطع بشن!", u"تو آفریقا یه قبیله اى هست نمیدونن طلاق چیه !!!\n\n\nاصن به این قرتى بازیا اعتقاد ندارن ...\nزن که پررو میشه میخورنش !!!", u"عرق نعنا\nاز خانواده همون عرق هاست..!!!\nولی اونا رفتن پی رفیق بازی\nاین نشست پای درس و مشقش\nمتخصص معده شده :))", u"ﺑﺰﺭﮔﺘﺮﯾﻦ ﺑُﺮﺩﯼ ﮐﻪ ﺗﻮ ﺯﻧﺪﮔﯽ ﮐﺮﺩﻡ ﺍﯾﻦ ﺑﻮﺩ ﮐﻪ ﺍﺯ ﺑﻘﺎﻟﯽ ﯾﻪ ﺩﻭﻧﻪ\nﻟﻮﺍﺷﮏ ﺧﺮﯾﺪﻡ\nﺭﻓﺘﻢ ﺧﻮﻧﻪ ﺩﯾﺪﻡ ﺩﻭﺗﺎﺳﺖ ﭼﺴﺒﯿﺪﻥ ﺑﻬﻢ :))", u"تو ژاپن از هرچیزی برق تولید میکنن…\n\n\nتو ایران سوسیس کالباس", u"باکتری چیست؟\n\nموجودی که با قوری نبوده است!!!", u"این روزا با این قیمت میوه ها\nتنها ویتامینی که می تونیم بگیریم\nویتامین دیه", u"همسایمون نذری آورده بود\nاومدم تشکر کنم قاطی کردم گفتم خداروشکر!!\n بیچاره فکر کرد\nما داشتیم از گشنگی میمردیم :|\nدوتا بهم داد !", u"بچه که بودم دلم میخواست زنگ بزنم به آدم خوبای فیلما\nبهشون از نقشه های آدم بدا بگم\nتا این حد مغزم کار میکرد :))", u"کتلت چیست؟\nنوعی کباب کوبیدست فقط خستس…خسته!!\nمیفهمییی؟؟؟؟داغوونه…", u"آقا ما ی پسر همسایه داریم موهاش بوره! خیییلیا!!!\nچند وقته ریش گذاشته!!!\nلامصب تا نگاش میکنم یاد پشمک زعفرونی میوفتم"]
	if text == '/joke':
		reply(random.choice(jokes))
		return
	if text == 'جک'.strip():
		reply(random.choice(jokes))
		return
	if text == 'دوست دارم'.strip():
		reply('منم دوست دارم عزیزم :)')
		return
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
	if text == 'پول'.strip():
		reply(u'\U0001f4b5')
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
