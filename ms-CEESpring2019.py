#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Call:
	python pwb.py masti/ms-CEESpring2019.py -page:"Szablon:CEE Spring 2019" -outpage:"meta:Wikimedia CEE Spring 2019/Statistics" -summary:"Bot updates statistics"
        python pwb.py masti/ms-CEESpring2019.py -page:"Szablon:CEE Spring 2019" -outpage:"Wikipedysta:Masti/CEE Spring 2019" -summary:"Bot updates statistics"


Use global -simulate option for test purposes. No changes to live wiki
will be done.

The following parameters are supported:

&params;

-always           If used, the bot won't ask if it should file the message
                  onto user talk page.   

-outpage          Results page; otherwise "Wikipedysta:mastiBot/test" is used

-maxlines         Max number of entries before new subpage is created; default 1000

-text:            Use this text to be added; otherwise 'Test' is used

-replace:         Dont add text but replace it

-top              Place additional text on top of the page

-summary:         Set the action summary message for the edit.

-negative:        mark if text not in page

-v:               make verbose output
-vv:              make even more verbose output

"""
#
# (C) Pywikibot team, 2006-2016
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, unicode_literals

__version__ = '$Id: c1795dd2fb2de670c0b4bddb289ea9d13b1e9b3f $'
#

import pywikibot
from pywikibot import pagegenerators
import re
from pywikibot import textlib
from datetime import datetime
import pickle
from pywikibot import (
    config, config2,
)

from pywikibot.bot import (
    MultipleSitesBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)
    #SingleSiteBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)
from pywikibot.tools import issue_deprecation_warning

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}
CEEtemplates = {'pl' : 'Szablon:CEE Spring 2019', 'az' : 'Şablon:Vikibahar 2019', 'ba' : 'Ҡалып:Вики-яҙ 2019', 'be' : 'Шаблон:CEE Spring 2019', 'be-tarask' : 'Шаблён:Артыкул ВікіВясны-2019', 'bg' : 'Шаблон:CEE Spring 2019', 'de' : 'Vorlage:CEE Spring 2019', 'el' : 'Πρότυπο:CEE Spring 2019', 'et' : 'Mall:CEE Spring 2019', 'hr' : 'Predložak:CEE proljeće 2019.', 'hy' : 'Կաղապար:CEE Spring 2019', 'ka' : 'თარგი:ვიკიგაზაფხული 2019', 'lv' : 'Veidne:CEE Spring 2019', 'lt' : 'Šablonas:VRE 2019', 'mk' : 'Шаблон:СИЕ Пролет 2019', 'ro' : 'Format:Wikimedia CEE Spring 2019', 'ru' : 'Шаблон:Вики-весна 2019', 'sr' : 'Шаблон:ЦЕЕ пролеће 2019', 'tr' : 'Şablon:Vikibahar 2019', 'uk' : 'Шаблон:CEE Spring 2019' }
countryList =[ u'Albania', u'Armenia', u'Austria', u'Azerbaijan', u'Bashkortostan', u'Belarus', u'Bosnia and Herzegovina', u'Bulgaria', u'Crimean Tatars', u'Croatia', u'Czechia', u'Erzia', u'Esperanto', u'Estonia', u'Georgia', u'Greece', u'Hungary', u'Kazakhstan', u'Kosovo', u'Latvia', u'Lithuania', u'Macedonia', u'Moldova', u'Poland', u'Romania', u'Republic of Srpska', u'Russia', u'Serbia', u'Slovakia', u'Tatarstan', u'Turkey', u'Ukraine', u'Other', u'Empty' ]
countryNames = {
'pl':{ 'Albania':'Albania', 'Austria':'Austria', 'Azerbejdżan':'Azerbaijan', 'Baszkortostan':'Bashkortostan', 'Białoruś':'Belarus', 'Bułgaria':'Bulgaria', 'Armenia':'Armenia', 'Bośnia i Hercegowina':'Bosnia and Herzegovina', 'Erzja':'Erzia', 'Esperanto':'Esperanto', 'Estonia':'Estonia', 'Gruzja':'Georgia', 'Czechy':'Czechia', 'Chorwacja':'Croatia', 'Kosowo':'Kosovo', 'Tatarzy krymscy':'Crimean Tatars', 'Litwa':'Lithuania', 'Łotwa':'Latvia', 'Węgry':'Hungary', 'Macedonia':'Macedonia', 'Mołdawia':'Moldova', 'Polska':'Poland', 'Rosja':'Russia', 'Rumunia':'Romania', 'Republika Serbska':'Republic of Srpska', 'Serbia':'Serbia', 'Słowacja':'Slovakia', 'Turcja':'Turkey', 'Ukraina':'Ukraine', 'Grecja':'Greece', 'Kazachstan':'Kazakhstan', 'Tatarstan':'Tatarstan'},
'az':{ 'Albaniya':'Albania', 'Avstriya':'Austria', 'Azərbaycan':'Azerbaijan', 'Başqırdıstan':'Bashkortostan', 'Belarus':'Belarus', 'Bolqarıstan':'Bulgaria', 'Ermənistan':'Armenia', 'Bosniya və Herseqovina':'Bosnia and Herzegovina', 'Erzya':'Erzia', 'Esperantida':'Esperanto', 'Estoniya':'Estonia', 'Gürcüstan':'Georgia', 'Çexiya':'Czechia', 'Xorvatiya':'Croatia', 'Kosovo':'Kosovo', 'Krımtatar':'Crimean Tatars', 'Krım tatarları':'Crimean Tatars', 'Krım-Tatar':'Crimean Tatars', 'Litva':'Lithuania', 'Latviya':'Latvia', 'Macarıstan':'Hungary', 'Makedoniya':'Macedonia', 'Moldova':'Moldova', 'Polşa':'Poland', 'Rusiya':'Russia', 'Rumıniya':'Romania', 'Serb Respublikası':'Republic of Srpska', 'Serbiya':'Serbia', 'Slovakiya':'Slovakia', 'Türkiyə':'Turkey', 'Ukrayna':'Ukraine', 'Yunanıstan':'Greece', 'Qazaxıstan':'Kazakhstan', },
'ba':{ 'Албания':'Albania', 'Австрия':'Austria', 'Әзербайжан':'Azerbaijan', 'Башҡортостан':'Bashkortostan', 'Белоруссия':'Belarus', 'Беларусь':'Belarus', 'Болгария':'Bulgaria', 'Әрмәнстан':'Armenia', 'Босния һәм Герцеговина':'Bosnia and Herzegovina', 'Эрзя':'Erzia', 'Эсперантида':'Esperanto', 'Эстония':'Estonia', 'Грузия':'Georgia', 'Чехия':'Czechia', 'Хорватия':'Croatia', 'Косово':'Kosovo', 'Ҡырым Республикаһы':'Crimean Tatars', 'Ҡырым татарҙары':'Crimean Tatars', 'Литва':'Lithuania', 'Латвия':'Latvia', 'Венгрия':'Hungary', 'Македония':'Macedonia', 'Молдавия':'Moldova', 'Польша':'Poland', 'Рәсәй':'Russia', 'Румыния':'Romania', 'Серб Республикаһы':'Republic of Srpska', 'Сербия':'Serbia', 'Словакия':'Slovakia', 'Төркиә':'Turkey', 'Украина':'Ukraine', 'Греция':'Greece', 'Ҡаҙағстан':'Kazakhstan', },
'be':{ 'Албанія':'Albania', 'Аўстрыя':'Austria', 'Азербайджан':'Azerbaijan', 'Башкартастан':'Bashkortostan', 'Беларусь':'Belarus', 'Балгарыя':'Bulgaria', 'Арменія':'Armenia', 'Боснія і Герцагавіна':'Bosnia and Herzegovina', 'Эрзя':'Erzia', 'Эсперанта':'Esperanto', 'Эстонія':'Estonia', 'Грузія':'Georgia', 'Чэхія':'Czechia', 'Харватыя':'Croatia', 'Рэспубліка Косава':'Kosovo', 'Крымскія татары':'Crimean Tatars', 'Літва':'Lithuania', 'Латвія':'Latvia', 'Венгрыя':'Hungary', 'Македонія':'Macedonia', 'Малдова':'Moldova', 'Польшча':'Poland', 'Расія':'Russia', 'Румынія':'Romania', 'Рэспубліка Сербская':'Republic of Srpska', 'Сербія':'Serbia', 'Славакія':'Slovakia', 'Турцыя':'Turkey', 'Украіна':'Ukraine', 'Грэцыя':'Greece', 'Казахстан':'Kazakhstan', },
'be-tarask':{ 'Альбанія':'Albania', 'Аўстрыя':'Austria', 'Азэрбайджан':'Azerbaijan', 'Башкартастан':'Bashkortostan', 'Беларусь':'Belarus', 'Баўгарыя':'Bulgaria', 'Армэнія':'Armenia', 'Босьнія і Герцагавіна':'Bosnia and Herzegovina', 'Эрзя':'Erzia', 'Эспэранта':'Esperanto', 'Эстонія':'Estonia', 'Грузія':'Georgia', 'Чэхія':'Czechia', 'Харватыя':'Croatia', 'Косава':'Kosovo', 'крымскія татары':'Crimean Tatars', 'Крымскія татары':'Crimean Tatars', 'Летува':'Lithuania', 'Латвія':'Latvia', 'Вугоршчына':'Hungary', 'Македонія':'Macedonia', 'Северна Македония':'Macedonia', 'Малдова':'Moldova', 'Польшча':'Poland', 'Расея':'Russia', 'Румынія':'Romania', 'Рэспубліка Сэрбская':'Republic of Srpska', 'Сэрбія':'Serbia', 'Славаччына':'Slovakia', 'Турэччына':'Turkey', 'Украіна':'Ukraine', 'Грэцыя':'Greece', 'Казахстан':'Kazakhstan', },
'bg':{ 'Албания':'Albania', 'Австрия':'Austria', 'Азербайджан':'Azerbaijan', 'Башкортостан':'Bashkortostan', 'Беларус':'Belarus', 'България':'Bulgaria', 'Армения':'Armenia', 'Босна и Херцеговина':'Bosnia and Herzegovina', 'кримските татари':'Crimean Tatars', 'Ерзяни':'Erzia','ерзяни':'Erzia','Эрзя':'Erzia', 'Есперанто':'Esperanto', 'Естония':'Estonia', 'Грузия':'Georgia', 'Чехия':'Czechia', 'Хърватия':'Croatia', 'Косово':'Kosovo', 'кримски татари':'Crimean Tatars', 'Кримски татари':'Crimean Tatars', 'Литва':'Lithuania', 'Латвия':'Latvia', 'Унгария':'Hungary', 'Република Македония':'Macedonia', 'Македония':'Macedonia', 'Молдова':'Moldova', 'Полша':'Poland', 'Русия':'Russia', 'Румъния':'Romania', 'Република Сръбска':'Republic of Srpska', 'Сърбия':'Serbia', 'Словакия':'Slovakia', 'Турция':'Turkey', 'Украйна':'Ukraine', 'Гърция':'Greece', 'Казахстан':'Kazakhstan', 'Татарстан':'Tatarstan'},
'de':{ 'Albanien':'Albania', 'Österreich':'Austria', 'Aserbaidschan':'Azerbaijan', 'Baschkortostan':'Bashkortostan', 'Weißrussland':'Belarus', 'Bulgarien':'Bulgaria', 'Armenien':'Armenia', 'Bosnien und Herzegowina':'Bosnia and Herzegovina', 'Ersja':'Erzia', 'Esperanto':'Esperanto', 'Estland':'Estonia', 'Georgien':'Georgia', 'Tschechien':'Czechia', 'Kroatien':'Croatia', 'Kosovo':'Kosovo', 'Krimtataren':'Crimean Tatars', 'Litauen':'Lithuania', 'Lettland':'Latvia', 'Ungarn':'Hungary', 'Mazedonien':'Macedonia', 'Moldau':'Moldova', 'Moldawien':'Moldova', 'Polen':'Poland', 'Russland':'Russia', 'Rumänien':'Romania', 'Republika Srpska':'Republic of Srpska', 'Serbien':'Serbia', 'Slowakei':'Slovakia', 'Türkei':'Turkey', 'Ukraine':'Ukraine', 'Griechenland':'Greece', 'Kasachstan':'Kazakhstan', },
'crh':{ 'Arnavutlıq':'Albania', 'Avstriya':'Austria', 'Azerbaycan':'Azerbaijan', 'Başqırtistan':'Bashkortostan', 'Belarus':'Belarus', 'Bulğaristan':'Bulgaria', 'Ermenistan':'Armenia', 'Bosna ve Hersek':'Bosnia and Herzegovina', 'Esperanto':'Esperanto', 'Estoniya':'Estonia', 'Gürcistan':'Georgia', 'Çehiya':'Czechia', 'Hırvatistan':'Croatia', 'Kosovo':'Kosovo', 'Qırımtatarlar':'Crimean Tatars', 'Litvaniya':'Lithuania', 'Latviya':'Latvia', 'Macaristan':'Hungary', 'Makedoniya':'Macedonia', 'Moldova':'Moldova', 'Lehistan':'Poland', 'Rusiye':'Russia', 'Romaniya':'Romania', 'Sırb Cumhuriyeti':'Republic of Srpska', 'Sırbistan':'Serbia', 'Slovakiya':'Slovakia', 'Türkiye':'Turkey', 'Ukraina':'Ukraine', 'Yunanistan':'Greece', 'Qazahistan':'Kazakhstan', },
'el':{ 'Αλβανία':'Albania', 'Αυστρία':'Austria', 'Αζερμπαϊτζάν':'Azerbaijan', 'Μπασκορτοστάν':'Bashkortostan', 'Λευκορωσία':'Belarus', 'Βουλγαρία':'Bulgaria', 'Αρμενία':'Armenia', 'Βοσνία και Ερζεγοβίνη':'Bosnia and Herzegovina', 'Έρζυα':'Erzia', 'Εσπεράντο':'Esperanto', 'Εσθονία':'Estonia', 'Γεωργία':'Georgia', 'Τσεχία':'Czechia', 'Κροατία':'Croatia', 'Κόσοβο':'Kosovo', 'Τατάροι Κριμαίας':'Crimean Tatars', 'Λιθουανία':'Lithuania', 'Λετονία':'Latvia', 'Ουγγαρία':'Hungary', 'πΓΔΜ':'Macedonia', 'Βόρεια Μακεδονία':'Macedonia', 'Μολδαβία':'Moldova', 'Πολωνία':'Poland', 'Ρωσική Ομοσπονδία':'Russia', 'Ρωσία':'Russia', 'Ρουμανία':'Romania', 'Δημοκρατία της Σερβίας':'Republic of Srpska', 'Σερβική Δημοκρατία':'Republic of Srpska', 'Σερβία':'Serbia', 'Σλοβακία':'Slovakia', 'Τουρκία':'Turkey', 'Ουκρανία':'Ukraine', 'Ελλάδα':'Greece', 'Καζακστάν':'Kazakhstan', },
'myv':{ 'Албания':'Albania', 'Австрия':'Austria', 'Азербайджан':'Azerbaijan', 'Башкирия':'Bashkortostan', 'Белорузия':'Belarus', 'Болгария':'Bulgaria', 'Армения':'Armenia', 'Босния ды Герцеговина':'Bosnia and Herzegovina', 'Эрзя':'Erzia', 'Эсперанто':'Esperanto', 'Эстэнь':'Estonia', 'Грузия':'Georgia', 'Чехия':'Czechia', 'Хорватия':'Croatia', 'Литва':'Lithuania', 'Латвия':'Latvia', 'Мадьяронь':'Hungary', 'Македония':'Macedonia', 'Молдавия':'Moldova', 'Польша':'Poland', 'Россия':'Russia', 'Румыния':'Romania', 'Сербань Республикась':'Republic of Srpska', 'Сербия':'Serbia', 'Словакия':'Slovakia', 'Турция':'Turkey', 'Украина':'Ukraine', 'Греция':'Greece', 'Казахстан':'Kazakhstan', },
'eo':{ 'Albanio':'Albania', 'Aŭstrio':'Austria', 'Azerbajĝano':'Azerbaijan', 'Baŝkirio':'Bashkortostan', 'Belorusio':'Belarus', 'Bulgario':'Bulgaria', 'Armenio':'Armenia', 'Bosnio kaj Hercegovino':'Bosnia and Herzegovina', 'Erzja':'Erzia', 'Esperantujo':'Esperanto', 'Esperanto':'Esperanto', 'Estonio':'Estonia', 'Kartvelio':'Georgia', 'Ĉeĥio':'Czechia', 'Kroatio':'Croatia', 'Kosovo':'Kosovo', 'Krimeo':'Crimean Tatars', 'Krime-tataroj':'Crimean Tatars', 'Litovio':'Lithuania', 'Latvio':'Latvia', 'Hungario':'Hungary', 'Makedonio':'Macedonia', 'Moldava':'Moldova', 'Pollando':'Poland', 'Rusio':'Russia', 'Rumanio':'Romania', 'Serba Respubliko':'Republic of Srpska', 'Serbio':'Serbia', 'Slovakio':'Slovakia', 'Turkio':'Turkey', 'Ukrainio':'Ukraine', 'Grekio':'Greece', 'Kazaĥio':'Kazakhstan', },
'hy':{ 'Ալբանիա':'Albania', 'Ավստրիա':'Austria', 'Ադրբեջան':'Azerbaijan', 'Ադրբեջանական Հանրապետություն':'Azerbaijan', 'Բաշկորտոստան':'Bashkortostan', 'Բելառուս':'Belarus', 'Բուլղարիա':'Bulgaria', 'Հայաստան':'Armenia', 'Բոսնիա և Հերցեգովինա':'Bosnia and Herzegovina', 'Էսպերանտո':'Esperanto', 'Էստոնիա':'Estonia', 'Էրզիա':'Erzia', 'Վրաստան':'Georgia', 'Չեխիա':'Czechia', 'Խորվաթիա':'Croatia', 'Կոսովո':'Kosovo', 'Ղրիմի թաթարներ':'Crimean Tatars', 'Լիտվա':'Lithuania', 'Լատվիա':'Latvia', 'Հունգարիա':'Hungary', 'Մակեդոնիա':'Macedonia', 'Մակեդոնիայի Հանրապետություն':'Macedonia', 'Մոլդովա':'Moldova', 'Լեհաստան':'Poland', 'Ռուսաստան':'Russia', 'Ռումինիա':'Romania', 'Սերբիայի Հանրապետություն':'Serbia', 'Սերբիա':'Serbia', 'Սլովակիա':'Slovakia', 'Թուրքիա':'Turkey', 'Ուկրաինա':'Ukraine', 'Հունաստան':'Greece', 'Ղազախստան':'Kazakhstan', },
'ka':{ 'ალბანეთი':'Albania', 'ავსტრია':'Austria', 'აზერბაიჯანი':'Azerbaijan', 'ბაშკირეთი':'Bashkortostan', 'ბელარუსი':'Belarus', 'ბულგარეთი':'Bulgaria', 'სომხეთი':'Armenia', 'ბოსნია და ჰერცეგოვინა':'Bosnia and Herzegovina', 'ესპერანტო':'Esperanto', 'ესტონეთი':'Estonia', 'საქართველო':'Georgia', 'ჩეხეთი':'Czechia', 'ხორვატია':'Croatia', 'კოსოვო':'Kosovo', 'ყირიმელი თათრები':'Crimean Tatars', 'ლიტვა':'Lithuania', 'ლატვია':'Latvia', 'უნგრეთი':'Hungary', 'მაკედონია':'Macedonia', 'მოლდოვა':'Moldova', 'პოლონეთი':'Poland', 'რუსეთი':'Russia', 'რუმინეთი':'Romania', 'სერბთა რესპუბლიკა':'Republic of Srpska', 'სერბეთი':'Serbia', 'სლოვაკეთი':'Slovakia', 'თურქეთი':'Turkey', 'უკრაინა':'Ukraine', 'საბერძნეთი':'Greece', 'ყაზახეთი':'Kazakhstan', },
'lv':{ 'Albānija':'Albania', 'Austrija':'Austria', 'Azerbaidžāna':'Azerbaijan', 'Baškortostāna':'Bashkortostan', 'Baltkrievija':'Belarus', 'Bulgārija':'Bulgaria', 'Armēnija':'Armenia', 'Bosnija un Hercegovina':'Bosnia and Herzegovina', 'erzji':'Erzia', 'Erzju':'Erzia', 'Esperanto':'Esperanto', 'Igaunija':'Estonia', 'Gruzija':'Georgia', 'Čehija':'Czechia', 'Horvātija':'Croatia', 'Kosova':'Kosovo', 'Krimas tatāri':'Crimean Tatars', 'Lietuva':'Lithuania', 'Latvija':'Latvia', 'Ungārija':'Hungary', 'Maķedonija':'Macedonia', 'Moldova':'Moldova', 'Polija':'Poland', 'Krievija':'Russia', 'Rumānija':'Romania', 'Serbu Republika':'Republic of Srpska', 'Serbija':'Serbia', 'Slovākija':'Slovakia', 'Turcija':'Turkey', 'Ukraina':'Ukraine', 'Grieķija':'Greece', 'Kazahstāna':'Kazakhstan', },
'lt':{ 'Albanija':'Albania', 'Austrija':'Austria', 'Azerbaidžanas':'Azerbaijan', 'Baškirija':'Bashkortostan', 'Baltarusija':'Belarus', 'Bulgarija':'Bulgaria', 'Armėnija':'Armenia', 'Bosnija ir Hercegovina':'Bosnia and Herzegovina', 'Erzių':'Erzia', 'Esperanto':'Esperanto', 'Estija':'Estonia', 'Gruzija':'Georgia', 'Čekija':'Czechia', 'Kroatija':'Croatia', 'Kosovas':'Kosovo', 'Krymas':'Crimean Tatars', 'Krymo totoriai':'Crimean Tatars', 'Lietuva':'Lithuania', 'Latvija':'Latvia', 'Vengrija':'Hungary', 'Makedonija':'Macedonia', 'Moldavija':'Moldova', 'Lenkija':'Poland', 'Rusija':'Russia', 'Rumunija':'Romania', 'Serbų Respublika':'Republic of Srpska', 'Serbų respublika':'Republic of Srpska', 'Serbija':'Serbia', 'Serbijos respublika':'Serbia', 'Slovakija':'Slovakia', 'Turkija':'Turkey', 'Ukraina':'Ukraine', 'Graikija':'Greece', 'Kazachstanas':'Kazakhstan', 'Tatarstanas':'Tatarstan' },
'mk':{ 'Албанија':'Albania', 'Австрија':'Austria', 'Азербејџан':'Azerbaijan', 'Башкортостан':'Bashkortostan', 'Bashkortostani':'Bashkortostan', 'Белорусија':'Belarus', 'Бугарија':'Bulgaria', 'Ерменија':'Armenia', 'Босна и Херцеговина':'Bosnia and Herzegovina', 'Ерзја':'Erzia', 'Есперанто':'Esperanto', 'Естонија':'Estonia', 'Грузија':'Georgia', 'Чешка':'Czechia', 'Хрватска':'Croatia', 'Косово':'Kosovo', 'Република Косово':'Kosovo', 'Крим':'Crimean Tatars', 'Кримски Татари':'Crimean Tatars', 'Литванија':'Lithuania', 'Латвија':'Latvia', 'Унгарија':'Hungary', 'Македонија':'Macedonia', 'Молдавија':'Moldova', 'Полска':'Poland', 'Русија':'Russia', 'Романија':'Romania', 'Република Српска':'Republic of Srpska', 'Србија':'Serbia', 'Словачка':'Slovakia', 'Турција':'Turkey', 'Украина':'Ukraine', 'Грција':'Greece', 'Казахстан':'Kazakhstan', 'Татарстан':'Tatarstan' },
'ro':{ 'Albania':'Albania', 'Austria':'Austria', 'Azerbaidjan':'Azerbaijan', 'Bașkortostan':'Bashkortostan', 'Bașchiria':'Bashkortostan', 'Belarus':'Belarus', 'Bulgaria':'Bulgaria', 'Armenia':'Armenia', 'Bosnia și Herțegovina':'Bosnia and Herzegovina', 'Esperanto':'Esperanto', 'Estonia':'Estonia', 'Georgia':'Georgia', 'Cehia':'Czechia', 'Croația':'Croatia', 'Kosovo':'Kosovo', 'Crimeea':'Crimean Tatars', 'Lituania':'Lithuania', 'Letonia':'Latvia', 'Ungaria':'Hungary', 'Macedonia':'Macedonia', 'Republica Moldova':'Moldova', 'Polonia':'Poland', 'Rusia':'Russia', 'România':'Romania', 'Republika Srpska':'Republic of Srpska', 'Serbia':'Serbia', 'Slovacia':'Slovakia', 'Turcia':'Turkey', 'Ucraina':'Ukraine', 'Grecia':'Greece', 'Kazahstan':'Kazakhstan', 'Erzia':'Erzia'},
'ru':{ 'Албания':'Albania', 'Австрия':'Austria', 'Азербайджан':'Azerbaijan', 'Башкортостан':'Bashkortostan', 'Беларусь':'Belarus', 'Белоруссия':'Belarus', 'Болгария':'Bulgaria', 'Армения':'Armenia', 'Босния и Герцеговина':'Bosnia and Herzegovina', 'Эрзя':'Erzia', 'Эсперантида':'Esperanto', 'Эсперанто':'Esperanto', 'Эстония':'Estonia', 'Грузия':'Georgia', 'Чехия':'Czechia', 'Хорватия':'Croatia', 'Косово':'Kosovo', 'Крымские татары':'Crimean Tatars', 'Литва':'Lithuania', 'Латвия':'Latvia', 'Венгрия':'Hungary', 'Республика Македония':'Macedonia', 'Македония':'Macedonia', 'Северная Македония':'Macedonia', 'Молдавия':'Moldova', 'Польша':'Poland', 'Россия':'Russia', 'Румыния':'Romania', 'Сербская Республика':'Republic of Srpska', 'Республика Сербская':'Republic of Srpska', 'Сербия':'Serbia', 'Словакия':'Slovakia', 'Турция':'Turkey', 'Украина':'Ukraine', 'Греция':'Greece', 'Казахстан':'Kazakhstan', },
'sq':{ 'Shqipërisë':'Albania', 'Shqipëria':'Albania', 'Austria':'Austria', 'Azerbajxhanit':'Azerbaijan', 'Azerbajxhani':'Azerbaijan', 'Bashkortostani':'Bashkortostan', 'Bjellorusia':'Belarus', 'Bullgaria':'Bulgaria', 'Armenisë':'Armenia', 'Armenia':'Armenia', 'Bosnja dhe Hercegovina':'Bosnia and Herzegovina', 'Gjuha esperanto':'Esperanto', 'Estonia':'Estonia', 'Gjeorgjisë':'Georgia', 'Gjeorgjia':'Georgia', 'Republika Çeke':'Czechia', 'Kroacisë':'Croatia', 'Kroacia':'Croatia', 'Kosovës':'Kosovo', 'Kosova':'Kosovo', 'Lituania':'Lithuania', 'Letonia':'Latvia', 'Hungaria':'Hungary', 'Maqedonisë':'Macedonia', 'Moldavinë':'Moldova', 'Moldavia':'Moldova', 'Polonisë':'Poland', 'Polonia':'Poland', 'Rusisë':'Russia', 'Rusia':'Russia', 'Rumania':'Romania', 'Serbia':'Serbia', 'Sllovakia':'Slovakia', 'Turqisë':'Turkey', 'Turqia':'Turkey', 'Ukraina':'Ukraine', 'Greqisë':'Greece', 'Greqia':'Greece', 'Kazakistanin':'Kazakhstan', 'Kazakistani':'Kazakhstan', },
'sr':{ 'Албанија':'Albania', 'Аустрија':'Austria', 'Атербејџан':'Azerbaijan', 'Азербејџан':'Azerbaijan', 'Башкортостан':'Bashkortostan', 'Белорусија':'Belarus', 'Бугарска':'Bulgaria', 'Јерменија':'Armenia', 'Босна и Херцеговина':'Bosnia and Herzegovina', 'Ерзја':'Erzia', 'Есперанто':'Esperanto', 'Естонија':'Estonia', 'Грузија':'Georgia', 'Чешка':'Czechia', 'Hrvatska':'Croatia', 'Хрватска':'Croatia', 'Република Косово':'Kosovo', 'Кримски Татари':'Crimean Tatars', 'Литванија':'Lithuania', 'Летонија':'Latvia', 'Мађарска':'Hungary', 'Македонија':'Macedonia', 'Република Македонија':'Macedonia', 'Молдавија':'Moldova', 'Пољска':'Poland', 'Руска Империја':'Russia', 'Rusija':'Russia', 'Русија':'Russia', 'Румунија':'Romania', 'Република Српска':'Republic of Srpska', 'Србија':'Serbia', 'Словачка':'Slovakia', 'Турска':'Turkey', 'Украјина':'Ukraine', 'грчка':'Greece', 'Грчка':'Greece', 'Казахстан':'Kazakhstan', },
'tt':{ 'Албания':'Albania', 'Австрия':'Austria', 'Азәрбайҗан':'Azerbaijan', 'Башкортстан':'Bashkortostan', 'Беларусия':'Belarus', 'Болгария':'Bulgaria', 'Әрмәнстан':'Armenia', 'Босния һәм Герцеговина':'Bosnia and Herzegovina', 'Эрзя':'Erzia', 'Ирзә':'Erzia', 'Эсперанто':'Esperanto', 'Эстония':'Estonia', 'Гөрҗистан':'Georgia', 'Чехия':'Czechia', 'Хорватия':'Croatia', 'Косово Җөмһүрияте':'Kosovo', 'Кырым татарлары':'Crimean Tatars', 'Литва':'Lithuania', 'Latviä':'Latvia', 'Маҗарстан':'Hungary', 'Македония Җөмһүрияте':'Macedonia', 'Македония':'Macedonia', 'Молдова':'Moldova', 'Польша':'Poland', 'РФ':'Russia', 'Русия':'Russia', 'Румыния':'Romania', 'Сербия':'Serbia', 'Словакия':'Slovakia', 'Төркия':'Turkey', 'Украина':'Ukraine', 'Греция':'Greece', 'Казакъстан':'Kazakhstan', },
'tr':{ 'Arnavutluk':'Albania', 'Avusturya':'Austria', 'Azerbaycan':'Azerbaijan', 'Başkurdistan':'Bashkortostan', 'Beyaz Rusya':'Belarus', 'Bulgaristan':'Bulgaria', 'Ermenistan':'Armenia', 'Bosna-Hersek':'Bosnia and Herzegovina', 'Erzya':'Erzia', 'Esperanto':'Esperanto', 'Estonya':'Estonia', 'Gürcistan':'Georgia', 'Çek Cumhuriyeti':'Czechia', 'Hırvatistan':'Croatia', 'Kosova':'Kosovo', 'Kırım':'Crimean Tatars', 'Kırım Tatar':'Crimean Tatars', 'Kırım Tatarları':'Crimean Tatars', 'Litvanya':'Lithuania', 'Letonya':'Latvia', 'Macaristan':'Hungary', 'Makedonya Cumhuriyeti':'Macedonia', 'Makedonya':'Macedonia', 'Moldova':'Moldova', 'Polonya':'Poland', 'Rusya':'Russia', 'Romanya':'Romania', 'Sırp Cumhuriyeti':'Republic of Srpska', 'Sırbistan':'Serbia', 'Slovakya':'Slovakia', 'Türkiye':'Turkey', 'Ukrayna':'Ukraine', 'Yunanistan':'Greece', 'Kazakistan':'Kazakhstan', 'Tataristan':'Tatarstan' },
'uk':{ 'Албанія':'Albania', 'Австрія':'Austria', 'Азербайджан':'Azerbaijan', 'Башкортостан':'Bashkortostan', 'Білорусь':'Belarus', 'Болгарія':'Bulgaria', 'Вірменія':'Armenia', 'Боснія':'Bosnia and Herzegovina', 'Боснія і Герцеговина':'Bosnia and Herzegovina', 'Ерзя':'Erzia', 'Есперантида':'Esperanto', 'Есперанто':'Esperanto', 'Естонія':'Estonia', 'Грузія':'Georgia', 'Чехія':'Czechia', 'Хорватія':'Croatia', 'Косово':'Kosovo', 'Кримські Татари':'Crimean Tatars', 'Кримські татари':'Crimean Tatars', 'Литва':'Lithuania', 'Латвія':'Latvia', 'Угорщина':'Hungary', 'Македонія':'Macedonia', 'Молдова':'Moldova', 'Польща':'Poland', 'Російська Федерація':'Russia', 'Росія':'Russia', 'Румунія':'Romania', 'Республіка Сербська':'Republic of Srpska', 'Сербія':'Serbia', 'Словаччина':'Slovakia', 'Туреччина':'Turkey', 'Туречинна':'Turkey', 'Україна':'Ukraine', 'Греція':'Greece', 'Казахстан':'Kazakhstan', },
'hu':{ 'Albánia':'Albania', 'Ausztria':'Austria', 'Azerbajdzsán':'Azerbaijan', 'Baskirföld':'Bashkortostan', 'Belorusz':'Belarus', 'Bulgária':'Bulgaria', 'Örményország':'Armenia', 'Bosznia és Hercegovina':'Bosnia and Herzegovina', 'Eszperantó':'Esperanto', 'Észtország':'Estonia', 'Grúzia':'Georgia', 'Csehország':'Czechia', 'Horvátország':'Croatia', 'Koszovo':'Kosovo', 'Krími tatárok':'Crimean Tatars', 'Litvánia':'Lithuania', 'Lettország':'Latvia', 'Magyarország':'Hungary', 'Macedónia':'Macedonia', 'Moldávia':'Moldova', 'Lengyelország':'Poland', 'Oroszország':'Russia', 'Románia':'Romania', 'Boszniai Szerb Köztársaság':'Republic of Srpska', 'Szerbia':'Serbia', 'Szlovákia':'Slovakia', 'Törökország':'Turkey', 'Ukrajna':'Ukraine', 'Görögország':'Greece', 'Kazahsztán':'Kazakhstan', },
'kk':{ 'Албания':'Albania', 'Аустрия':'Austria', 'Әзірбайжан':'Azerbaijan', 'Башқұртстан':'Bashkortostan', 'Беларусь':'Belarus', 'Болгария':'Bulgaria', 'Армения':'Armenia', 'Босния және Герцеговина':'Bosnia and Herzegovina', 'Эсперанто':'Esperanto', 'Эстония':'Estonia', 'Грузия':'Georgia', 'Чехия':'Czechia', 'Хорватия':'Croatia', 'Косово':'Kosovo', 'Қырым татарлары':'Crimean Tatars', 'Литва':'Lithuania', 'Латвия':'Latvia', 'Мажарстан':'Hungary', 'Македония':'Macedonia', 'Молдова':'Moldova', 'Польша':'Poland', 'Ресей':'Russia', 'Румыния':'Romania', 'Сербия':'Serbia', 'Словакия':'Slovakia', 'Түркия':'Turkey', 'Украина':'Ukraine', 'Грекия':'Greece', 'Қазақстан':'Kazakhstan', },
'et':{ 'Albaania':'Albania', 'Austria':'Austria', 'Aserbaidžaan':'Azerbaijan', 'Baškortostanu':'Bashkortostan', 'Baškortostan':'Bashkortostan', 'Valgevene':'Belarus', 'Bulgaaria':'Bulgaria', 'Armeenia':'Armenia', 'Bosnia ja Hertsegoviina':'Bosnia and Herzegovina', 'Esperanto':'Esperanto', 'Eesti':'Estonia', 'Gruusia':'Georgia', 'Tšehhi':'Czechia', 'Horvaatia':'Croatia', 'Kosovo':'Kosovo', 'Krimski Tatari':'Crimean Tatars', 'Leedu':'Lithuania', 'Läti':'Latvia', 'Ungari':'Hungary', 'Makedoonia':'Macedonia', 'Moldova':'Moldova', 'Poola':'Poland', 'Venemaa':'Russia', 'Rumeenia':'Romania', 'Serblaste Vabariik':'Republic of Srpska', 'Republika Srpska':'Republic of Srpska', 'Serbia':'Serbia', 'Slovakkia':'Slovakia', 'Türgi':'Turkey', 'Ukraina':'Ukraine', 'Kreeka':'Greece', 'Kasahstan':'Kazakhstan', 'Ersa':'Erzia'},
'hr':{ 'Albaniji':'Albania', 'Albanija':'Albania', 'Austriji':'Austria',  'Austrija':'Austria', 'Azerbajdžanu':'Azerbaijan', 'Azerbajdžan':'Azerbaijan', 'Baškortostanu (Bashkortostan)':'Bashkortostan', 'Baškirska':'Bashkortostan', 'Bjelorusiji':'Belarus', 'Bjelorusija':'Belarus', 'Bugarskoj':'Bulgaria', 'Bugarska':'Bulgaria', 'Armeniji':'Armenia', 'Armenija':'Armenia', 'Bosni i Hercegovini':'Bosnia and Herzegovina', 'Bosne i Hercegovine':'Bosnia and Herzegovina', 'Bosna i Hercegovina':'Bosnia and Herzegovina', 'esperantu':'Esperanto', 'Esperanto':'Esperanto', 'Estoniji':'Estonia', 'Estonija':'Estonia', 'Gruziji':'Georgia', 'Gruziji (Georgia)':'Georgia', 'Gruzija':'Georgia', 'Češkoj (Czech)':'Czechia', 'Češka':'Czechia', 'Hrvatskoj':'Croatia', 'Hrvatska':'Croatia', 'Kosovo':'Kosovo', 'Kosovu':'Kosovo', 'Krimskih Tatara':'Crimean Tatars',  'Krimski Tatari':'Crimean Tatars', 'Litvi':'Lithuania', 'Litva':'Lithuania', 'Latviji':'Latvia', 'Latvija':'Latvia', 'Mađarskoj':'Hungary', 'Mađarska':'Hungary', 'Makedoniji':'Macedonia', 'Makedonija':'Macedonia', 'Moldaviji':'Moldova', 'Moldavija':'Moldova', 'Poljskoj':'Poland', 'Poljska':'Poland', 'Rusiji':'Russia', 'Rusija':'Russia', 'Rumunjskoj (Romania)':'Romania', 'Rumunjskoj':'Romania', 'Rumunjska':'Romania', 'Republici Srpskoj':'Republic of Srpska', 'Republika Srpska':'Republic of Srpska', 'Srbiji':'Serbia', 'Srbija':'Serbia', 'Slovačkoj':'Slovakia', 'Slovačkoj (Slovakia)':'Slovakia', 'Slovačka':'Slovakia', 'Turskoj':'Turkey', 'Turska':'Turkey', 'Ukrajini':'Ukraine', 'Ukrajina':'Ukraine', 'Grčkoj':'Greece', 'Grčka':'Greece', 'Kazahstanu':'Kazakhstan', 'Kazahstan':'Kazakhstan', 'Erziji (Erzya)':'Erzia', 'Erziji':'Erzia', 'Erzya':'Erzia'},
}
class BasicBot(
    # Refer pywikobot.bot for generic bot classes
    #SingleSiteBot,  # A bot only working on one site
    MultipleSitesBot,  # A bot only working on one site
    # CurrentPageBot,  # Sets 'current_page'. Process it in treat_page method.
    #                  # Not needed here because we have subclasses
    ExistingPageBot,  # CurrentPageBot which only treats existing pages
    NoRedirectPageBot,  # CurrentPageBot which only treats non-redirects
    AutomaticTWSummaryBot,  # Automatically defines summary; needs summary_key
):

    """
    An incomplete sample bot.

    @ivar summary_key: Edit summary message key. The message that should be used
        is placed on /i18n subdirectory. The file containing these messages
        should have the same name as the caller script (i.e. basic.py in this
        case). Use summary_key to set a default edit summary message.
    @type summary_key: str
    """

    summary_key = 'basic-changing'
    springList = {}
    templatesList = {}
    authors = {}
    authorsData = {}
    authorsArticles = {}
    missingCount = {}
    pagesCount = {}
    countryTable = {}
    lengthTable = {}
    womenAuthors = {} # authors of articles about women k:author v; (count,[list])
    otherCountriesList = {'pl':[], 'az':[], 'ba':[], 'be':[], 'be-tarask':[], 'bg':[], 'de':[], 'crh':[], 'el':[], 'et':[], 'myv':[], 'eo':[], 'hr':[], 'hy':[], 'ka':[], 'lv':[], 'lt':[], \
             'mk':[], 'ro':[], 'ru':[], 'sq':[], 'sr':[], 'tt':[], 'tr':[], 'uk':[], 'hu':[]}
    women = {'pl':0, 'az':0, 'ba':0, 'be':0, 'be-tarask':0, 'bg':0, 'de':0, 'crh':0, 'el':0, 'et':0, 'myv':0, 'eo':0, 'hr':0, 'hy':0, 'ka':0, 'lv':0, 'lt':0, \
             'mk':0, 'ro':0, 'ru':0, 'sq':0, 'sr':0, 'tt':0, 'tr':0, 'uk':0, 'hu':0}
    countryp = { 'pl':'kraj', 'az':'ölkə', 'ba':'ил', 'be':'краіна', 'be-tarask':'краіна', 'bg':'държава', 'de':'land', 'crh':'memleket', 'el':'country', 'et':'maa', \
                 'myv':'мастор', 'eo':'country', 'ka':'ქვეყანა', 'lv':'valsts', 'lt':'šalis', 'mk':'земја', 'ro':'țară', 'ru':'страна', 'sq':'country', \
                 'sr':'држава', 'tt':'ил', 'tr':'ülke', 'uk':'країна', 'hr':'zemlja', 'hy':'երկիր' }
    topicp = {'pl':'parametr', 'az':'qadınlar', 'ba':'тема', 'be':'тэма', 'be-tarask':'тэма', 'bg':'тема', 'de':'thema', 'crh':'mevzu', 'el':'topic', 'et':'teema', \
             'myv':'тема', 'eo':'topic', 'ka':'თემა', 'lv':'tēma', 'lt':'tema', 'mk':'тема', 'ro':'secțiune', 'ru':'тема', 'sq':'topic', 'sr':'тема', \
             'tt':'тема', 'tr':'konu', 'uk':'тема', 'hr':'tema', 'hy':'Թուրքիա|թեմա'}
    womenp = {'pl':'kobiety', 'az':'qadınlar', 'ba':'Ҡатын-ҡыҙҙар', 'be':'Жанчыны', 'be-tarask':'жанчыны', 'bg':'жени', 'de':'Frauen','el':'γυναίκες', 'et':'naised', \
              'ka':'ქალები', 'lv':'Sievietes','mk':'Жени', 'ro':'Femei', 'ru':'женщины', 'sq':'Gratë', 'sr':'Жене', 'tt':'Хатын-кызлар', 'tr':'Kadın',\
               'uk':'жінки', 'hu':'nők', 'hr':'Žene', 'hy':'Կանայք'}
    userp = {'pl':'autor', 'az':'istifadəçi', 'ba':'ҡатнашыусы', 'be':'удзельнік', 'be-tarask':'удзельнік', 'bg':'потребител', 'hu':'szerkesztő',\
             'de':'benutzer','crh':'qullanıcı','el':'user', 'et':'kasutaja', 'myv':'сёрмадыця', 'eo':'user', 'ka':'მომხმარებელი', 'lv':'dalībnieks', 'lt':'naudotojas',\
             'mk':'корисник', 'ro':'utilizator', 'ru':'участник', 'sq':'user', 'sr':'корисник', 'tt':'кулланучы', 'tr':'kullanıcı', 'uk':'користувач', 'hr':'suradnik', 'hy':'մասնակից' }

    def __init__(self, generator, **kwargs):
        """
        Constructor.

        @param generator: the page generator that determines on which pages
            to work
        @type generator: generator
        """
        # Add your own options to the bot and set their defaults
        # -always option is predefined by BaseBot class
        self.availableOptions.update({
            'replace': False,  # delete old text and write the new text
            'summary': None,  # your own bot summary
            'text': 'Test',  # add this text from option. 'Test' is default
            'top': False,  # append text on top of the page
            'outpage': u'User:mastiBot/test', #default output page
            'maxlines': 1000, #default number of entries per page
            'testprint': False, # print testoutput
            'negative': False, #if True negate behavior i.e. mark pages that DO NOT contain search string
            'test': False, # make verbose output
            'test2': False, # make verbose output
            'test3': False, # make verbose output
            'test4': False, # make verbose output
            'testartinfo': False, # make verbose output
            'testwomen': False, # make verbose output for women table
            'testwomenauthors': False, # make verbose output for women authors table
            'testnewbie': False, # make verbose output for newbies
            'testlength': False, # make verbose output for article length
            'testpickle': False, # make verbose output for article list load/save
            'testauthorwiki': False, # make verbose output for author/wiki 
            'short': False, # make short run
            'append': False, 
            'reset': False, # rebuild database from scratch
            'progress': False, #report progress

        })

        # call constructor of the super class
        #super(BasicBot, self).__init__(site=True, **kwargs)
        super(BasicBot, self).__init__(**kwargs)

        # assign the generator to the bot
        self.generator = generator

    def articleExists(self,art):
        #check if article already in springList
        result = False
        lang = art.site.code
        title = art.title()
        if self.getOption('testpickle'):
            pywikibot.output('testing existence: [%s:%s]' % (lang,title))
        if lang in self.springList.keys():
            for a in self.springList[lang]:
                if self.getOption('testpickle'):
                    pywikibot.output('checking existence: [%s:%s]==%s' % (lang,title,a['title']))
                if a['title'] == title:
                    result = True
                    return(result)
        return(result)

    def run(self):

        header = u'{{TNT|Wikimedia CEE Spring 2019 navbar}}\n\n'
        header += u'{{Wikimedia CEE Spring 2019/Statistics/Header}}\n\n'
        #header += u"Last update: '''<onlyinclude>{{#time: Y-m-d H:i|{{REVISIONTIMESTAMP}}}} UTC</onlyinclude>'''.\n\n"
        header += u"Last update: '''~~~~~'''.\n\n"
        footer = u''

        #load springList from previous run
        self.springList = self.loadArticleList()


        #generate dictionary of articles
        # article[pl:title] = pageobject
        ceeArticles = self.getArticleList()
        self.printArtList(ceeArticles)

        pywikibot.output(u'ART INFO')
        count = 1
        for a in ceeArticles:
            if self.articleExists(a):
                if self.getOption('testpickle'):
                    pywikibot.output('SKIPPING: [%s:%s]' % (a.site.code,a.title()))
            else:    
                aInfo = self.getArtInfo(a)
                if self.getOption('test'):
                    pywikibot.output(aInfo)
            count += 1
            if self.getOption('progress') and not count % 10:
                pywikibot.output('[%i] Lang:%s Article:%s' % (count,aInfo['lang'],aInfo['title']))
            #populate article list per language
            if aInfo['lang'] not in self.springList.keys():
                self.springList[aInfo['lang']] = []
            self.springList[aInfo['lang']].append(aInfo)
            #populate authors list
            if aInfo['newarticle']:
                user = aInfo['creator']
                if self.getOption('testnewbie'):
                    pywikibot.output('NEWBIE CREATOR:%s' % user)
                if aInfo['creator'] not in self.authors.keys():
                    self.authors[aInfo['creator']] = 1
                else:
                    self.authors[aInfo['creator']] += 1
            else:
                user = aInfo['template']['user']
                if self.getOption('testnewbie'):
                    pywikibot.output('NEWBIE FROM TEMPLATE:%s' % user)
                if aInfo['template']['user'] not in self.authors.keys():
                    self.authors[aInfo['template']['user']] = 1
                else:
                    self.authors[aInfo['template']['user']] += 1
            self.newbie(aInfo['lang'],user)


        self.printArtInfo(self.springList)
        #print self.springList

        # save list for the future
        self.saveArticleList(self.springList)

        self.createCountryTable(self.springList) #generate results for pages about countries 
        self.createWomenTable(self.springList) #generate results for pages about women
        self.createWomenAuthorsTable(self.springList) #generate results for pages about women
        self.createLengthTable(self.springList) #generate results for pages length
        self.createAuthorsArticles(self.springList) #generate list of articles per author/wiki

        self.generateOtherCountriesTable(self.otherCountriesList,self.getOption('outpage')+u'/Other countries',header,footer)
        self.generateResultCountryTable(self.countryTable,self.getOption('outpage'),header,footer)
        self.generateResultArticleList(self.springList,self.getOption('outpage')+u'/Article list',header,footer)
        self.generateResultAuthorsPage(self.authors,self.getOption('outpage')+u'/Authors list',header,footer)
        self.generateAuthorsCountryTable(self.authorsArticles,self.getOption('outpage')+u'/Authors list/per wiki',header,footer)
        self.generateResultWomenPage(self.women,self.getOption('outpage')+u'/Articles about women',header,footer)
        self.generateResultWomenAuthorsTable(self.womenAuthors,self.getOption('outpage')+u'/Articles about women/Authors',header,footer) #generate results for pages about women
        #self.generateResultLengthPage(self.lengthTable,self.getOption('outpage')+u'/Article length',header,footer)

        return


    def newbie(self,lang,user):
        #check if user is a newbie
        newbieLimit =  datetime.strptime("2017-12-20T12:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        if self.getOption('testnewbie'):
            pywikibot.output('NEWBIE:%s' % self.authorsData)
        if user in self.authorsData.keys():
            if lang not in self.authorsData[user]['wikis']:
                self.authorsData[user]['wikis'].append(lang)
            if self.authorsData[user]['anon']:
                return(False)
            if not self.authorsData[user]['newbie']:
                return(False)
        else:
            self.authorsData[user] = {'newbie':True, 'wikis':[lang], 'anon':False, 'gender':'unknown'}
        userpage = u'user:' + user
        site = pywikibot.Site(lang,fam='wikipedia')
        #page = pywikibot.Page(site,userpage)
        if self.getOption('testnewbie'):
            pywikibot.output('GETTING USER DATA:[[:%s:%s]]' % (lang,userpage))
        try:
            userdata = pywikibot.User(site,userpage)
        except:
            pywikibot.output('NEWBIE Exception: [[%s:user:%s]]' % (lang,user))
            return(False)
        self.authorsData[user]['anon'] = userdata.isAnonymous()
        if self.authorsData[user]['anon']:
            return(False)
        usergender = userdata.gender()
        if not self.authorsData[user]['gender'] == 'female':
            self.authorsData[user]['gender'] = usergender
        if self.authorsData[user]['newbie']:
            reg = userdata.registration()
            if reg:
                register = datetime.strptime(str(reg), "%Y-%m-%dT%H:%M:%SZ")
                if register < newbieLimit:
                    self.authorsData[user]['newbie'] = False
            else:
                self.authorsData[user]['newbie'] = False
            if self.getOption('testnewbie'):
                pywikibot.output('NEWBIE [%s]:%s' % (user,self.authorsData[user]))
                pywikibot.output('registration:%s' % reg)

        return(self.authorsData[user]['newbie'])

    def createCountryTable(self,aList):
        #creat dictionary with la:country article counts
        if self.getOption('test2'):
            pywikibot.output(u'createCountryTable')
        artCount = 0
        countryCount = 0
        for l in aList.keys():
            for a in aList[l]:
                #print a
                artCount += 1
                lang = a['lang'] #source language
                tmpl = a['template'] #template data {country:[clist], women:T/F, nocountry:T/F}
                if self.getOption('test2'):
                    pywikibot.output('tmpl:%s' % tmpl)
                if u'country' in tmpl.keys():
                    cList = tmpl['country']
                else:
                    continue
                if lang not in self.countryTable.keys():
                        self.countryTable[lang] = {}
                if tmpl['nocountry']:
                    if 'Empty' in self.countryTable[lang].keys():
                        self.countryTable[lang]['Empty'] += 1
                    else:
                        self.countryTable[lang]['Empty'] = 1
                else:
                    for c in cList:
                        if c not in self.countryTable[lang].keys():
                            self.countryTable[lang][c] = 0
                        self.countryTable[lang][c] += 1
                        countryCount += 1
                        if self.getOption('test2'):
                            pywikibot.output(u'art:%i coutry:%i, [[%s:%s]]' % (artCount, countryCount, lang, a['title']))
        return

    def createWomenTable(self,aList):
        #creat dictionary with la:country article counts
        if self.getOption('test') or self.getOption('testwomen'):
            pywikibot.output(u'createWomenTable')
            pywikibot.output(self.women)
        artCount = 0
        countryCount = 0
        for l in aList.keys():
            for a in aList[l]:
                #print a
                artCount += 1
                lang = a['lang'] #source language
                tmpl = a['template'] #template data {country:[clist], women:T/F}
                if u'woman' in tmpl.keys():
                    if not tmpl['woman']:
                        continue
                else:
                    continue
                if self.getOption('testwomen'):
                    pywikibot.output('tmpl:%s' % tmpl)
                if lang not in self.women.keys():
                    self.women[lang] = 1
                else:
                    self.women[lang] += 1
                if self.getOption('testwomen'):
                    pywikibot.output('self.women[%s]:%i' % (lang,self.women[lang]))
                countryCount += 1
                if self.getOption('test') or self.getOption('testwomen'):
                    pywikibot.output(u'art:%i Women:True [[%s:%s]]' % (artCount, lang, a['title']))
        if self.getOption('testwomen'):
            pywikibot.output('**********')
            pywikibot.output('self.women')
            pywikibot.output('**********')
            pywikibot.output(self.women)
        return

    def createWomenAuthorsTable(self,aList):
        #creat dictionary with la:country article counts
        if self.getOption('test') or self.getOption('testwomenauthors'):
            pywikibot.output(u'createWomenAuthorsTable')
            pywikibot.output(self.womenAuthors)
        artCount = 0
        countryCount = 0
        for l in aList.keys():
            for a in aList[l]:
                #print a
                artCount += 1

                if self.getOption('testwomenauthors'):
                    pywikibot.output('article:%s' % a)

                lang = a['lang'] #source language
                tmpl = a['template'] #template data {country:[clist], women:T/F}
                newart = a['newarticle']
                womanart = tmpl['woman']
                if not newart:
                    if self.getOption('test') or self.getOption('testwomenauthors'):
                        pywikibot.output(u'Skipping updated [%i]: [[%s:%s]]' % (artCount,lang,a['title']))
                    continue
                if not womanart:
                    if self.getOption('test') or self.getOption('testwomenauthors'):
                        pywikibot.output(u'Skipping NOT WOMAN [%i]: [[%s:%s]]' % (artCount,lang,a['title']))
                    continue
                user = a['creator']
                if user in self.womenAuthors.keys():
                    self.womenAuthors[user]['count'] += 1
                    self.womenAuthors[user]['list'].append(lang+':'+a['title'])
                else:
                    self.womenAuthors[user] = {'count':1, 'list':[lang+':'+a['title']]}


        if self.getOption('testwomenauthors'):
            pywikibot.output('**********')
            pywikibot.output('self.women.authors')
            pywikibot.output('**********')
            pywikibot.output(self.womenAuthors)
        return

    def createLengthTable(self,aList):
        #creat dictionary with la:country article counts
        if self.getOption('test') or self.getOption('testwomen'):
            pywikibot.output(u'createLengthTable')
            pywikibot.output(self.lengthTable)
        artCount = 0
        countryCount = 0
        for l in aList.keys():
            for a in aList[l]:
                if a['newarticle']:
                    artCount += 1
                    lang = a['lang'] #source language
                    title = lang + ':' + a['title'] #art title

                    if self.getOption('testlength'):
                        pywikibot.output('Title:%s' % title)
                    self.lengthTable[title] = (a['charcount'],a['wordcount'])
                    if self.getOption('testlength'):
                        pywikibot.output('self.lengthtable[%s]:%s' % (title,self.lengthTable[title]))

        if self.getOption('testlength'):
            pywikibot.output('**********')
            pywikibot.output('self.lengthTable')
            pywikibot.output('**********')
            pywikibot.output(self.lengthTable)
        return

    def createAuthorsArticles(self,aList):
        #creat dictionary with author:wiki:{count,[artlist]} in self.authorsArticles
        if self.getOption('test') or self.getOption('testauthorwiki'):
            pywikibot.output(u'createAuthorsArticles')

        wikilist = list(aList.keys())

        artCount = 0
        countryCount = 0
        for l in aList.keys():
            for a in aList[l]:
                author = a['creator']
                if author not in self.authorsArticles.keys():
                    self.authorsArticles[author] = {}
                    for lang in wikilist:
                        self.authorsArticles[author][lang] = {'count':0, 'list':[]}

                self.authorsArticles[author][l]['count'] += 1    
                self.authorsArticles[author][l]['list'].append(a['title'])

        if self.getOption('testauthorwiki'):
            pywikibot.output('**********')
            pywikibot.output('createAuthorsArticles')
            pywikibot.output('**********')
            pywikibot.output(self.authorsArticles)
        return


    def loadArticleList(self):
        #load article list form pickled dictionary
        result = {}
        if self.getOption('reset'):
            if self.getOption('testpickle'):
                pywikibot.output('PICKLING SKIPPED at %s' % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            if self.getOption('testpickle'):
                pywikibot.output('PICKLING LOAD at %s' % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            try:
                with open('masti/CEESpring2019.dat', 'rb') as datfile:
                    result = pickle.load(datfile)
            except (IOError, EOFError):
                # no saved history exists yet, or history dump broken
                if self.getOption('testpickle'):
                    pywikibot.output('PICKLING FILE NOT FOUND')
                result = {}
        if self.getOption('testpickle'):
            pywikibot.output('PICKLING RESULT:%s' % result)
        return(result)

    def saveArticleList(self,artList):
        #save list as pickle file
        if self.getOption('testpickle'):
            pywikibot.output('PICKLING SAVE at %s' % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with open('masti/CEESpring2019.dat', 'wb') as f:
            pickle.dump(artList, f, protocol=config.pickle_protocol)


    def getArticleList(self):
        #generate article list
        artList = []

        #use pagegenerator to get articles linking to CEE templates
        for p in self.generator:
            #p = t.toggleTalkPage()
            pywikibot.output(u'Treating: %s' % p.title())
            d = p.data_item()
            pywikibot.output(u'WD: %s' % d.title() )
            dataItem = d.get()
            count = 0
            for i in self.genInterwiki(p):
                lang = self.lang(i.title(asLink=True,force_interwiki=True))
                #test switch
                if self.getOption('short'):
                    if lang not in ('hu','et'):
                         continue

                self.templatesList[lang] = i.title()
                pywikibot.output(u'Getting references to %s Lang:%s' % (i.title(asLink=True,force_interwiki=True), lang) )
                countlang = 0
                for p in i.getReferences(namespaces=1):
                    artParams = {}
                    art = p.toggleTalkPage()
                    if art.exists():
                        countlang += 1
                        artList.append(art)
                        if self.getOption('test'):
                            pywikibot.output(u'#%i/%i:%s:%s' % (count,countlang,lang,art.title()))
                        count += 1
        '''
        #get et.wiki article list
        if self.getOption('test'):
            pywikibot.output(u'GET ET WIKI')
        etwiki = pywikibot.Site('et',fam='wikipedia')
        lang = u'et'
        for etart in etArticles.keys():
            etpage = pywikibot.Page( etwiki, etart )
            if etpage.exists():
                artList.append(etpage)
                if self.getOption('test'):
                     pywikibot.output(u'#%i:%s:%s' % (count,lang,etpage.title()))
                count += 1
        #get hr.wiki article list
        if self.getOption('test'):
            pywikibot.output(u'GET HR WIKI')
        hrwiki = pywikibot.Site('hr',fam='wikipedia')
        lang = u'hr'
        for hrart in hrArticles.keys():
            hrpage = pywikibot.Page( hrwiki, hrart )
            if hrpage.exists():
                artList.append(hrpage)
                if self.getOption('test'):
                     pywikibot.output(u'#%i:%s:%s' % (count,lang,hrpage.title()))
                count += 1
        '''

        return(artList)

    def printArtList(self,artList):
        for p in artList:
            s = p.site
            l = s.code
            if self.getOption('test'):
                pywikibot.output(u'Page lang:%s : %s' % (l, p.title(asLink=True,force_interwiki=True)))
        return

    def printArtInfo(self,artInfo):
        #test print of article list result
        if self.getOption('testartinfo'):
            pywikibot.output(u'***************************************')
            pywikibot.output(u'**            artInfo                **')
            pywikibot.output(u'***************************************')
        for l in artInfo.keys():
            for a in artInfo[l]:
                if self.getOption('testartinfo'):
                    pywikibot.output(a)
        return

    def getWordCount(self,text):
        # get a word count for text
        return(len(text.split()))

    def getArtLength(self,text):
        # get article length
        return(len(text))

    def cleanUsername(self,user):
        # remove lang> from username
        if '>' in user:
            user = re.sub(r'.*\>','',user)
        return(user)        

    def getArtInfo(self,art):
        #get article language, creator, creation date
        artParams = {}
        talk = art.toggleTalkPage()
        if art.exists():
            creator, creationDate = self.getUpdater(art)
            creator = self.cleanUsername(creator)
            lang = art.site.code

            woman = self.checkWomen(art)            
            artParams['title'] = art.title()
            artParams['lang'] = lang
            artParams['creator'] = creator
            artParams['creationDate'] = creationDate
            artParams['newarticle'] = self.newArticle(art)
            cleantext = textlib.removeDisabledParts(art.text)
            artParams['charcount'] = self.getArtLength(cleantext)
            artParams['wordcount'] = self.getWordCount(cleantext)

            artParams['template'] = {u'country':[], 'user':creator, 'woman':woman, 'nocountry':False}

            if lang in CEEtemplates.keys() and talk.exists():
                TmplInfo = self.getTemplateInfo(talk, CEEtemplates[lang], lang)
                artParams['template'] = TmplInfo
            if not artParams['template']['woman']:
                artParams['template']['woman'] = woman
            if not len(artParams['template']['country']):
                artParams['template']['nocountry'] = True

            if u'template' not in artParams.keys():
                artParams['template'] = {u'country':[], 'user':creator, 'woman':woman, 'nocountry':True}
            #if not artParams['newarticle'] : 
            #if artParams['newarticle'] : 
            #    artParams['template']['user'] = creator
            if not artParams['template']['user'] == 'dummy' : 
                artParams['creator'] = artParams['template']['user']

            #print artParams
            if self.getOption('test2'):
                pywikibot.output('artParams:%s' % artParams)
        return(artParams)

    def checkWomen(self,art):
        #check if the article is about woman 
        #using WikiData
        try:
            d = art.data_item()
            if self.getOption('test4'):
                pywikibot.output(u'WD: %s' % d.title() )
            dataItem = d.get()
            #pywikibot.output(u'DataItem:%s' % dataItem.keys()  )
            claims = dataItem['claims']
        except:
            return(False)
        try:
            gender = claims["P21"]
        except:
            return(False)
        for c in gender:
            cjson = c.toJSON()
            genderclaim = cjson[u'mainsnak'][u'datavalue'][u'value'][u'numeric-id']
            if u'6581072' == str(genderclaim):
                if self.getOption('test4'):
                    pywikibot.output(u'%s:Woman' % art.title())
                return(True)
            else:
                if self.getOption('test4'):
                    pywikibot.output(u'%s:Man' % art.title())
                return(False)
        return(False)

    def getUpdater(self, art):
        #find author and update datetime of the biggest update within CEESpring
        creator, creationDate = art.getCreator()
        SpringStart =  datetime.strptime("2019-03-20T12:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        if self.newArticle(art):
            if self.getOption('test3'):
                pywikibot.output(u'New art creator %s:%s (T:%s)' % (art.title(asLink=True,force_interwiki=True),creator,creationDate))
            return(creator, creationDate)
        else:
            #for rv in art.revisions(reverse=True,starttime="2017-03-20T12:00:00Z",endtime="2017-06-01T00:00:00Z"):
            for rv in art.revisions(reverse=True, starttime=SpringStart):
                if self.getOption('test3'):
                    pywikibot.output(u'updated art editor %s:%s (T:%s)' % (art.title(asLink=True,force_interwiki=True),rv.user,rv.timestamp))
                if datetime.strptime(str(rv.timestamp), "%Y-%m-%dT%H:%M:%SZ") > SpringStart:
                    if self.getOption('test3'):
                        pywikibot.output(u'returning art editor %s:%s (T:%s)' % (art.title(asLink=True,force_interwiki=True),rv.user,rv.timestamp))
                    return(rv.user,rv.timestamp)
                else:
                    if self.getOption('test3'):
                        pywikibot.output(u'Skipped returning art editor %s:%s (T:%s)' % (art.title(asLink=True,force_interwiki=True),rv.user,rv.timestamp))
                #if self.getOption('test3'):
                #    pywikibot.output(u'updated art editor %s:%s (T:%s)' % (art.title(asLink=True,force_interwiki=True),rv['user'],rv['timestamp']))
            #    return(rv['user'],rv['timestamp'])
            return("'''UNKNOWN USER'''", creationDate)
       

    def newArticle(self,art):
        #check if the article was created within CEE Spring
        creator, creationDate = art.getCreator()
        SpringStart =  datetime.strptime("2019-03-20T12:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        SpringEnd = datetime.strptime("2019-06-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        return ( datetime.strptime(creationDate, "%Y-%m-%dT%H:%M:%SZ") > SpringStart )


    def getTemplateInfo(self,page,template,lang):
        param = {}
        #author, creationDate = self.getUpdater(page)
        parlist = {'country':[],'user':'dummy','woman':False, 'nocountry':False}
        #return dictionary with template params
        for t in page.templatesWithParams():
            title, params = t
            #print(title)
            #print(params)
            tt = re.sub(ur'\[\[.*?:(.*?)\]\]', r'\1', title.title())
            if self.getOption('test2'):
                pywikibot.output(u'tml:%s * %s * %s' % (title,tt,template) )
            if tt == template:
                paramcount = 1
                countryDef = False # check if country defintion exists
                parlist['woman'] = False
                parlist['country'] = []
                parlist['user'] = 'dummy'
                for p in params:
                    named, name, value = self.templateArg(p)
                    # strip square brackets from value
                    value = re.sub(ur"\'*\[*([^\]\|\']*).*", r'\1', value)
                    if not named:
                        name = str(paramcount)
                    param[name] = value
                    paramcount += 1
                    if self.getOption('test2'):
                        pywikibot.output(u'p:%s' % p )
                    #check username in template
                    if lang in self.userp.keys() and name.lower().startswith(self.userp[lang].lower()):
                        if self.getOption('test'):
                            pywikibot.output(u'user:%s:%s' % (name,value))
                        #if lang in self.userp.keys() and value.lower().startswith(self.userp[lang].lower()):
                        #    parlist['user'] = value
                        parlist['user'] = value
                    #check article about women
                    if lang in self.topicp.keys() and name.lower().startswith(self.topicp[lang].lower()):
                        if self.getOption('test2'):
                            pywikibot.output(u'topic:%s:%s' % (name,value))
                        if lang in self.womenp.keys() and value.lower().startswith(self.womenp[lang].lower()):
                            #self.women[lang] += 1
                            parlist['woman'] = True
                    #check article about country
                    if lang in self.countryp.keys() and name.lower().startswith(self.countryp[lang].lower()):
                        if self.getOption('test2'):
                            pywikibot.output(u'country:%s:%s' % (name,value))
                        if len(value)>0:
                            countryDef = True
                            if lang in countryNames.keys() and value in (countryNames[lang].keys()):
                                countryEN = countryNames[lang][value]
                                parlist['country'].append(countryEN)
                                if lang not in self.pagesCount.keys():
                                    self.pagesCount[lang] = {}
                                if countryEN in self.pagesCount[lang].keys():
                                    self.pagesCount[lang][countryEN] += 1
                                else:
                                    self.pagesCount[lang][countryEN] = 1
                            else:
                                parlist['country'].append(value)
                                self.otherCountriesList[lang].append(value)
                    if self.getOption('test'):
                        pywikibot.output(self.pagesCount)
                if self.getOption('test3'):
                    #pywikibot.output(u'PARAM:%s' % param)
                    pywikibot.output(u'PARLIST:%s' % parlist)
                return parlist
        return parlist

    def lang(self,template):
        return(re.sub(ur'\[\[(.*?):.*?\]\]',ur'\1',template))

    def genInterwiki(self,page):
        # yield interwiki sites generator
        iw = []
        try:
            d = page.data_item()
            pywikibot.output(u'WD: %s' % d.title() )
            dataItem = d.get()
            #pywikibot.output(u'DataItem:%s' % dataItem.keys()  )
            sitelinks = dataItem['sitelinks']
            for s in sitelinks:
                #if self.getOption('test'):
                #    pywikibot.output(u'SL iw: %s' % d)
                site = re.sub(ur'(.*)wiki$', ur'\1',s)
                if site == u'be_x_old':
                    site = u'be-tarask'
                ssite = pywikibot.Site(site,fam='wikipedia')
                spage = pywikibot.Page( ssite, title=sitelinks[s] )
                #pywikibot.output(u'gI Page: %s' % spage.title(asLink=True,force_interwiki=True) )
                iw.append( spage )
                #print( iw)
        except:
            pass
        #print(iw)
        return(iw)

    def generateOtherCountriesTable(self, res, pagename, header, footer):
        """
        Generates results page from res
        Starting with header, ending with footer
        Output page is pagename
        """
        locpagename = re.sub(ur'.*:','',pagename)

        finalpage = header

        if self.getOption('test'):
            pywikibot.output(u'**************************')
            pywikibot.output(u'generateOtherCountriesTable')
            pywikibot.output(u'**************************')
            pywikibot.output(u'OtherCountries:%s' % self.otherCountriesList)

        for c in self.otherCountriesList.keys():
            finalpage += u'\n== ' + c + u' =='
            pywikibot.output('== ' + c + u' ==')
            for i in self.otherCountriesList[c]:
                pywikibot.output('c:%s, i:%s' % (c,i))
                finalpage += u'\n# <nowiki>' + i + u'</nowiki>'

        finalpage += footer
        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        if self.getOption('test') or self.getOption('progress'):
            pywikibot.output(u'OtherCountries:%s' % outpage.title())
        outpage.text = finalpage
        outpage.save(summary=self.getOption('summary'))
        if self.getOption('test') or self.getOption('progress'):
            pywikibot.output(u'OtherCountries SAVED')

        return


    def generateResultCountryTable(self, res, pagename, header, footer):
        """
        Generates results page from res
        Starting with header, ending with footer
        Output page is pagename
        """
        locpagename = re.sub(ur'.*:','',pagename)

        finalpage = header

        if self.getOption('test'):
            pywikibot.output(u'**************************')
            pywikibot.output(u'generateResultCountryTable')
            pywikibot.output(u'**************************')

        #total counters
        countryTotals = {}
        for c in countryList:
            countryTotals[c] = 0

        # generate table header
        finalpage += u'\n{| class="wikitable sortable" style="text-align: center;"'
        finalpage += u'\n|-'
        finalpage += u'\n! wiki/country'
        finalpage += u' !! Total'
        for c in countryList:
            finalpage += u' !! ' + c
        finalpage += u' !! Total'
        
        # generate table rows
        for wiki in res.keys():
            finalpage += u'\n|-'
            finalpage += u'\n| [[' + locpagename + u'/Article list#'+ wiki + u'.wikipedia|' + wiki + u']]'
            wikiTotal = 0 # get the row total
            newline = '' # keep info for the table row
            for c in countryList:
                newline += u' || '
                if u'Other' in c:
                    if self.getOption('test3'):
                         pywikibot.output(u'other:%s' % c)
                         pywikibot.output(u'res[wiki]:%s' % res[wiki])
                    otherCountry = 0 # count other countries
                    for country in res[wiki]:
                       if country not in countryList and not country==u'':
                           if self.getOption('test3'):
                               pywikibot.output(u'country:%s ** otherCountry=%i+%i=%i' % (country,otherCountry,res[wiki][country],otherCountry+res[wiki][country]))
                           otherCountry += res[wiki][country]
                    newline += str(otherCountry)
                    wikiTotal += otherCountry # add to wiki total
                    countryTotals[c] += otherCountry
                else:
                    if c in res[wiki].keys():
                        if res[wiki][c]:
                            newline += str(res[wiki][c])
                            wikiTotal += res[wiki][c] # add to wiki total
                            countryTotals[c] += res[wiki][c]
            # add row (wiki) total to table
            finalpage += u" || '''" + str(wikiTotal) + "'''" + newline + u" || '''" + str(wikiTotal) + "'''"
            
        finalpage += u'\n|-'

        # generate totals
        totalTotal = 0
        finalpage += u"\n! Total: !! '''" + str(totalTotal) + "'''"
        for c in countryList:
            finalpage += u' !! ' + str(countryTotals[c])
            totalTotal += countryTotals[c]
        finalpage += u" || '''" + str(totalTotal) + "'''"
        # generate table footer
        finalpage += u'\n|}'

        finalpage += u"\n\n'''NOTE:''' the table counts references to respective countries. Article can reference more than 1 country"


        finalpage += footer

        if self.getOption('test2'):
            pywikibot.output(finalpage)

        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        if self.getOption('test'):
            pywikibot.output(u'WomenPage:%s' % outpage.title())
        outpage.text = finalpage
        outpage.save(summary=self.getOption('summary'))

        return

    def generateAuthorsCountryTable(self, res, pagename, header, footer):
        """
        Generates results page from res
        Starting with header, ending with footer
        Output page is pagename
        """
        locpagename = re.sub(ur'.*:','',pagename)

        finalpage = header

        pywikibot.output(u'***************************')
        pywikibot.output(u'generateAuthorsCountryTable')
        pywikibot.output(u'***************************')

        #total counters
        wikiTotals = {}
        wikiList = list(self.otherCountriesList.keys())
        for a in wikiList:
            wikiTotals[a] = 0

        # generate table header
        finalpage += u'\n{| class="wikitable sortable" style="text-align: center;"'
        finalpage += u'\n|-'
        finalpage += u'\n! author/wiki'
        finalpage += u' !! Total'
        for w in wikiList:
            finalpage += u' !! ' + w
        finalpage += u' !! Total'
        
        # generate table rows
        for author in res.keys():
            finalpage += u'\n|-'
            finalpage += u'\n| [[user:%s|%s]]' % (author,author)
            authorTotal = 0 # get the row total
            newline = '' # keep info for the table row
            for w in wikiList:
                newline += u' || '
                if w in res[author].keys():
                    if res[author][w]:
                        newline += str(res[author][w]['count'])
                        authorTotal += res[author][w]['count'] # add to author total (horizontal)
                        wikiTotals[w] += res[author][w]['count'] # add to wiki total {verical)

            # add row (wiki) total to table
            finalpage += u" || '''" + str(authorTotal) + "'''" + newline + u" || '''" + str(authorTotal) + "'''"
            
        finalpage += u'\n|-'

        # generate totals
        totalTotal = 0
        finalpage += u"\n! Total: !! '''" + str(totalTotal) + "'''"
        for w in wikiList:
            finalpage += u' !! ' + str(wikiTotals[w])
            totalTotal += wikiTotals[w]
        finalpage += u" || '''" + str(totalTotal) + "'''"
        # generate table footer
        finalpage += u'\n|}'

        finalpage += u"\n\n'''NOTE:''' the table counts all articles per author: both new and updated"


        finalpage += footer

        if self.getOption('testauthorwiki'):
            pywikibot.output(finalpage)

        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        if self.getOption('testauthorwiki'):
            pywikibot.output(u'authorListperWiki:%s' % outpage.title())
        outpage.text = finalpage
        outpage.save(summary=self.getOption('summary'))

        return


    def generateResultWomenPage(self, res, pagename, header, footer):
        """
        Generates results page from res
        Starting with header, ending with footer
        Output page is pagename
        """
        locpagename = re.sub(ur'.*:','',pagename)

        finalpage = header
        itemcount = 0
        artcount = 0
        finalpage += u'\n== Articles about women ==\n'

        finalpage += u'\n{| class="wikitable sortable" style="text-align: center;"'
        finalpage += u'\n!#'
        finalpage += u'\n!Wikipedia'
        finalpage += u'\n!Articles'

        #ath = sorted(self.authors, reverse=True)
        ath = sorted(res, key=res.__getitem__, reverse=True)
        for a in ath:
            itemcount += 1
            finalpage += u'\n|-\n| %i. || %s || %i' % (itemcount,a,res[a])
            artcount += res[a]
        # generate totals
        finalpage += u'\n|-\n! !! Total: !! %i' % artcount

        finalpage += u'\n|}'

        finalpage += u'\n\nTotal number of articles: ' + str(artcount)

        finalpage += "\n\n'''NOTE:''' page counts all articles - new and updated"

        finalpage += footer

        #pywikibot.output(finalpage)

        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        if self.getOption('test'):
            pywikibot.output(u'WomenPage:%s' % outpage.title())
        outpage.text = finalpage
        outpage.save(summary=self.getOption('summary'))
        return

    def generateResultWomenAuthorsTable(self, res, pagename, header, footer):
        """
        Generates results page from res
        Starting with header, ending with footer
        Output page is pagename
        """
        locpagename = re.sub(ur'.*:','',pagename)

        finalpage = header
        itemcount = 0
        artcount = 0
        finalpage += u'\n== Articles about women authors ==\n'

        finalpage += u'\n{| class="wikitable sortable" style="text-align: center;"'
        finalpage += u'\n!#'
        finalpage += u'\n!Author'
        finalpage += u'\n!Count'
        finalpage += u'\n!Articles'

        #ath = sorted(self.authors, reverse=True)
        ath = sorted(res, key=res.__getitem__, reverse=True)
        for a in ath:
            if a == 'dummy':
                author = "'''unkown'''"
            else:
                author =  a
            itemcount += 1
            finalpage += u'\n|-\n| %i. || %s || %s || %s' % (itemcount,author,res[a]['count'],'[[:'+']], [[:'.join(res[a]['list'])+']]')
            artcount += res[a]['count']
        # generate totals
        finalpage += u'\n|-\n! !! Total: !! %i !!' % artcount

        finalpage += u'\n|}'

        finalpage += u'\n\nTotal number of articles: ' + str(artcount)
        finalpage += "\n\n'''NOTE:''' page counts only newly created articles"
        finalpage += footer

        if self.getOption('testwomenauthors'):
            pywikibot.output(finalpage)

        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        if self.getOption('testwomenauthors'):
            pywikibot.output(u'WomenAuthorsPage:%s' % outpage.title())
        outpage.text = finalpage
        outpage.save(summary=self.getOption('summary'))
        return


    def generateResultLengthPage(self, res, pagename, header, footer):
        """
        Generates results page from res
        Starting with header, ending with footer
        Output page is pagename
        """
        locpagename = re.sub(ur'.*:','',pagename)

        csvpage = '<pre>'
        finalpage = header
        itemcount = 0
        finalpage += u'\n\nLength of new articles excluding disabled parts in text. Word count approximated.'
        finalpage += u'\n== Article length ==\n'
        #ath = sorted(self.authors, reverse=True)
        ath = sorted(res, key=res.__getitem__, reverse=True)
        if self.getOption('testlength'):
            pywikibot.output(u'LengthPage:%s' % ath)
 
        finalpage += u'\n{| class="wikitable sortable"'
        finalpage += u'\n!#'
        finalpage += u'\n!Article'
        finalpage += u'\n!Character count'
        finalpage += u'\n!Word count'
      

        for a in ath:
            itemcount += 1
            ccount,wcount = res[a]
            finalpage += u'\n|-\n| %i. || [[:%s]] || %i || %i'% (itemcount,a,ccount,wcount)
            csvpage += u'\n[[:%s]];%i;%i'% (a,ccount,wcount)
            if self.getOption('testlength'):
                pywikibot.output(u'\n|-\n| %i. || [[:%s]] || %i || %i'% (itemcount, a,ccount,wcount))

        finalpage += u'\n|}'

        finalpage += u'\n\nTotal number of articles: ' + str(itemcount)
        finalpage += footer
        csvpage += '\n</pre>'

        #pywikibot.output(finalpage)

        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        if self.getOption('test'):
            pywikibot.output(u'LengthPage:%s' % outpage.title())
        outpage.text = finalpage
        outpage.save(summary=self.getOption('summary'))

        # save csv version
        outpage = pywikibot.Page(pywikibot.Site(), pagename+'/csv')
        pywikibot.output(u'CSVLengthPage:%s' % pagename+'/csv')
        #pywikibot.output(csvpage)
        outpage.text = csvpage
        outpage.save(summary=self.getOption('summary'))

        return


    def generateResultAuthorsPage(self, res, pagename, header, footer):
        """
        Generates results page from res
        Starting with header, ending with footer
        Output page is pagename
        """
        locpagename = re.sub(ur'.*:','',pagename)

        finalpage = header
        itemcount = 0
        anon = 0
        women = 0
        newbies = 0
        finalpage += u'\n== Authors ==\n'
        finalpage += u'\n{| class="wikitable sortable" style="text-align: center;"'
        finalpage += u'\n!#'
        finalpage += u'\n!User'
        finalpage += u'\n!Articles'
        finalpage += u'\n!New user'
        finalpage += u'\n!Female'

        #ath = sorted(self.authors, reverse=True)
        ath = sorted(res, key=res.__getitem__, reverse=True)
        for a in ath:
            itemcount += 1
            if 'UNKNOWN USER' in a:
                finalpage += u'\n|-\n| %i. || %s || %i || ' % (itemcount,a,res[a])
            else:
                finalpage += u'\n|-\n| %i. || [[user:%s|%s]] || %i || ' % (itemcount,a,a,res[a])
            if self.authorsData[a]['newbie']: 
                newbies += 1
                finalpage += u'[[File:Noto Emoji Oreo 1f476 1f3fb.svg|25px]] || '
            else:
                finalpage += u'|| '
            if self.authorsData[a]['gender'] == u'female': 
                women += 1
                finalpage += u'[[File:Noto Emoji Oreo 2640.svg|25px]]'

            if self.authorsData[a]['anon']:
                anon += 1 

        finalpage += u'\n|-\n! !! Total: !! !! %i !! %i' % (newbies,women)
        finalpage += u'\n|}'


        finalpage += u'\n\n== Statistics =='
        finalpage += u'\n* Number of authors: ' + str(itemcount)
        finalpage += u'\n* Number of not registered authors: ' + str(anon)
        finalpage += u'\n* Number of female  authors: ' + str(women)
        finalpage += u'\n* Number of new authors: ' + str(newbies)

        finalpage += footer

        #pywikibot.output(finalpage)

        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        if self.getOption('test'):
            pywikibot.output(u'AuthorsPage:%s' % outpage.title())
        outpage.text = finalpage
        outpage.save(summary=self.getOption('summary'))
        return

    def generateResultArticleList(self, res, pagename, header, footer):
        """
        Generates results page from res
        Starting with header, ending with footer
        Output page is pagename
        """
        locpagename = re.sub(ur'.*:','',pagename)

        finalpage = header
        
        itemcount = 0
        newartscount = 0
        updartscount = 0
        #go by language
        for l in res.keys():
            artCount = 0
            newarts = 0
            updarts = 0

            #print('[[:' + i + u':' + self.templatesList[i] +u'|' + i + u' wikipedia]]')
            if l in self.templatesList.keys():
                finalpage += u'\n== [[:' + l + ':' + self.templatesList[l] +u'|' + l + u'.wikipedia]] =='
            else:
                finalpage += u'\n== ' + l + u'.wikipedia =='
            finalpage += u'\n=== ' + l + u'.wikipedia new articles ==='
            finalpage += u'\n{| class="wikitable"'
            finalpage += u'\n!#'
            finalpage += u'\n!Article'
            finalpage += u'\n!User'
            finalpage += u'\n!Date'
            finalpage += u'\n!About'
            updatedArticles = u'\n\n=== ' + l + u'.wikipedia updated articles ==='
            updatedArticles += u'\n{| class="wikitable"'
            updatedArticles += u'\n!#'
            updatedArticles += u'\n!Article'
            updatedArticles += u'\n!User'
            updatedArticles += u'\n!About'
            for i in res[l]:
                if self.getOption('test3'):
                    pywikibot.output(u'Generating line from: %s:' % i )
                itemcount += 1
                artCount += 1
                if i['newarticle']:
                    newarts += 1
                    newartscount += 1
                    artLine = u'\n|-\n| %i. || [[:%s:%s]] || %s || %s || '  % (newarts,i['lang'],i['title'],i['creator'],i['creationDate'])
                    cList = []
                    for a in i['template']['country']:
                        if a in countryList:
                            cList.append(a)
                        else:
                            cList.append(u"'''" + a + u"'''")
                    finalpage += artLine + ', '.join(cList)
                    if self.getOption('test3'):
                        pywikibot.output(artLine + u' (NEW)')
                else:
                    #finalpage += u" '''(updated)'''"
                    updarts += 1
                    updartscount += 1
                    if i['template']['user']:
                        artLine = u'\n|-\n| %i. || [[:%s:%s]] || %s || ' % (updarts,i['lang'],i['title'],i['template']['user'])
                    else:
                        artLine = u'\n|-\n| %i. || [[:%s:%s]] || %s || ' % (updarts,i['lang'],i['title'],"'''unknown'''")

                    uList = []
                    for a in i['template']['country']:

                        if a in countryList:
                            uList.append(a)
                        else:
                            uList.append(u"'''" + a + u"'''")
                    updatedArticles += artLine + ', '.join(uList)
                    if self.getOption('test3'):
                        pywikibot.output(artLine + u" '''(updated)'''")

            finalpage += u'\n|}'
            finalpage += updatedArticles + u'\n|}'
            finalpage += u'\nTotal number of articles ' + l + u'.wikipedia:' + str(artCount)

        finalpage += u'\n\n== Statistics =='
        finalpage += u'\n\nNumber of new articles: ' + str(newartscount)
        finalpage += u'\n\nNumber of updated articles: ' + str(updartscount)
        finalpage += u"\n\n'''Total number of articles: " + str(itemcount) + u"'''"
        finalpage += footer
        #pywikibot.output(finalpage)

        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        if self.getOption('test'):
            pywikibot.output(u'ArticlesPage:%s' % outpage.title())
        outpage.text = finalpage        
        outpage.save(summary=self.getOption('summary'))
        return

    def templateWithNamedParams(self):
        """
        Iterate template as returned by templatesWithNames()

        @return: a generator that yields a tuple for each param of a template
            type: named, int
            name: name of param
            value: value of param
        @rtype: generator
        """
        # TODO

    def templateArg(self, param):
        """
        return name,value for each template param

        input text in form "name = value"
        @return: a tuple for each param of a template
            named: named (True) or int
            name: name of param or None if numbered
            value: value of param
        @rtype: tuple
        """
        # TODO
        paramR = re.compile(ur'(?P<name>.*)=(?P<value>.*)')
        if '=' in param:
            match = paramR.search(param)
            named = True
            name = match.group("name").strip()
            value = match.group("value").strip()
        else:
           named = False
           name = None
           value = param
        #test
        if self.getOption('test'):
            pywikibot.output(u'name:%s:value:%s' % (name, value))
        return named, name, value

def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: list of unicode
    """
    options = {}
    # Process global arguments to determine desired site
    local_args = pywikibot.handle_args(args)

    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()

    # Parse command line arguments
    for arg in local_args:

        # Catch the pagegenerators options
        if genFactory.handleArg(arg):
            continue  # nothing to do here

        # Now pick up your own options
        arg, sep, value = arg.partition(':')
        option = arg[1:]
        if option in ('summary', 'text', 'outpage', 'maxlines'):
            if not value:
                pywikibot.input('Please enter a value for ' + arg)
            options[option] = value
        # take the remaining options as booleans.
        # You will get a hint if they aren't pre-definded in your bot class
        else:
            options[option] = True

    gen = genFactory.getCombinedGenerator()
    if gen:
        # The preloading generator is responsible for downloading multiple
        # pages from the wiki simultaneously.
        gen = pagegenerators.PreloadingGenerator(gen)
        # pass generator and private options to the bot
        bot = BasicBot(gen, **options)
        bot.run()  # guess what it does
        return True
    else:
        pywikibot.bot.suggest_help(missing_generator=True)
        return False

if __name__ == '__main__':
    main()
