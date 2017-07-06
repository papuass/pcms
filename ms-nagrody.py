#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Lista artykułów z uzupełnionym parametrem "Nagrody" bez sekcji "Nagrody", "Nominacje" lub "Nagrody i nominacje" w artykule. Dotyczycy artykułów w których występuje infobox Szablon:Film infobox.
Call:
python pwb.py masti/ms-nagrody.py -transcludes:"Film infobox" -ns:0 -outpage:"Wikipedysta:mastiBot/Film infobox" -summary:"Bot uaktualnia stronę"

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

-test:            Switch on test prinouts
"""
#
# (C) Pywikibot team, 2006-2016
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, unicode_literals

__version__ = '$Id: m-artdisamblist.py masti $'
#

import pywikibot
from pywikibot import pagegenerators

from pywikibot.bot import (
    SingleSiteBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)
from pywikibot.tools import issue_deprecation_warning

import re

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
            'test': False, #switch on test functionality 
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
        #prepare new page with table
        header = u"Ta strona jest okresowo uaktualniana przez [[Wikipedysta:MastiBot|bota]]. Ostatnia aktualizacja ~~~~~. \nWszelkie uwagi proszę zgłaszać w [[Dyskusja_Wikipedysty:Masti|dyskusji operatora]]."
	header += u"\n<small>"
	header += u"\n*Legenda:"
	header += u"\n*:'''Hasło''' - Tytuł hasła"
	header += u"\n*:'''Nagrody''' - zawartość pola nagrody"
	header += u"\n</small>\n"
	header += u'{| class="wikitable" style="font-size:85%;"\n|-\n!Lp.\n!Hasło\n!Nagrody'

        results = {}

        finalpage = header
        counter = 0
        marked = 0
        for page in self.generator:
            counter += 1
            #finalpage = finalpage + self.treat(page)
            pywikibot.output(u'Processing page #%i (%i marked): %s' % (counter, marked, page.title(asLink=True)) )
            result = self.treat(page)
            if result:
               results[page.title(withNamespace=False)] = result
               marked += 1
               pywikibot.output(u'Added line #%i: %s' % ( marked, page.title(asLink=True) ))

        footer = u'\n|}\n\n'
        footer += u'Przetworzono stron:' + str(counter)

        if self.getOption('test'):
            pywikibot.output(results)
        self.generateresultspage(results, self.getOption('outpage'), header, footer)
        return

    def treat(self, page):
        """
        Loads the given page, looks for sections:
            "Nagrody", "Nominacje" lub "Nagrody i nominacje"
        look for Film infobox with nonempty param: Nagrody
        returns nagrody content
        """
        found = False
        mark = False
        result = None
 
        text = page.text
        #if self.getOption('test'):
        #    pywikibot.output(text)
        if not text or page.isDisambig():
            return(None)

        awardR = re.compile(ur'=+\s*?(nagrody|nominacje|nagrody i nominacje)\s*?=+',re.I)
        award = awardR.search(text)
        if award:
            found = True
            if self.getOption('test'):
                pywikibot.output(u'wynik:%s' % award.group(0))
        else:
            if self.getOption('test'):
                pywikibot.output(u'wynik: BRAK')
            return(None)

        #look for film infobox
        for t in page.templatesWithParams():
            tt, arglist = t
            if self.getOption('test'):
                pywikibot.output(u'Template:%s' % tt.title())
            if  u'Szablon:Film infobox' in tt.title():
                for a in arglist:
                    if self.getOption('test'):
                        pywikibot.output(u'Arg:%s' % a)
                    named, name, value = self.templateArg(a)
                    if self.getOption('test'):
                        pywikibot.output(u'name:%s; value:%s' % (name,value))
                    if u'nagrody' in name and len(value)>0:
                        mark = True
                        result = value
                        return (result)

	#return None as no filled field found
        return(None)

    def generateresultspage(self, redirlist, pagename, header, footer):
        """
        Generates results page from redirlist
        Starting with header, ending with footer
        Output page is pagename
        """
        finalpage = header
        lineN = 1
        for i in list(redirlist):
            r, t = redirlist[i]
            if t: #marked page is Template
                finalpage += u'\n|-\n| ' + str(lineN) + u' || {{s|' + i + u'}} || '
            else: #marked page is article
                finalpage += u'\n|-\n| ' + str(lineN) + u' || [[' + i + u']] || '
            lineN += 1
            firstLine = True
            for d in r:
                if firstLine:
                    firstLine = False
                    finalpage += u'[[' + d + u']]'
                else:
                    finalpage += u'<br />[[' + d + u']]'

        finalpage += footer

        outpage = pywikibot.Page(pywikibot.Site(), pagename)
        outpage.text = finalpage
        outpage.save(summary=self.getOption('summary'))
        
        if self.getOption('test'):
            pywikibot.output(finalpage)
        return(redirlist)

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
