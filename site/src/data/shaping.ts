/**
 * OpenType feature sets for the "Shaping, step by step" control. They must
 * match STAGES in scripts/shape-data.py, which counts glyphs per stage.
 */
const LIGATURES = ['akhn', 'pres', 'cjct', 'abvs', 'blws', 'psts'];
const FORMS = ['half', 'haln', 'rphf', 'rkrf', 'pref', 'blwf', 'vatu', 'pstf', 'cfar'];

const off = (list: string[]) => list.map((f) => `"${f}" 0`).join(', ');

export const STAGE_FEATURES = [
  off([...LIGATURES, ...FORMS]),
  off(LIGATURES),
  off(LIGATURES.filter((f) => f !== 'akhn')),
  'normal',
];
