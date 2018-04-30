#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This bot creates pages listing most required pages;
Wikipedia:Propozycje tematów/Najwięcej linkujących

Call: python pwb.py masti/ms-requiredredlinks.py -start:'!' -summary:"Bot aktualizuje stronę" -outpage:'Wikipedia:Propozycje tematów/Najwięcej linkujących'

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

from pywikibot.bot import (
    SingleSiteBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)
from pywikibot.tools import issue_deprecation_warning

import re
import datetime

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}


class BasicBot(
    # Refer pywikobot.bot for generic bot classes
    SingleSiteBot,  # A bot only working on one site
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
    results = {}

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
            'test': False, #test printouts
            'testlinks': False, #test printouts
            'progress': False, #show progress
            'resprogress': False, #show progress in generating results
            'minlinks': 50, #print only >minlinks results

        })

        # call constructor of the super class
        super(BasicBot, self).__init__(site=True, **kwargs)

        # handle old -dry paramter
        self._handle_dry_param(**kwargs)

        # assign the generator to the bot
        self.generator = generator

    def _handle_dry_param(self, **kwargs):
        """
        Read the dry parameter and set the simulate variable instead.

        This is a private method. It prints a deprecation warning for old
        -dry paramter and sets the global simulate variable and informs
        the user about this setting.

        The constuctor of the super class ignores it because it is not
        part of self.availableOptions.

        @note: You should ommit this method in your own application.

        @keyword dry: deprecated option to prevent changes on live wiki.
            Use -simulate instead.
        @type dry: bool
        """
        if 'dry' in kwargs:
            issue_deprecation_warning('dry argument',
                                      'pywikibot.config.simulate', 1)
            # use simulate variable instead
            pywikibot.config.simulate = True
            pywikibot.output('config.simulate was set to True')

    def run(self):
        #prepare new page
        header = 'Na tej stronie znajdują się najbardziej potrzebne strony, do których linki pojawiają się na 100+ stronach.\n\n' 
	#header += u':<small>Pominięto strony z szablonem {{s|Inne znaczenia}}</small>\n\n'
	header += u"Ta strona jest okresowo uaktualniana przez [[Wikipedysta:MastiBot|MastiBota]]. Ostatnia aktualizacja przez bota: '''~~~~~'''. \n"
	header += u'Wszelkie uwagi proszę zgłaszać w [[Dyskusja_Wikipedysty:Masti|dyskusji operatora]].\n\n'
        footer = u'\n\n[[[[Kategoria:Najbardziej potrzebne strony]]'

        counter = 1
        refscounter = 0

        for page in self.generator:
            if self.getOption('progress'):
                pywikibot.output(u'%s #%i Treating:%s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), counter, page.title(asLink=True)) )
            refs = self.treat(page)
            if self.getOption('progress'):
                pywikibot.output('%s #%i refs found:%i' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), counter, refs))
            counter += 1

        result = self.generateresultspage(self.results,self.getOption('outpage'),header,footer)

        return

    def redirCount(self,article):
        #return number of linkined redirs
        return(article['count'])

    def generateresultspage(self, redirlist, pagename, header, footer):
        """
        Generates results page from redirlist
        Starting with header, ending with footer
        Output page is pagename
        """
        finalpage = header
        res = sorted(redirlist, key=redirlist.__getitem__, reverse=True)
        if self.getOption('test'):
            pywikibot.output('***** INPUT *****')
            pywikibot.output(redirlist)
            pywikibot.output('***** RESULT *****')
            pywikibot.output(res)
        linkcount = 0
        for i in res:
            count = self.redirCount(redirlist[i])
            l = redirlist[i]['list']
            if self.getOption('resprogress'):
                pywikibot.output('i:[[%s]], count:%i, l:%s' % (i,count,l))

            #if count < int(self.getOption('minlinks')):
            #      continue
            strcount = str(count)
            if count == 1:
                 suffix = u''
            elif strcount[len(strcount)-1] in (u'2',u'3',u'4') and (count>20 or count<10) :
                 suffix = u'i'
            else:
                 suffix = u'ów'
            finalpage += u'\n# [[%s]] ([[Specjalna:Linkujące/%s|%s link%s]])  &rarr; [[%s]]' % (i,i,str(count),suffix,']], [['.join(l))

        finalpage += footer

        if self.getOption('test'):
            pywikibot.output('***** FINALPAGE *****')
            pywikibot.output(finalpage)

        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        outpage.text = finalpage
        outpage.save(summary=self.getOption('summary'))

        #if self.getOption('test'):
        #    pywikibot.output(redirlist)
        return(res)
      
    def addResult(self,what,where):
        if not where in self.results.keys():
            self.results[where] = {'count':0,'list':[]}
        self.results[where]['count'] += 1
        self.results[where]['list'].append(what)
        return

    def treat(self, page):
        #get all linkedPages
        # check for disambigs
        linkR = re.compile(ur'\[\[(?P<title>.*?)(#(?P<section>.*?))?(\|(?P<label>.*?))?\]\]')
        counter = 0
        reqcounter = 0
        checkedpages = []
        for p in linkR.finditer(page.text):
            counter += 1
            t = p.group('title')
            if t in checkedpages:
                continue
            checkedpages.append(t)
            rp = pywikibot.Page(pywikibot.Site(),t)
            if not rp.namespace()==0:
                continue
            if self.getOption('testlinks'):
                pywikibot.output(u'%s #%i (%i) In %s checking:%s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), counter, reqcounter,page.title(asLink=True), rp.title(asLink=True)) )
            if not rp.exists():
                reqcounter += 1
                self.addResult(page.title(),rp.title())
        return(reqcounter)

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
        if option in ('summary', 'text', 'outpage', 'maxlines','minlinks'):
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
