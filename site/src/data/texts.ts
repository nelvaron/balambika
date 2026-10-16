/**
 * Source passages shown on the site. Devanagari and IAST follow standard
 * editions; English and Bulgarian translations are the project's own.
 * IAST uses U+02BC (modifier letter apostrophe) for avagraha.
 */
export interface Passage {
  id: string;
  source: { en: string; bg: string };
  kind: { en: string; bg: string };
  deva: string;
  iast: string;
  en: string;
  bg: string;
}

export const passages: Passage[] = [
  {
    id: 'rv-1-1-1',
    source: { en: 'Ṛgveda 1.1.1', bg: 'Ригведа 1.1.1' },
    kind: { en: 'Vedic, with accents', bg: 'Ведически, с ударения' },
    deva: 'अ॒ग्निमी॑ळे पु॒रोहि॑तं य॒ज्ञस्य॑ दे॒वमृ॒त्विज॑म् ।\nहोता॑रं रत्न॒धात॑मम् ॥',
    iast: 'agním īḷe puróhitaṃ yajñásya devám ṛtvíjam |\nhótāraṃ ratnadhā́tamam ||',
    en: 'I praise Agni, the household priest, god of the sacrifice, its minister, the invoker, the greatest giver of treasure.',
    bg: 'Възпявам Агни, домашния жрец, бога на жертвоприношението, неговия служител, призоваващия, най-щедрия даряващ съкровища.',
  },
  {
    id: 'isha-1',
    source: { en: 'Īśopaniṣad 1', bg: 'Ишопанишад 1' },
    kind: { en: 'Upaniṣad', bg: 'Упанишад' },
    deva: 'ईशा वास्यमिदं सर्वं यत्किञ्च जगत्यां जगत् ।\nतेन त्यक्तेन भुञ्जीथा मा गृधः कस्यस्विद्धनम् ॥',
    iast: 'īśā vāsyam idaṃ sarvaṃ yat kiñca jagatyāṃ jagat |\ntena tyaktena bhuñjīthā mā gṛdhaḥ kasya svid dhanam ||',
    en: 'All this, whatever moves in this moving world, is to be pervaded by the Lord. Find your joy through letting go; do not covet. Whose, after all, is wealth?',
    bg: 'Всичко това, което се движи в движещия се свят, е проникнато от Господа. Намери радостта си в отказа; не пожелавай. Чие всъщност е богатството?',
  },
  {
    id: 'gita-2-47',
    source: { en: 'Bhagavadgītā 2.47', bg: 'Бхагавадгита 2.47' },
    kind: { en: 'Epic', bg: 'Епос' },
    deva: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन ।\nमा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि ॥',
    iast: 'karmaṇy evādhikāras te mā phaleṣu kadācana |\nmā karmaphalahetur bhūr mā te saṅgo ʼstv akarmaṇi ||',
    en: 'Your right is to the action alone, never to its fruits. Let the fruit of action not be your motive, and let you not cling to inaction.',
    bg: 'Твое право е само действието, никога плодовете му. Нека плодът на действието не бъде твой подтик и не се привързвай към бездействието.',
  },
  {
    id: 'lalita-1-2',
    source: { en: 'Lalitāsahasranāma 1–2', bg: 'Лалитасахасранама 1–2' },
    kind: { en: 'Purāṇic, Brahmāṇḍapurāṇa', bg: 'Пуранически, Брахманда пурана' },
    deva: 'श्रीमाता श्रीमहाराज्ञी श्रीमत्सिंहासनेश्वरी ।\nचिदग्निकुण्डसम्भूता देवकार्यसमुद्यता ॥',
    iast: 'śrīmātā śrīmahārājñī śrīmatsiṃhāsaneśvarī |\ncidagnikuṇḍasambhūtā devakāryasamudyatā ||',
    en: 'The auspicious Mother, the great Queen, sovereign of the splendid lion throne; born from the fire altar of consciousness, risen for the work of the gods.',
    bg: 'Благата Майка, великата Царица, владетелка на славния лъвски трон; родена от огнището на съзнанието, въздигнала се за делото на боговете.',
  },
  {
    id: 'raghu-1-1',
    source: { en: 'Raghuvaṃśa 1.1', bg: 'Рагхувамша 1.1' },
    kind: { en: 'Classical poetry, Kālidāsa', bg: 'Класическа поезия, Калидаса' },
    deva: 'वागर्थाविव संपृक्तौ वागर्थप्रतिपत्तये ।\nजगतः पितरौ वन्दे पार्वतीपरमेश्वरौ ॥',
    iast: 'vāgarthāv iva saṃpṛktau vāgarthapratipattaye |\njagataḥ pitarau vande pārvatīparameśvarau ||',
    en: 'For the true grasp of word and meaning, I bow to the parents of the world, Pārvatī and Parameśvara, joined as word and meaning are joined.',
    bg: 'За вярното постигане на словото и смисъла се покланям на родителите на света, Парвати и Парамешвара, съединени както са съединени слово и смисъл.',
  },
];

export const gayatri = {
  accented: 'तत्स॑वि॒तुर्वरे॑ण्यं॒ भर्गो॑ दे॒वस्य॑ धीमहि ।\nधियो॒ यो नः॑ प्रचो॒दया॑त् ॥',
  plain: 'तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि ।\nधियो यो नः प्रचोदयात् ॥',
  iast: 'tát savitúr váreṇyaṃ bhárgo devásya dhīmahi |\ndhíyo yó naḥ pracodáyāt ||',
  en: 'We meditate on that excellent radiance of the god Savitṛ; may he stir our thoughts.',
  bg: 'Съзерцаваме онова превъзходно сияние на бог Савитр; нека той събуди нашите мисли.',
};

export const verse = passages.find((p) => p.id === 'raghu-1-1')!;
