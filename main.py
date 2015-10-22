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


# start connecting to telegram bot api

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


def edit_distance(str1, str2):
    if len(str1) == 0:
        return len(str2)
    elif len(str2) == 0:
        return len(str1)
    m = len(str1) + 1
    n = len(str2) + 1
    d = []
    for i in range(m):
        d += [n*[0]]
    for i in range(0, m):
        d[i][0] = i
    for j in range(0, n):
        d[0][j] = j
    for i in range(1, m):
        for j in range(1, n):
            d[i][j] = min(
                1+d[i-1][j],
                1+d[i][j-1],
                d[i-1][j-1] + (1 if str1[i-1] != str2[j-1] else 0)
            )
    return d[m-1][n-1]


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
            self.response.write(
                json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


def reply(chat_id, message_id, msg=None, img=None):
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
        ], [('photo', 'image.jpg', img)])
    else:
        logging.error('no msg or img specified')
        resp = None

    logging.info('send response:')
    logging.info(resp)


class WebhookHandler(webapp2.RequestHandler):
    def __init__(self):
        self.actions = {
            '/start': self.action_start,
            '/list': self.action_list,
            '/about': self.action_about,
            '/help': self.action_help,
            '/joke': self.action_joke,
        }
        self.jokes = [u'مرده میخوره به نرده برمیگرده', u'به مگسه میگن سلام میگه سلام',
                      u"انقدر هوا گرمه\nدیدم یه مگس با یه پرچم سفید چسبیده به پنجره\nروش نوشته\nدرو باز کن بی انصاف\nناموسن اذیتت نمیکنم\nفقط میخوام خنک شم :))",
                      u"خدایا جوانانی را که\nبا پدر و مادرشون قهر می کنن\nبه راهی جز خوانندگی هدایت بفرم :))",
                      u"تو مغازه رفته بودم چیزی بخرم\nیهو دختره اومد گفت ببخشید اقا سلام خدافظ دارین؟0_0\nهمه این شکلی شدن 0_o\nیهو دختره گفت ای بابا چرا هیشکی نمیفهمه من چی میگم ؟\nهای بای منظورمه دیگه …\nمیگن افق شلوغه\nمن برم شفق محو شم !",
                      u"محصول جدید صحت\nشامپو سیب زمینی\nمخصوص موهای بی تفاوت :))",
                      u"پیرمرده دم‌ عابر کارتشو‌ داده به من\nمیگه موجودی بگیر برام\nبراش گرفتم ، میگم ۵ هزار تومنه پدر جان\nگفت خاک بر اون سرت کنن با این موجودی گرفتنت و رفت :/",
                      u"هیچ وقت کار امروز رو به فردا ننداز…\nفردا یه عالمه کار داری،\nقشنگ بندازش واسه دو سه هفته دیگه\nکه خیالــــــــــــــتم راحت باشه :))",
                      u"به مامانم میگم چرا تو خونه همش دمپایی پات میکنی ؟\nمیگه: یه کابوی هیچوقت از اسلحه اش دور نمیمونه…\nمنم قانع شدم ، چون مسلح بود!!!",
                      u"سلامتى همه سیکس پکاى اینستا\nکه هیچکدومشون سر ندارن! :))",
                      u"تو خارج فقط اسکلا میزن مدرسه\n.\nواسه همین به مدرسه میگن school :))",
                      u"الان یه پشه رو دیوار خوابیده\nمیخوام برم تو گوشش ویزز ویز کنم\nمن رفتم :))",
                      u"بدترین شکستمو وقتی خوردم که…\nبا عشق و امید گره هندزفریمو باز کردم ولی…\nدیدم گوشیم شارژ نداره…\nهنوز کمر راست نکردم!!! ",
                      u"بهترین و امیدوار کننده ترین\nچراغای زندگیم\nچراغای مودممه\nنباشن دق میکنم :))",
                      u"دقت کردین به بعضیا که دست میدی انگار داری ماهی مرده رو تکون میدی ؟\nخو نمیخوای دست نده :/",
                      u"یارو به جای عکس پروفایلش نوشته\ncoming soon ...\nاحتمالا تو این مدت میخواد فتوشاپ یاد بگیره",
                      u"تو دانشگاه ما هر موقع چمنارو میزدن فرداش قرمه سبزی داشتیم!!!\nعایا این دوتا به هم ربط دارن؟؟؟",
                      u"دختـر باس وختـى آقاش میگه لباسامـو اتـو کـن ؛ بگه :\nشلـوار لـى که اتـو نمیخـواد |:\nپاییـن پیرهنتـم که میره تو شلـوار |:\nآستینتـو هـم که میـدى بالا |:\nجلوشـم که صافـه |:\nیقتـ هـم که بازه |:\nپشتشـم که الان میرى تو ماشیـن لـم میدى به صندلـى صافـ میشه |:\nبقیشـو بده اتـو کنـم سایـه ســر !",
                      u"دختر همسایمون اسمش طلاست\nتو نقره فروشی کار می کنه\nتازگیام رفته برنزه کرده…!!!\nفک کنم آخرش با مسی ازدواج کنه\nبچشم شکل استیلی بشه :))",
                      u"دلیل اینکه من دکتر نشدم\n\nاینه که من از سبزی پلو خوشم نمیاد\nمیدونم ربطی نداره، ولی دلیل من اینه . . .\nبا منم بحث نکنید !!",
                      u"میگن سود آورترین شغل در آمریکا دندون پزشکی هست\nاز بس ما مشت محکم بر دهان آمریکا میزنیم\nبیچاره ها دندون سالم ندارن خب",
                      u"ﺍﻻﻥ ﺍﺧﺒﺎﺭ ﺍﻋﻼﻡ ﮐﺮﺩ ﺳﺎﻻﻧﻪ 800 ﻧﻔﺮ ﺩﺭ ﮐﺸﻮﺭﻣﺎﻥ\nﺩﺭ ﺍﺛﺮ ﮔﺎﺯ ﮔﺮﻓﺘﮕﯽ ﻣﯿﻤﯿﺮﻥ\nﺧﻮﺍﻫﺸﺎ ﮔﺎﺯ ﻧﮕﯿﺮﯾﻦ\nﺑﻮﺱ ﮐﻨﯿﺪ\nﻣﮕﻪ ﻫﺎﺭﯾﻦ",
                      u"” خـــــــر نشو الاغ ”\nاوج نصحیت پسرا",
                      u"پسرخالم رفته دستشویی ، آواز میخونه :\nحالا یارم بیاااا\nادرارم بیاااااا\nینی با این حرکتش موسیقی رو برد زیر سوال",
                      u"اگه مامانم نصف راهکارهایی که موقع دیدن سریال\nبه هنرپیشه اول سریال نشون میده ، به من گفته بود\nالان کل مشکلات زندگیم حل شده بود !\nبه جون خودم . . .",
                      u"هرکس به طریقی دل ما میشکند…\nخداروشکر تنوع بالاست\nحوصلمون سرنمیره",
                      u"یه مرحله ای بالاتر از روشنفکری هست!…\n اونم اینه که کتاب نخری تا درخت های کمتری قطع بشن!",
                      u"تو آفریقا یه قبیله اى هست نمیدونن طلاق چیه !!!\n\n\nاصن به این قرتى بازیا اعتقاد ندارن ...\nزن که پررو میشه میخورنش !!!",
                      u"عرق نعنا\nاز خانواده همون عرق هاست..!!!\nولی اونا رفتن پی رفیق بازی\nاین نشست پای درس و مشقش\nمتخصص معده شده :))",
                      u"ﺑﺰﺭﮔﺘﺮﯾﻦ ﺑُﺮﺩﯼ ﮐﻪ ﺗﻮ ﺯﻧﺪﮔﯽ ﮐﺮﺩﻡ ﺍﯾﻦ ﺑﻮﺩ ﮐﻪ ﺍﺯ ﺑﻘﺎﻟﯽ ﯾﻪ ﺩﻭﻧﻪ\nﻟﻮﺍﺷﮏ ﺧﺮﯾﺪﻡ\nﺭﻓﺘﻢ ﺧﻮﻧﻪ ﺩﯾﺪﻡ ﺩﻭﺗﺎﺳﺖ ﭼﺴﺒﯿﺪﻥ ﺑﻬﻢ :))",
                      u"تو ژاپن از هرچیزی برق تولید میکنن…\n\n\nتو ایران سوسیس کالباس",
                      u"باکتری چیست؟\n\nموجودی که با قوری نبوده است!!!",
                      u"این روزا با این قیمت میوه ها\nتنها ویتامینی که می تونیم بگیریم\nویتامین دیه",
                      u"همسایمون نذری آورده بود\nاومدم تشکر کنم قاطی کردم گفتم خداروشکر!!\n بیچاره فکر کرد\nما داشتیم از گشنگی میمردیم :|\nدوتا بهم داد !",
                      u"بچه که بودم دلم میخواست زنگ بزنم به آدم خوبای فیلما\nبهشون از نقشه های آدم بدا بگم\nتا این حد مغزم کار میکرد :))",
                      u"کتلت چیست؟\nنوعی کباب کوبیدست فقط خستس…خسته!!\nمیفهمییی؟؟؟؟داغوونه…",
                      u"آقا ما ی پسر همسایه داریم موهاش بوره! خیییلیا!!!\nچند وقته ریش گذاشته!!!\nلامصب تا نگاش میکنم یاد پشمک زعفرونی میوفتم"]
        self.emojis = {
            'دوست دارم'.strip(): 'منم دوست دارم عزیزم :)',
            'سلام'.strip(): 'سلام :)',
            'خداحافظ'.strip(): 'خداحافظ',
            'پوزخند'.strip(): u'\U0001f601',
            'شادی'.strip(): u'\U0001f602',
            'شکلک'.strip(): u'\U0001f603',
            'خندان'.strip(): u'\U0001f604',
            'خنده-شیرین'.strip(): u'\U0001f605',
            'خنده'.strip(): u'\U0001f606',
            'چشمک'.strip(): u'\U0001f609',
            'لپ-گلی'.strip(): u'\U0001f60A',
            'خوشمزه'.strip(): u'\U0001f60B',
            'پکر'.strip(): u'\U0001f60C',
            'چشم-عاشق'.strip(): u'\U0001f60D',
            'لبخند-مغرورانه'.strip(): u'\U0001f60F',
            'افسرده'.strip(): u'\U0001f614',
            'بی-توجه'.strip(): u'\U0001f612',
            'سردرگم'.strip(): u'\U0001f616',
            'بوس-فرستادن'.strip(): u'\U0001f618',
            'سرخ'.strip(): u'\U0001f633',
            'فریاد-ترس'.strip(): u'\U0001f631',
            'متعجب'.strip(): u'\U0001f632',
            'ماسک'.strip(): u'\U0001f637',
            'کسل'.strip(): u'\U0001f629',
            'گربه-عاشق'.strip(): u'\U0001f63B',
            'دعا'.strip(): u'\U0001f64F',
            'گربه-ترسان'.strip(): u'\U0001f640',
            'موشک'.strip(): u'\U0001f680',
            'قطار'.strip(): u'\U0001f684',
            'اتوبوس'.strip(): u'\U0001f68C',
            'کشتی'.strip(): u'\U0001f6A2',
            'پول'.strip(): u'\U0001f4b5',
            'زمین'.strip(): u'\U0001f30f',
            'ماه'.strip(): u'\U0001f319',
            'ستاره'.strip(): u'\U0001f31F',
            'حلزون'.strip(): u'\U0001f40C',
            'مار'.strip(): u'\U0001f40D',
            'اسب'.strip(): u'\U0001f40E',
            'میمون'.strip(): u'\U0001f412',
            'هشت-پا'.strip(): u'\U0001f419',
            'ناامید'.strip(): u'\U0001f61E',
            'عرق-سرد'.strip(): u'\U0001f630',
            'عصبانی'.strip(): u'\U0001f621',
            'گریه'.strip(): u'\U0001f622',
            'رضایت'.strip(): u'\U0001f623',
            'واقع-بین'.strip(): u'\U0001f625',
            'مشت'.strip(): u'\U0001f44A',
            'دیس-لایک'.strip(): u'\U0001f44E',
            'لایک'.strip(): u'\U0001f44D',
            'دست-زدن'.strip(): u'\U0001f44F',
            'روح'.strip(): u'\U0001f47B',
            'قلب-تیرخورده'.strip(): u'\U0001f498',
            'قلب'.strip(): u'\U0001f493',
            'ادم-فضایی'.strip(): u'\U0001f47D',
            'هاله'.strip(): u'\U0001f607',
            'خنده-شیطانی'.strip(): u'\U0001f608',
            'بمب'.strip(): u'\U0001f4A3',
            'عینک-افتابی'.strip(): u'\U0001f60E',
            'ترسان'.strip(): u'\U0001f628',
            'خنثی'.strip(): u'\U0001f610',
            'گیج'.strip(): u'\U0001f615',
            'زبان-درازی'.strip(): u'\U0001f61B',
            'نگران'.strip(): u'\U0001f61F',
            'قهقه'.strip(): u'\U0001f62D',
            'تفنگ'.strip(): u'\U0001f52B',
            'خودکشی'.strip(): u'\U0001f610'u'\U0001f52B',
            'قدم-زدن'.strip(): u'\U0001f60e\u2615\ufe0f\U0001f463',
        }

    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        request_body_raw = self.request.body
        body = json.loads(request_body_raw)
        logging.info('request body: \n' + body)
        self.response.write(request_body_raw)

        message = body['message']
        message_id = message.get('message_id')
        text = message.get('text')
        sticker = message.get('sticker')
        chat_id = message['chat']['id']

        if sticker:
            reply(chat_id, message_id, 'من ایموجی بات هستم :) بنابراین نظری در مورد استیکر شما ندارم :)')
        else:
            text = text.strip()
            logging.info(text.decode('utf-8'))

            if text in self.actions:
                self.actions[text](chat_id=chat_id, message_id=message_id)
            elif text == 'جک'.strip():
                self.action_joke()
            elif text in self.emojis:
                reply(chat_id, message_id, self.emojis[text])
            else:
                min_distance = len(text) + 1
                min_distance_word = ''
                for word in self.emojis:
                    dist = edit_distance(text, word)
                    if dist > max(len(word), len(text)) * 0.75:  # Age kheyli fargh dashte bashan ehtemalan ghalat typi nist
                        del dist
                    else:
                        if min_distance > dist:
                            min_distance = dist
                            min_distance_word = word

                if len(min_distance_word) > 0:
                    reply(chat_id, message_id, 'آیا منظورتان {} بود؟'.format(min_distance_word))
                    reply(chat_id, message_id, self.emojis[min_distance_word])
                else:
                    reply(chat_id, message_id, 'لطفا نام ایموجی بعدی مورد نظر خود را درست وارد کنید.')

    def action_joke(self, **kwargs):
        reply(kwargs['chat_id'], kwargs['message_id'], random.choice(self.jokes))

    def action_start(self, **kwargs):
        reply(kwargs['chat_id'], kwargs['message_id'], 'بات روشن شد.لطفا برای به دست آوردن لیست اسامی ایموجی ها دستور /help رو برام بفرستید :)')
        setEnabled(kwargs['chat_id'], True)

    def action_list(self, **kwargs):
        # reply(kwargs['chat_id'], kwargs['message_id'],
        #     u"شما میتونید اسم ایموجی مورد نظرتونو از لیست انخاب کنید و برام بفرستید:\nپوزخند,شادی,شکلک,خندان\nخنده-شیرین,خنده,چشمک,لپ-گلی\nخوشمزه,پکر,چشم-عاشق,پول\nلبخند-مغرورانه,بی-توجه,افسرده,سردرگم\nبوس-فرستادن,فریاد-ترس,متعجب,سرخ\nماسکی,کسل,گربه-عاشق,دعا,گربه-ترسان\nموشک,قطار,اتوبوس,کشتی,زمین\nماه,ستاره,حلزون,مار,اسب,میمون,هشت-پا\nناامید,عرق-سرد,عصبانی,گریه,رضایت,واقع-بین\nمشت,دیس-لایک,لایک,دست-زدن,روح\nقلب-تیرخورده,ادم-فضایی,قلب,هاله\nخنده-شیطانی\nبمب,عینک-افتابی,خنثی,گیج\nزبان-درازی,قهقه,تفنگ\nبعضی ایموجی ها هم ترکیبی هستن:\nخودکشی,قدم-زدن")
        reply(kwargs['chat_id'], kwargs['message_id'], ', '.join(self.emojis))


    def action_about(self, **kwargs):
        reply(kwargs['chat_id'], kwargs['message_id'],
            'من ایموجی بات هستم و شما میتونید اسم ایموجی مورد نظرتون رو از لیست انتخاب کنید :) برای ارتباط با سازندم هم میتونید به @farbodgame پیام بدید :) سورس من هم روی گیتهاب منتشر شده و میتونید ازش استفاده کنید و لذت ببرید :) https://github.com/farbodgame/emoji-bot/')

    def action_help(self, **kwargs):
        reply(kwargs['chat_id'], kwargs['message_id'],
            'شما میتونید برای به دست آوردن لیست نام ایموجی ها دستور /list رو برام بفرستید.شما میتونید کلمه جک رو برام بفرستید تا براتون جک تعریف کنم.من به استیکر هایی که شما برام میفرستید حساسم و واکنش نشون میدم.امیدوارم لذت ببرید :)')


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
