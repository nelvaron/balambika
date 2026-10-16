import type { Locale } from '../i18n/ui';

export type ScriptId = 'devanagari' | 'latin' | 'cyrillic';

export const groupNames: Record<string, Record<Locale, string>> = {
  vowels: { en: 'Vowels', bg: 'Гласни' },
  consonants: { en: 'Consonants', bg: 'Съгласни' },
  signs: { en: 'Vowel signs and modifiers', bg: 'Гласни знаци и модификатори' },
  digits: { en: 'Digits', bg: 'Цифри' },
  punctuation: { en: 'Punctuation and symbols', bg: 'Пунктуация и символи' },
  vedic: { en: 'Vedic Extensions and Devanagari Extended', bg: 'Ведически разширения и разширено деванагари' },
  basic: { en: 'Basic Latin', bg: 'Основна латиница' },
  iast: { en: 'IAST letters', bg: 'Букви на IAST' },
  accented: { en: 'Accented Latin', bg: 'Латиница с диакритика' },
  figures: { en: 'Figures', bg: 'Цифри' },
  bulgarian: { en: 'Bulgarian alphabet', bg: 'Българска азбука' },
  extended: { en: 'Other Cyrillic', bg: 'Друга кирилица' },
  historic: { en: 'Historic letters', bg: 'Исторически букви' },
};

interface Specimen {
  lang: string;
  name: Record<Locale, string>;
  lede: Record<Locale, string>;
  hero: string;
  waterfall: string;
  styles: string;
  paragraphs: { lang: string; text: string }[];
  note?: Record<Locale, string>;
}

export const specimens: Record<ScriptId, Specimen> = {
  devanagari: {
    lang: 'sa',
    name: { en: 'Devanagari', bg: 'Деванагари' },
    lede: {
      en: 'Shobhika’s Devanagari, based on Yashomudra, with Vedic accents, thousands of conjunct ligatures and a word space that widens between Devanagari words only.',
      bg: 'Деванагари на Shobhika, основано на Yashomudra, с ведически ударения, хиляди лигатури за съчетания и интервал, който се разширява само между думи на деванагари.',
    },
    hero: 'क्ष्म्य ज्ञ श्री',
    waterfall: 'वागर्थाविव संपृक्तौ वागर्थप्रतिपत्तये',
    styles: 'श्रीमत्सिंहासनेश्वरी',
    note: {
      en: 'Devanagari has no italic tradition, so the italic styles carry the same upright Devanagari.',
      bg: 'Деванагари няма курсивна традиция, затова курсивните стилове съдържат същото право деванагари.',
    },
    paragraphs: [
      { lang: 'sa', text: 'अस्ति भागीरथीतीरे पाटलिपुत्रनामधेयं नगरम् । तत्र सर्वस्वामिगुणोपेतः सुदर्शनो नाम नरपतिरासीत् ।' },
      { lang: 'sa', text: 'कुर्वन्नेवेह कर्माणि जिजीविषेच्छतं समाः । एवं त्वयि नान्यथेतोऽस्ति न कर्म लिप्यते नरे ॥' },
      { lang: 'sa', text: 'अ॒ग्निः पूर्वे॑भि॒र्ऋषि॑भि॒रीड्यो॒ नूत॑नैरु॒त । स दे॒वाँ एह व॑क्षति ॥' },
    ],
  },
  latin: {
    lang: 'en',
    name: { en: 'Latin', bg: 'Латиница' },
    lede: {
      en: 'Common Serif, scaled to 108 per cent so its capitals meet the Devanagari headline, with every IAST letter precomposed and kerned.',
      bg: 'Common Serif, увеличен до 108 %, за да се изравнят главните букви с горната линия на деванагари, с всички букви на IAST като готови знаци и с кернинг.',
    },
    hero: 'Ā ṛ ṣ',
    waterfall: 'vāgarthāv iva saṃpṛktau vāgarthapratipattaye',
    styles: 'Śrīmatsiṃhāsaneśvarī',
    paragraphs: [
      { lang: 'en', text: 'Balambika is a compilation of two typefaces released under the SIL Open Font License. Its Devanagari comes from Shobhika, made at IIT Bombay on the basis of Yashomudra; its Latin, IAST and Cyrillic come from Common Serif, derived from Libertinus Serif. The Latin is scaled so that its cap height meets the Devanagari headline, and the bold pairs Common Serif SemiBold with Shobhika Bold, so both scripts carry the same colour on the page.' },
      { lang: 'sa-Latn', text: 'asti bhāgīrathītīre pāṭaliputranāmadheyaṃ nagaram | tatra sarvasvāmiguṇopetaḥ sudarśano nāma narapatir āsīt |' },
      { lang: 'en', text: 'On the bank of the Bhāgīrathī there is a city called Pāṭaliputra. A king named Sudarśana once ruled there, endowed with every quality of a sovereign.' },
    ],
  },
  cyrillic: {
    lang: 'bg',
    name: { en: 'Cyrillic', bg: 'Кирилица' },
    lede: {
      en: 'Bulgarian Cyrillic is the default: the Bulgarian letterforms are mapped directly, so they appear in Word and Pages without any language tagging.',
      bg: 'Българската кирилица е по подразбиране: българските форми на буквите са зададени директно, затова се появяват в Word и Pages без задаване на език.',
    },
    hero: 'Жд лъв',
    waterfall: 'Слово и смисъл, съединени в едно',
    styles: 'Шрифт за санскритски издания',
    paragraphs: [
      { lang: 'bg', text: 'Balambika съчетава два шрифта, издадени под SIL Open Font License. Деванагари идва от Shobhika, създаден в IIT Bombay въз основа на Yashomudra; латиницата, IAST и кирилицата идват от Common Serif, производен на Libertinus Serif. Латиницата е увеличена така, че височината на главните букви да съвпада с горната линия на деванагари, а получерният стил съчетава Common Serif SemiBold с Shobhika Bold, за да имат двете писмености еднаква плътност на страницата.' },
      { lang: 'bg', text: 'На брега на Бхагиратхи има град на име Паталипутра. Там някога царувал владетел на име Сударшана, надарен с всички качества на господар.' },
      { lang: 'bg', text: 'Жълтата дюля беше щастлива, че пухът, който цъфна, замръзна като гьон.' },
    ],
  },
};

/** Devanagari ↔ IAST correspondence for the Latin specimen. */
export const iastTable: [string, string][] = [
  ['अ', 'a'], ['आ', 'ā'], ['इ', 'i'], ['ई', 'ī'], ['उ', 'u'], ['ऊ', 'ū'], ['ऋ', 'ṛ'], ['ॠ', 'ṝ'],
  ['ऌ', 'ḷ'], ['ॡ', 'ḹ'], ['ए', 'e'], ['ऐ', 'ai'], ['ओ', 'o'], ['औ', 'au'], ['अं', 'aṃ'], ['अः', 'aḥ'],
  ['क', 'ka'], ['ख', 'kha'], ['ग', 'ga'], ['घ', 'gha'], ['ङ', 'ṅa'],
  ['च', 'ca'], ['छ', 'cha'], ['ज', 'ja'], ['झ', 'jha'], ['ञ', 'ña'],
  ['ट', 'ṭa'], ['ठ', 'ṭha'], ['ड', 'ḍa'], ['ढ', 'ḍha'], ['ण', 'ṇa'],
  ['त', 'ta'], ['थ', 'tha'], ['द', 'da'], ['ध', 'dha'], ['न', 'na'],
  ['प', 'pa'], ['फ', 'pha'], ['ब', 'ba'], ['भ', 'bha'], ['म', 'ma'],
  ['य', 'ya'], ['र', 'ra'], ['ल', 'la'], ['व', 'va'],
  ['श', 'śa'], ['ष', 'ṣa'], ['स', 'sa'], ['ह', 'ha'], ['ळ', 'ḷa'], ['ऽ', 'ʼ'],
];

export const bulgarianForms = 'в г д ж з и й к л п т ц ш щ ъ ю';
