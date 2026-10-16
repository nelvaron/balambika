export const locales = ['en', 'bg'] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = 'en';

export const localeNames: Record<Locale, string> = { en: 'English', bg: 'Български' };
export const ogLocales: Record<Locale, string> = { en: 'en_US', bg: 'bg_BG' };

const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

/** Absolute path (with base) of a page in a locale. `page` has no leading slash. */
export function localePath(locale: Locale, page = ''): string {
  const prefix = locale === defaultLocale ? '' : `/${locale}`;
  const clean = page.replace(/^\/+/, '');
  return `${BASE}${prefix}/${clean}`;
}

/** Path of a static asset in public/. */
export function asset(file: string): string {
  return `${BASE}/${file.replace(/^\/+/, '')}`;
}

export function getStaticLocalePaths() {
  return locales.map((locale) => ({
    params: { locale: locale === defaultLocale ? undefined : locale },
    props: { locale },
  }));
}

export const REPO = 'https://github.com/nelvaron/balambika';
export const RELEASES = `${REPO}/releases/latest`;
export const RAW = `${REPO}/raw/main/fonts/ttf`;

export const ui = {
  en: {
    'site.name': 'Balambika',
    'site.tagline': 'One font for Sanskrit publishing, in Devanagari, IAST and Bulgarian Cyrillic',
    'skip': 'Skip to main content',
    'nav.label': 'Main',
    'nav.home': 'Overview',
    'nav.specimens': 'Specimens',
    'nav.devanagari': 'Devanagari',
    'nav.latin': 'Latin',
    'nav.cyrillic': 'Cyrillic',
    'nav.usage': 'Usage',
    'nav.source': 'Source on GitHub',
    'theme.label': 'Theme',
    'theme.auto': 'Auto',
    'theme.light': 'Light',
    'theme.dark': 'Dark',
    'lang.label': 'Language',
    'footer.license': 'SIL Open Font License 1.1',
    'footer.privacy': 'Privacy',
    'footer.credits': 'Devanagari from Shobhika (IIT Bombay). Latin and Cyrillic from Common Serif (The Common Serif Project Authors).',
    'footer.made': 'Site and font by nelvaron',

    'home.title': 'Balambika — a font for Sanskrit in three scripts',
    'home.description': 'Balambika sets Vedic and Purāṇic texts in Devanagari, with IAST transliteration and Bulgarian or English translation, in one font that behaves the same in Pages, Word and XeLaTeX.',
    'hero.eyebrow': 'Open font · SIL OFL 1.1',
    'hero.title': 'One font for Sanskrit, in three scripts.',
    'hero.lede': 'Vedic and Purāṇic texts in Devanagari, with IAST transliteration and English or Bulgarian translation, set from one file that works the same in Pages, Word and XeLaTeX.',
    'hero.download': 'Download the fonts',
    'hero.try': 'Try it with your text',
    'hero.facts': 'Six styles · {glyphs} glyphs · {cps} code points',
    'globe.label': 'A slowly turning globe of letters from the three scripts. Arcs connect letters that transliterate one another, such as क, k and к.',
    'globe.pause': 'Pause animation',
    'globe.play': 'Play animation',
    'globe.legend': 'Letters on the globe',

    'verse.eyebrow': 'Raghuvaṃśa 1.1 · Kālidāsa',
    'verse.title': 'Word and meaning, joined.',
    'verse.lede': 'A multilingual edition prints the same verse four ways. In Balambika, every line comes from one family with matched heights and weights.',
    'row.deva': 'Devanagari',
    'row.iast': 'IAST',
    'row.en': 'English',
    'row.bg': 'Bulgarian',

    'conj.eyebrow': 'Conjuncts',
    'conj.title': 'Seven code points, one glyph.',
    'conj.lede': 'Shobhika’s Devanagari draws thousands of conjuncts as single ligatures. Pick one to see what it is made of, then step through the shaping stages.',
    'conj.stages': 'Shaping, step by step',
    'conj.stage0': 'Code points',
    'conj.stage1': 'Half forms',
    'conj.stage2': 'Akhand ligatures',
    'conj.stage3': 'Conjunct ligatures',
    'conj.glyphs': 'glyphs',
    'conj.codepoints': 'code points',
    'conj.example': 'In a word',
    'conj.made': 'Made of',
    'conj.stress': 'Stress test',
    'conj.stress.note': 'Rare clusters that still resolve to one or two glyphs.',
    'conj.stage.note': 'Stages use font-feature-settings and need a HarfBuzz browser: Chrome, Edge or Firefox.',
    'conj.close': 'Close',

    'vedic.eyebrow': 'Vedic accents',
    'vedic.title': 'Accents that never collide.',
    'vedic.lede': 'Ṛgveda marks the low and falling tones with strokes below and above the akṣara. Vertical metrics are tall enough that stacked marks are never clipped.',
    'vedic.source': 'Ṛgveda 3.62.10, the Gāyatrī',
    'vedic.toggle': 'Show accents',
    'vedic.table': 'Vedic marks used on this page',
    'vedic.mark': 'Mark',
    'vedic.code': 'Code point',
    'vedic.name': 'Name',
    'vedic.role': 'Role',
    'vedic.anudatta': 'Low tone, written below the syllable before an udātta.',
    'vedic.svarita': 'Falling tone, written above the syllable after an udātta.',
    'vedic.udatta': 'High tone, left unmarked in the Ṛgveda convention.',
    'vedic.double': 'Double svarita, used in some recensions.',
    'vedic.cbv': 'Anusvāra variant used in Yajurveda texts.',

    'tester.eyebrow': 'Type tester',
    'tester.title': 'Set your own text.',
    'tester.lede': 'Type or paste anything. Nothing you enter leaves your browser.',
    'tester.text': 'Sample text',
    'tester.preset': 'Sample',
    'tester.size': 'Size',
    'tester.leading': 'Line height',
    'tester.weight': 'Weight',
    'tester.italic': 'Italic',
    'tester.w400': 'Regular',
    'tester.w500': 'Medium',
    'tester.w700': 'Bold',
    'tester.reset': 'Reset',

    'texts.eyebrow': 'Sources',
    'texts.title': 'From the Veda to the Purāṇas.',
    'texts.lede': 'Each passage in Devanagari, IAST, English and Bulgarian. Translations are our own, kept close to the Sanskrit.',
    'texts.prev': 'Previous passage',
    'texts.next': 'Next passage',

    'spec.eyebrow': 'Specimens',
    'spec.title': 'One family, three alphabets.',
    'spec.lede': 'A full specimen for each script: character set, sizes, weights and running text.',
    'spec.open': 'Open the {name} specimen',

    'dl.eyebrow': 'Download',
    'dl.title': 'Six styles, free to use.',
    'dl.lede': 'Regular, Italic, Medium, Medium Italic, Bold and Bold Italic, as TrueType. Use, embed and redistribute them freely, including in commercial books.',
    'dl.release': 'All fonts from the latest release',
    'dl.file': 'Download {style} (TTF)',
    'dl.install': 'Installing and setting up Pages, Word and XeLaTeX',

    'specimen.charset': 'Character set',
    'specimen.waterfall': 'Sizes',
    'specimen.styles': 'Styles',
    'specimen.text': 'Running text',
    'specimen.count': '{n} characters',
    'specimen.back': 'All specimens',

    'usage.title': 'Usage',
    'usage.description': 'How to install Balambika and set it up in Pages, Word and XeLaTeX, with notes on line spacing, hyphenation and Devanagari word spacing.',

    'privacy.title': 'Privacy',
    'privacy.description': 'This site sets no cookies, runs no analytics and sends what you type in the tester nowhere.',

    '404.title': 'Page not found',
    '404.text': 'There is no page at this address. It may have moved.',
    '404.home': 'Go to the overview',
  },
  bg: {
    'site.name': 'Balambika',
    'site.tagline': 'Един шрифт за санскритски издания, на деванагари, IAST и българска кирилица',
    'skip': 'Към основното съдържание',
    'nav.label': 'Основна навигация',
    'nav.home': 'Общ преглед',
    'nav.specimens': 'Спесимени',
    'nav.devanagari': 'Деванагари',
    'nav.latin': 'Латиница',
    'nav.cyrillic': 'Кирилица',
    'nav.usage': 'Употреба',
    'nav.source': 'Изходен код в GitHub',
    'theme.label': 'Тема',
    'theme.auto': 'Авто',
    'theme.light': 'Светла',
    'theme.dark': 'Тъмна',
    'lang.label': 'Език',
    'footer.license': 'SIL Open Font License 1.1',
    'footer.privacy': 'Поверителност',
    'footer.credits': 'Деванагари от Shobhika (IIT Bombay). Латиница и кирилица от Common Serif (The Common Serif Project Authors).',
    'footer.made': 'Сайт и шрифт: nelvaron',

    'home.title': 'Balambika — шрифт за санскрит в три писмености',
    'home.description': 'Balambika набира ведически и пуранически текстове на деванагари, с транслитерация в IAST и превод на български или английски, в един шрифт, който работи еднакво в Pages, Word и XeLaTeX.',
    'hero.eyebrow': 'Свободен шрифт · SIL OFL 1.1',
    'hero.title': 'Един шрифт за санскрит, в три писмености.',
    'hero.lede': 'Ведически и пуранически текстове на деванагари, с транслитерация в IAST и превод на български или английски, набрани от един файл, който работи еднакво в Pages, Word и XeLaTeX.',
    'hero.download': 'Изтегли шрифта',
    'hero.try': 'Изпробвай с твой текст',
    'hero.facts': 'Шест стила · {glyphs} глифа · {cps} кодови точки',
    'globe.label': 'Бавно въртящо се кълбо от букви на трите писмености. Дъги свързват букви, които се транслитерират една в друга, например क, k и к.',
    'globe.pause': 'Спри анимацията',
    'globe.play': 'Пусни анимацията',
    'globe.legend': 'Букви върху кълбото',

    'verse.eyebrow': 'Рагхувамша 1.1 · Калидаса',
    'verse.title': 'Слово и смисъл, съединени.',
    'verse.lede': 'Многоезичното издание печата един и същ стих по четири начина. С Balambika всеки ред идва от едно семейство със съгласувани височини и дебелини.',
    'row.deva': 'Деванагари',
    'row.iast': 'IAST',
    'row.en': 'Английски',
    'row.bg': 'Български',

    'conj.eyebrow': 'Съчетания',
    'conj.title': 'Седем кодови точки, един глиф.',
    'conj.lede': 'Деванагари на Shobhika изписва хиляди съгласни съчетания като единни лигатури. Изберете едно, за да видите от какво се състои, и минете през етапите на оформянето.',
    'conj.stages': 'Оформяне стъпка по стъпка',
    'conj.stage0': 'Кодови точки',
    'conj.stage1': 'Полуформи',
    'conj.stage2': 'Лигатури akhn',
    'conj.stage3': 'Пълни лигатури',
    'conj.glyphs': 'глифа',
    'conj.codepoints': 'кодови точки',
    'conj.example': 'В дума',
    'conj.made': 'Състав',
    'conj.stress': 'Изпитание',
    'conj.stress.note': 'Редки съчетания, които пак се свеждат до един или два глифа.',
    'conj.stage.note': 'Етапите използват font-feature-settings и изискват браузър с HarfBuzz: Chrome, Edge или Firefox.',
    'conj.close': 'Затвори',

    'vedic.eyebrow': 'Ведически ударения',
    'vedic.title': 'Ударения, които не се сблъскват.',
    'vedic.lede': 'Ригведа отбелязва ниския и падащия тон с черти под и над акшарата. Вертикалните метрики са достатъчно високи, за да не се изрязват натрупаните знаци.',
    'vedic.source': 'Ригведа 3.62.10, Гаятри',
    'vedic.toggle': 'Покажи ударенията',
    'vedic.table': 'Ведически знаци, използвани на тази страница',
    'vedic.mark': 'Знак',
    'vedic.code': 'Кодова точка',
    'vedic.name': 'Име',
    'vedic.role': 'Роля',
    'vedic.anudatta': 'Нисък тон, пише се под сричката преди удатта.',
    'vedic.svarita': 'Падащ тон, пише се над сричката след удатта.',
    'vedic.udatta': 'Висок тон, по традицията на Ригведа не се отбелязва.',
    'vedic.double': 'Двойна сварита, в някои рецензии.',
    'vedic.cbv': 'Вариант на анусвара в текстовете на Яджурведа.',

    'tester.eyebrow': 'Изпробване',
    'tester.title': 'Наберете свой текст.',
    'tester.lede': 'Пишете или поставете какъвто и да е текст. Нищо от въведеното не напуска браузъра ви.',
    'tester.text': 'Примерен текст',
    'tester.preset': 'Образец',
    'tester.size': 'Размер',
    'tester.leading': 'Междуредие',
    'tester.weight': 'Дебелина',
    'tester.italic': 'Курсив',
    'tester.w400': 'Нормален',
    'tester.w500': 'Среден',
    'tester.w700': 'Получер',
    'tester.reset': 'Възстанови',

    'texts.eyebrow': 'Източници',
    'texts.title': 'От Ведите до Пураните.',
    'texts.lede': 'Всеки откъс на деванагари, IAST, английски и български. Преводите са наши, близки до санскритския оригинал.',
    'texts.prev': 'Предишен откъс',
    'texts.next': 'Следващ откъс',

    'spec.eyebrow': 'Спесимени',
    'spec.title': 'Едно семейство, три азбуки.',
    'spec.lede': 'Пълен спесимен за всяка писменост: набор от знаци, размери, стилове и текст.',
    'spec.open': 'Отвори спесимена за {name}',

    'dl.eyebrow': 'Изтегляне',
    'dl.title': 'Шест стила, свободни за употреба.',
    'dl.lede': 'Нормален, курсив, среден, среден курсив, получер и получер курсив, във формат TrueType. Използвайте, вграждайте и разпространявайте ги свободно, включително в търговски издания.',
    'dl.release': 'Всички шрифтове от последното издание',
    'dl.file': 'Изтегли {style} (TTF)',
    'dl.install': 'Инсталиране и настройка за Pages, Word и XeLaTeX',

    'specimen.charset': 'Набор от знаци',
    'specimen.waterfall': 'Размери',
    'specimen.styles': 'Стилове',
    'specimen.text': 'Текст',
    'specimen.count': '{n} знака',
    'specimen.back': 'Всички спесимени',

    'usage.title': 'Употреба',
    'usage.description': 'Как да инсталирате Balambika и да я настроите в Pages, Word и XeLaTeX, с бележки за междуредието, пренасянето и разстоянието между думите на деванагари.',

    'privacy.title': 'Поверителност',
    'privacy.description': 'Сайтът не поставя бисквитки, не събира статистика и не изпраща никъде текста, който въвеждате.',

    '404.title': 'Страницата не е намерена',
    '404.text': 'На този адрес няма страница. Възможно е да е преместена.',
    '404.home': 'Към общия преглед',
  },
} as const;

export type UiKey = keyof (typeof ui)['en'];

export function useTranslations(locale: Locale) {
  return (key: UiKey, vars: Record<string, string | number> = {}) => {
    let s: string = ui[locale][key] ?? ui.en[key];
    for (const [k, v] of Object.entries(vars)) s = s.replace(`{${k}}`, String(v));
    return s;
  };
}

export function formatNumber(locale: Locale, n: number) {
  return new Intl.NumberFormat(locale === 'bg' ? 'bg-BG' : 'en-US').format(n);
}

const units = {
  glyph: { en: { one: 'glyph', other: 'glyphs' }, bg: { one: 'глиф', other: 'глифа' } },
  codepoint: { en: { one: 'code point', other: 'code points' }, bg: { one: 'кодова точка', other: 'кодови точки' } },
} as const;

/** "1 glyph", "7 code points": CLDR plural categories via Intl.PluralRules. */
export function countOf(locale: Locale, n: number, unit: keyof typeof units) {
  const cat = new Intl.PluralRules(locale).select(n) === 'one' ? 'one' : 'other';
  return units[unit][locale][cat];
}
