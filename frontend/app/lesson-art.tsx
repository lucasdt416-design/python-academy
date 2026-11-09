// Generated from docs/design/prototype/index.html (its <symbol> elements), then kept by hand.
// How the pictures are drawn, so new ones match: docs/design/art-style.md.
import type {ReactNode} from 'react';

/** Lesson id → picture id and its description (the picture's accessible name). */
export const LESSON_ART: Record<string, {art: string; label: string}> = {
 "hello": {art: "art-hello", label: "An open book that reads print(\"Hi!\"), under a speech bubble saying Hi!"},
 "variables": {art: "art-variables", label: "A hero pointing at two labelled boxes, hero and tool"},
 "input": {art: "art-input", label: "A speech bubble asking name?, above a box where the player types a reply"},
 "choices": {art: "art-choices", label: "A signpost where the path splits, one sign saying if and the other else"},
 "adventure": {art: "art-adventure", label: "A castle on a hill, with a flag and a path leading up to it"},
 "py.arithmetic": {art: "art-arithmetic", label: "Five pouches with three coins each and two coins left over in a chest"},
 "py.int-float": {art: "art-int-float", label: "A ruler from 3 to 5 with a marker at 4.5, between the labels int and float"},
 "py.convert-input": {art: "art-convert", label: "The text \"7\" going through an int() funnel and coming out as the number 7"},
 "py.compare": {art: "art-compare", label: "A balance weighing the secret against the guess"},
 "py.boolean-logic": {art: "art-logic", label: "Two switches, A and B, joined on their way to a door, beside the words and, or and not"},
 "py.elif": {art: "art-elif", label: "A score of 5 checked against if, elif, elif and else, one after another"},
 "py.while-loops": {art: "art-while", label: "A looping path around a question mark, ending at a door"},
 "py.loop-termination": {art: "art-three-tries", label: "Three candles: two tries crossed out and the third still lit"},
 "py.for-range": {art: "art-for-range", label: "A hero hopping up a staircase numbered 0, 2, 4, 6 and 8"},
 "py.accumulate": {art: "art-accumulate", label: "Bars adding 4, 6 and 5 into a total of 15"},
 "py.nested-loops": {art: "art-nested", label: "A grid of rooms with a path through them, row by row"},
};

const PICTURES: Record<string, ReactNode> = {
 "art-hello": <>
   <rect className="bg1" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 140Q80 118 160 134T320 126V180H0Z"/>
   <path className="f-moss" d="M0 160Q90 142 170 156T320 148V180H0Z"/>
   <path className="f-white s-ink" d="M62 78Q110 62 158 80V138Q110 122 62 138Z"/>
   <path className="f-cream s-ink" d="M162 80Q210 62 258 78V138Q210 122 162 138Z"/>
   <path className="s-ink" d="M160 80V138"/>
   <path className="s-moss" d="M78 96h60M78 108h48M78 120h56"/>
   <text className="mono f-ink" x="178" y="100" fontSize="13">print(</text>
   <text className="mono f-clay" x="178" y="118" fontSize="13">"Hi!")</text>
   <path className="f-white s-ink" d="M112 20h96a12 12 0 0 1 12 12v22a12 12 0 0 1-12 12h-46l-14 14v-14h-36a12 12 0 0 1-12-12V32a12 12 0 0 1 12-12z"/>
   <text className="mono f-moss" x="128" y="48" fontSize="18" fontWeight="700">Hi!</text>
   <path className="f-amber" d="M270 30l4 10 10 4-10 4-4 10-4-10-10-4 10-4z"/>
   <path className="f-amber" d="M44 52l3 7 7 3-7 3-3 7-3-7-7-3 7-3z"/>
 </>,
 "art-variables": <>
   <rect className="bg1" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 146Q90 126 170 142T320 134V180H0Z"/>
   <rect className="f-cream s-ink" x="168" y="96" width="62" height="50" rx="6"/>
   <path className="s-ink" d="M168 112h62"/>
   <rect className="f-white s-ink" x="180" y="78" width="38" height="18" rx="4"/>
   <text className="mono f-ink" x="185" y="91" fontSize="12">hero</text>
   <rect className="f-cream s-ink" x="244" y="106" width="52" height="40" rx="6"/>
   <path className="s-ink" d="M244 120h52"/>
   <rect className="f-white s-ink" x="252" y="90" width="36" height="16" rx="4"/>
   <text className="mono f-ink" x="257" y="102" fontSize="11">tool</text>
   <path className="f-amber-l s-ink" d="M262 128l6-14 6 14z"/>
   <circle className="f-amber-l s-ink" cx="108" cy="62" r="18"/>
   <path className="f-plum s-ink" d="M84 140q0-46 24-46t24 46z"/>
   <path className="s-ink" d="M170 72q-26 4-42 24"/>
   <path className="f-ink" d="M126 90l-4 10 12-4z"/>
   <text className="mono f-moss" x="18" y="28" fontSize="13" fontWeight="700">hero = "Kai"</text>
 </>,
 "art-input": <>
   <rect className="bg1" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 146Q90 126 170 142T320 134V180H0Z"/>
   <path className="f-slate s-ink" d="M200 150V62q0-34 40-34t40 34v88z"/>
   <path className="f-ink" d="M214 150V66q0-22 26-22t26 22v84z"/>
   <circle className="f-amber" cx="258" cy="100" r="4"/>
   <circle className="f-cream s-ink" cx="96" cy="84" r="17"/>
   <path className="f-plum s-ink" d="M72 150q0-46 24-46t24 46z"/>
   <path className="f-white s-ink" d="M118 38h76a10 10 0 0 1 10 10v22a10 10 0 0 1-10 10h-50l-14 12v-12h-12a10 10 0 0 1-10-10V48a10 10 0 0 1 10-10z"/>
   <text className="mono f-ink" x="132" y="63" fontSize="13">name?</text>
   <rect className="f-white s-moss" x="116" y="112" width="68" height="22" rx="5"/>
   <path className="s-moss" d="M126 123h2M132 123h2"/>
   <rect className="f-amber" x="148" y="117" width="2.5" height="12"/>
 </>,
 "art-choices": <>
   <rect className="bg1" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 120Q90 100 170 114T320 106V180H0Z"/>
   <path className="f-cream" d="M140 180Q150 130 160 112Q100 100 56 112Q110 106 150 126Q150 150 170 180Z"/>
   <path className="f-cream" d="M160 112Q215 96 276 108Q220 104 172 128Q170 150 190 180H168Q156 150 160 112Z"/>
   <path className="s-ink" d="M158 112V44"/>
   <rect className="f-amber-l s-ink" x="92" y="40" width="64" height="22" rx="4"/>
   <text className="mono f-ink" x="101" y="55" fontSize="12">if ...</text>
   <rect className="f-white s-ink" x="162" y="62" width="70" height="22" rx="4"/>
   <text className="mono f-ink" x="171" y="77" fontSize="12">else</text>
   <path className="f-ink" d="M156 40l-10 4 10 4z"/>
   <path className="f-ink" d="M164 62l10 4-10 4z"/>
   <path className="f-amber" d="M278 28l3 8 8 3-8 3-3 8-3-8-8-3 8-3z"/>
 </>,
 "art-adventure": <>
   <rect className="bg1" width="320" height="180" rx="16"/>
   <circle className="f-amber-l" cx="260" cy="42" r="18"/>
   <path className="f-moss-l" d="M0 118Q80 78 160 112T320 98V180H0Z"/>
   <path className="f-moss" d="M0 150Q100 118 190 144T320 132V180H0Z"/>
   <path className="f-cream" d="M150 180Q190 150 166 118"/>
   <path className="s-cream-w" d="M150 180Q190 152 168 120"/>
   <g className="f-slate"><rect x="132" y="62" width="64" height="52"/><rect x="122" y="48" width="20" height="66"/><rect x="186" y="48" width="20" height="66"/></g>
   <g className="f-plum"><path d="M118 49l14-22 14 22z"/><path d="M182 49l14-22 14 22z"/></g>
   <path className="f-amber-l" d="M154 114V94q10-16 20 0v20z"/>
   <path className="s-ink" d="M164 12v18"/>
   <path className="f-clay" d="M164 12l18 6-18 6z"/>
   <path className="f-amber" d="M60 40l3 8 8 3-8 3-3 8-3-8-8-3 8-3z"/>
 </>,
 "art-arithmetic": <>
   <rect className="bg2" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 142Q90 126 170 138T320 130V180H0Z"/>
   <g className="pouch"><path className="f-cream s-ink" d="M24 140q-6-26 8-34h20q14 8 8 34z"/><path className="s-ink" d="M30 106q10-8 22 0"/></g>
   <g className="pouch"><path className="f-cream s-ink" d="M86 140q-6-26 8-34h20q14 8 8 34z"/><path className="s-ink" d="M92 106q10-8 22 0"/></g>
   <g className="pouch"><path className="f-cream s-ink" d="M148 140q-6-26 8-34h20q14 8 8 34z"/><path className="s-ink" d="M154 106q10-8 22 0"/></g>
   <g className="pouch"><path className="f-cream s-ink" d="M210 140q-6-26 8-34h20q14 8 8 34z"/><path className="s-ink" d="M216 106q10-8 22 0"/></g>
   <g className="pouch"><path className="f-cream s-ink" d="M272 140q-6-26 8-34h20q14 8 8 34z"/><path className="s-ink" d="M278 106q10-8 22 0"/></g>
   <g className="f-amber s-ink-s">
   <circle cx="34" cy="124" r="5"/><circle cx="44" cy="124" r="5"/><circle cx="39" cy="115" r="5"/>
   <circle cx="96" cy="124" r="5"/><circle cx="106" cy="124" r="5"/><circle cx="101" cy="115" r="5"/>
   <circle cx="158" cy="124" r="5"/><circle cx="168" cy="124" r="5"/><circle cx="163" cy="115" r="5"/>
   <circle cx="220" cy="124" r="5"/><circle cx="230" cy="124" r="5"/><circle cx="225" cy="115" r="5"/>
   <circle cx="282" cy="124" r="5"/><circle cx="292" cy="124" r="5"/><circle cx="287" cy="115" r="5"/>
   </g>
   <rect className="f-plum s-ink" x="128" y="30" width="64" height="40" rx="6"/>
   <path className="f-clay s-ink" d="M128 40q32-22 64 0v-4q-32-22-64 0z"/>
   <rect className="f-amber-l s-ink" x="154" y="46" width="12" height="12" rx="2"/>
   <g className="f-amber s-ink-s"><circle cx="146" cy="82" r="5"/><circle cx="174" cy="82" r="5"/></g>
   <text className="mono f-ink" x="22" y="26" fontSize="13" fontWeight="700">17 // 5 = 3</text>
   <text className="mono f-ink" x="22" y="44" fontSize="13" fontWeight="700">17 % 5 = 2</text>
 </>,
 "art-int-float": <>
   <rect className="bg2" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 150Q90 134 170 146T320 138V180H0Z"/>
   <rect className="f-cream s-ink" x="24" y="52" width="272" height="30" rx="4"/>
   <g className="s-ink-s"><path d="M52 52v16M80 52v16M108 52v16M136 52v16M164 52v16M192 52v16M220 52v16M248 52v16M276 52v16"/></g>
   <g className="s-moss-s"><path d="M66 52v9M94 52v9M122 52v9M150 52v9M178 52v9M206 52v9M234 52v9M262 52v9"/></g>
   <text className="mono f-ink" x="46" y="102" fontSize="14" fontWeight="700">3</text>
   <text className="mono f-ink" x="132" y="102" fontSize="14" fontWeight="700">4</text>
   <text className="mono f-ink" x="214" y="102" fontSize="14" fontWeight="700">5</text>
   <path className="f-clay s-ink" d="M150 118l-9-14h18z"/>
   <rect className="f-white s-ink" x="112" y="124" width="76" height="26" rx="5"/>
   <text className="mono f-clay" x="124" y="142" fontSize="14" fontWeight="700">4.5</text>
   <rect className="f-amber-l s-ink" x="28" y="112" width="52" height="26" rx="5"/>
   <text className="mono f-ink" x="42" y="130" fontSize="14" fontWeight="700">int</text>
   <rect className="f-amber-l s-ink" x="240" y="112" width="56" height="26" rx="5"/>
   <text className="mono f-ink" x="248" y="130" fontSize="14" fontWeight="700">float</text>
 </>,
 "art-convert": <>
   <rect className="bg2" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 150Q90 134 170 146T320 138V180H0Z"/>
   <rect className="f-white s-ink" x="28" y="62" width="76" height="50" rx="8"/>
   <text className="mono f-clay" x="46" y="96" fontSize="26" fontWeight="700">"7"</text>
   <text className="sans f-ink" x="28" y="130" fontSize="11">text</text>
   <path className="f-amber-l s-ink" d="M130 62h60l-14 26v22h-32V88z"/>
   <text className="mono f-ink" x="134" y="52" fontSize="12">int()</text>
   <path className="s-ink" d="M110 86h14M196 86h14"/>
   <path className="f-ink" d="M122 80l8 6-8 6zM208 80l8 6-8 6z"/>
   <circle className="f-amber s-ink" cx="262" cy="84" r="30"/>
   <text className="mono f-ink" x="251" y="94" fontSize="28" fontWeight="700">7</text>
   <text className="sans f-ink" x="236" y="130" fontSize="11">number</text>
   <g className="f-amber s-ink-s"><circle cx="150" cy="130" r="4"/><circle cx="160" cy="134" r="4"/></g>
 </>,
 "art-compare": <>
   <rect className="bg2" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 148Q90 132 170 144T320 136V180H0Z"/>
   <path className="f-ink" d="M158 150h4V50h-4z"/>
   <path className="f-ink" d="M130 150h60v6h-60z"/>
   <path className="s-ink-w" d="M70 62L250 44"/>
   <circle className="f-amber s-ink" cx="160" cy="53" r="7"/>
   <path className="s-ink" d="M70 62L52 100M70 62L88 100M250 44L232 82M250 44L268 82"/>
   <path className="f-cream s-ink" d="M44 100h52q-4 16-26 16T44 100z"/>
   <path className="f-cream s-ink" d="M224 82h52q-4 16-26 16T224 82z"/>
   <text className="mono f-ink" x="44" y="136" fontSize="14" fontWeight="700">secret</text>
   <text className="mono f-clay" x="236" y="118" fontSize="14" fontWeight="700">guess</text>
   <rect className="f-white s-ink" x="132" y="112" width="56" height="26" rx="6"/>
   <text className="mono f-moss" x="143" y="130" fontSize="16" fontWeight="700">{'>= =='}</text>
 </>,
 "art-logic": <>
   <rect className="bg2" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 150Q90 134 170 146T320 138V180H0Z"/>
   <path className="f-slate s-ink" d="M120 150V70q0-40 40-40t40 40v80z"/>
   <path className="f-ink" d="M134 150V74q0-24 26-24t26 24v76z"/>
   <path className="f-amber-l" d="M146 150V80q0-14 14-14t14 14v70z"/>
   <rect className="f-white s-ink" x="28" y="48" width="56" height="34" rx="6"/>
   <circle className="f-amber s-ink" cx="46" cy="65" r="8"/>
   <text className="mono f-ink" x="58" y="70" fontSize="12">A</text>
   <rect className="f-white s-ink" x="28" y="98" width="56" height="34" rx="6"/>
   <circle className="f-amber s-ink" cx="46" cy="115" r="8"/>
   <text className="mono f-ink" x="58" y="120" fontSize="12">B</text>
   <path className="s-ink" d="M84 65h22q10 0 10 14v14M84 115h22q10 0 10-14"/>
   <rect className="f-cream s-ink" x="232" y="58" width="64" height="28" rx="6"/>
   <text className="mono f-ink" x="244" y="77" fontSize="14" fontWeight="700">and</text>
   <rect className="f-cream s-ink" x="232" y="94" width="64" height="28" rx="6"/>
   <text className="mono f-ink" x="248" y="113" fontSize="14" fontWeight="700">or</text>
   <rect className="f-cream s-ink" x="232" y="130" width="64" height="28" rx="6"/>
   <text className="mono f-ink" x="240" y="149" fontSize="14" fontWeight="700">not</text>
 </>,
 "art-elif": <>
   <rect className="bg2" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 150Q90 134 170 146T320 138V180H0Z"/>
   <rect className="f-white s-ink" x="40" y="22" width="150" height="30" rx="6"/>
   <text className="mono f-ink" x="52" y="42" fontSize="13">if exact</text>
   <rect className="f-white s-ink" x="40" y="62" width="150" height="30" rx="6"/>
   <text className="mono f-ink" x="52" y="82" fontSize="13">elif close</text>
   <rect className="f-white s-ink" x="40" y="102" width="150" height="30" rx="6"/>
   <text className="mono f-ink" x="52" y="122" fontSize="13">elif near</text>
   <rect className="f-white s-ink" x="40" y="142" width="150" height="26" rx="6"/>
   <text className="mono f-ink" x="52" y="160" fontSize="13">else</text>
   <rect className="f-amber s-ink" x="206" y="62" width="82" height="30" rx="6"/>
   <text className="mono f-ink" x="216" y="82" fontSize="14" fontWeight="700">score 5</text>
   <path className="s-clay-w" d="M190 77h14"/>
   <path className="f-clay" d="M202 71l8 6-8 6z"/>
   <g className="f-slate"><circle cx="24" cy="37" r="5"/><circle cx="24" cy="77" r="5"/></g>
   <path className="s-slate-d" d="M24 42v30"/>
 </>,
 "art-while": <>
   <rect className="bg3" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 150Q90 134 170 146T320 138V180H0Z"/>
   <ellipse className="s-moss-w" cx="130" cy="92" rx="88" ry="50"/>
   <path className="f-moss" d="M216 92l-12-12 2 24z"/>
   <circle className="f-cream s-ink" cx="130" cy="92" r="24"/>
   <text className="mono f-ink" x="121" y="102" fontSize="28" fontWeight="700">?</text>
   <circle className="f-amber s-ink" cx="62" cy="68" r="9"/>
   <path className="f-plum s-ink" d="M48 112q0-18 14-18t14 18z"/>
   <path className="f-slate s-ink" d="M246 150V82q0-26 28-26t28 26v68z"/>
   <path className="f-ink" d="M256 150V86q0-16 18-16t18 16v64z"/>
   <text className="mono f-ink" x="236" y="46" fontSize="13" fontWeight="700">== secret</text>
   <path className="s-ink-s" d="M226 112h16"/>
   <path className="f-ink" d="M240 106l8 6-8 6z"/>
   <text className="mono f-moss" x="64" y="168" fontSize="13" fontWeight="700">while guess != secret:</text>
 </>,
 "art-three-tries": <>
   <rect className="bg3" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 150Q90 134 170 146T320 138V180H0Z"/>
   <g>
   <rect className="f-cream s-ink" x="48" y="72" width="40" height="64" rx="6"/>
   <path className="s-ink" d="M68 72V58"/>
   <path className="f-ink" d="M68 40q-8 10 0 18 8-8 0-18z"/>
   <rect className="f-cream s-ink" x="140" y="72" width="40" height="64" rx="6"/>
   <path className="s-ink" d="M160 72V58"/>
   <path className="f-ink" d="M160 40q-8 10 0 18 8-8 0-18z"/>
   <rect className="f-white s-ink" x="232" y="72" width="40" height="64" rx="6"/>
   <path className="s-ink" d="M252 72V58"/>
   <path className="f-amber s-ink" d="M252 30q-14 16 0 30 14-14 0-30z"/>
   <circle className="f-amber-l" cx="252" cy="46" r="3"/>
   </g>
   <text className="mono f-ink" x="62" y="108" fontSize="16" fontWeight="700">1</text>
   <text className="mono f-ink" x="154" y="108" fontSize="16" fontWeight="700">2</text>
   <text className="mono f-ink" x="246" y="108" fontSize="16" fontWeight="700">3</text>
   <path className="s-clay-w" d="M52 150l32 14M84 150l-32 14"/>
   <path className="s-clay-w" d="M144 150l32 14M176 150l-32 14"/>
   <text className="mono f-moss" x="14" y="24" fontSize="13" fontWeight="700">tries = 3</text>
 </>,
 "art-for-range": <>
   <rect className="bg3" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 150Q90 134 170 146T320 138V180H0Z"/>
   <path className="f-cream s-ink" d="M30 152v-22h44v-20h44v-20h44v-20h44v-20h44v-20h20v122z"/>
   <path className="s-ink-s" d="M74 130v22M118 110v42M162 90v62M206 70v82M250 50v102"/>
   <text className="mono f-ink" x="46" y="148" fontSize="14" fontWeight="700">0</text>
   <text className="mono f-ink" x="90" y="148" fontSize="14" fontWeight="700">2</text>
   <text className="mono f-ink" x="134" y="148" fontSize="14" fontWeight="700">4</text>
   <text className="mono f-ink" x="178" y="148" fontSize="14" fontWeight="700">6</text>
   <text className="mono f-ink" x="222" y="148" fontSize="14" fontWeight="700">8</text>
   <circle className="f-cream s-ink" cx="96" cy="86" r="8"/>
   <path className="f-plum s-ink" d="M85 108q0-14 11-14t11 14z"/>
   <path className="s-clay-w" d="M104 84Q124 58 142 66"/>
   <path className="f-clay" d="M146 62l-12 0 6 11z"/>
   <path className="s-clay-w" d="M150 62Q168 38 186 46"/>
   <path className="f-clay" d="M190 42l-12 0 6 11z"/>
   <text className="mono f-moss" x="18" y="28" fontSize="13" fontWeight="700">range(0, 10, 2)</text>
 </>,
 "art-accumulate": <>
   <rect className="bg3" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 150Q90 134 170 146T320 138V180H0Z"/>
   <rect className="f-amber-l s-ink" x="34" y="110" width="40" height="36" rx="4"/>
   <rect className="f-amber-l s-ink" x="96" y="88" width="40" height="58" rx="4"/>
   <rect className="f-amber-l s-ink" x="158" y="68" width="40" height="78" rx="4"/>
   <rect className="f-amber s-ink" x="220" y="38" width="52" height="108" rx="4"/>
   <text className="mono f-ink" x="42" y="132" fontSize="14" fontWeight="700">+4</text>
   <text className="mono f-ink" x="104" y="122" fontSize="14" fontWeight="700">+6</text>
   <text className="mono f-ink" x="166" y="112" fontSize="14" fontWeight="700">+5</text>
   <text className="mono f-ink" x="226" y="96" fontSize="18" fontWeight="700">15</text>
   <text className="mono f-ink" x="226" y="118" fontSize="11">total</text>
   <path className="s-ink-s" d="M76 126h18M138 116h18M200 106h18"/>
   <text className="mono f-moss" x="20" y="28" fontSize="13" fontWeight="700">total = total + points</text>
 </>,
 "art-nested": <>
   <rect className="bg3" width="320" height="180" rx="16"/>
   <g className="f-cream s-ink">
   <rect x="40" y="26" width="52" height="38" rx="5"/><rect x="100" y="26" width="52" height="38" rx="5"/><rect x="160" y="26" width="52" height="38" rx="5"/><rect x="220" y="26" width="52" height="38" rx="5"/>
   <rect x="40" y="72" width="52" height="38" rx="5"/><rect x="100" y="72" width="52" height="38" rx="5"/><rect x="160" y="72" width="52" height="38" rx="5"/><rect x="220" y="72" width="52" height="38" rx="5"/>
   <rect x="40" y="118" width="52" height="38" rx="5"/><rect x="100" y="118" width="52" height="38" rx="5"/><rect x="160" y="118" width="52" height="38" rx="5"/><rect x="220" y="118" width="52" height="38" rx="5"/>
   </g>
   <path className="s-clay-w" d="M66 45H246Q262 45 262 58Q262 91 246 91H66Q50 91 50 104Q50 137 66 137H246"/>
   <g className="f-amber s-ink-s"><circle cx="74" cy="52" r="5"/><circle cx="130" cy="58" r="5"/><circle cx="190" cy="50" r="5"/><circle cx="246" cy="56" r="5"/><circle cx="74" cy="96" r="5"/><circle cx="190" cy="100" r="5"/><circle cx="130" cy="140" r="5"/><circle cx="246" cy="140" r="5"/></g>
   <text className="mono f-moss" x="286" y="48" fontSize="12" fontWeight="700">row</text>
   <text className="mono f-moss" x="284" y="92" fontSize="12" fontWeight="700">row</text>
   <text className="mono f-moss" x="284" y="138" fontSize="12" fontWeight="700">row</text>
 </>,
 // The plain picture for a lesson that has none of its own yet.
 fallback: <>
   <rect className="bg1" width="320" height="180" rx="16"/>
   <path className="f-moss-l" d="M0 128Q80 104 160 122T320 112V180H0Z"/>
   <path className="f-moss" d="M0 156Q90 136 170 152T320 142V180H0Z"/>
   <rect className="f-white s-ink" x="128" y="54" width="64" height="40" rx="10"/>
   <text className="mono f-moss" x="146" y="80" fontSize="18" fontWeight="700">py</text>
   <path className="f-amber" d="M262 34l3 8 8 3-8 3-3 8-3-8-8-3 8-3z"/>
 </>,
};
export const FALLBACK_LABEL = 'Green hills under a small py sign';

/** The picture for a lesson, keyed by lesson id, with a plain fallback for any lesson without one.
 * label false: decorative (hidden from screen readers), for thumbnails beside the lesson's own title. */
export default function LessonArt({lesson, label, className}: {lesson: string; label?: string | false; className?: string}) {
 const known = LESSON_ART[lesson], id = known?.art ?? 'fallback';
 const name = label === false ? undefined : label ?? known?.label ?? FALLBACK_LABEL;
 return <svg className={'art' + (className ? ' ' + className : '')} viewBox="0 0 320 180" data-art={id} focusable="false"
  {...(name ? {role: 'img', 'aria-label': name} : {'aria-hidden': true})}>{PICTURES[id]}</svg>;
}

const ICONS: Record<string, ReactNode> = {
 "discover": <><path d="M12 2v3M8 5h8l1 5H7zM7 10l-1 9h12l-1-9M9 14h6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></>,
 "example": <><path d="M4 5h7a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2H4zM20 5h-7a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h7z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/></>,
 "predict": <><path d="M9 9a3 3 0 1 1 4 2.8c-.9.5-1 1.2-1 2.2M12 18h.01" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/><circle cx="12" cy="12" r="9.5" fill="none" stroke="currentColor" strokeWidth="1.8"/></>,
 "try": <><path d="M8 5l11 7-11 7z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/></>,
 "challenge": <><path d="M6 21V4M6 5h11l-2 4 2 4H6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></>,
 "lock": <><rect x="5" y="11" width="14" height="10" rx="2" fill="none" stroke="currentColor" strokeWidth="1.8"/><path d="M8 11V8a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" strokeWidth="1.8"/></>,
 "check": <><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"/></>,
 "arrow": <><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></>,
};
export type IconName = "discover" | "example" | "predict" | "try" | "challenge" | "lock" | "check" | "arrow";

/** A small line icon. Always decorative: the text beside it says what it means. */
export function Icon({name, className}: {name: IconName; className?: string}) {
 return <svg className={'ico' + (className ? ' ' + className : '')} viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>;
}

/** The five card types, in lesson order: the class suffix (ct-*, t-*) and the icon. */
export const CARD_TYPES:{type:string;icon:IconName}[]=[{type:'discover',icon:'discover'},{type:'example',icon:'example'},{type:'predict',icon:'predict'},{type:'try',icon:'try'},{type:'challenge',icon:'challenge'}];
