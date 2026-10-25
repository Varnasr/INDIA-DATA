/* Languages: English, Hindi, Urdu (right to left) and Telugu.

   Load this first, in <head>. It decides the language (?lang= in the address,
   else the reader's last choice, else English), sets <html lang> and dir,
   loads the dictionary and the script's font, and defines L().

   Two kinds of text are translated:
   - Sentences built by a page's script go through L('English template with
     {placeholders}', {placeholders: values}). The English template is the
     key; scripts/check_i18n.py fails CI if any key lacks a translation.
   - Fixed text in the markup is translated by L.apply(), which sir.js calls
     before the page's own script runs. A unit is an element whose children
     are all inline (a, b, strong, em, span, br, code...); its innerHTML is
     the key. Other elements have their own text nodes translated one by
     one, as are the children of an element marked data-i18n-each (a row of
     links whose addresses change from page to page). Attributes (aria-label, placeholder, title), the page title and
     the meta description are keys too. Mark anything that must stay as it
     is with data-no-i18n.

   Figures stay in Western digits with Indian grouping (6,62,063), and names
   of places, parties and people stay as the data spells them. */
(function () {
  'use strict';
  var LANGS = {
    en: { name: 'English', short: 'EN', dir: 'ltr' },
    hi: { name: 'हिन्दी', short: 'हिं', dir: 'ltr', font: 'Noto+Sans+Devanagari:wght@400;600;700' },
    ur: { name: 'اردو', short: 'اردو', dir: 'rtl', font: 'Noto+Nastaliq+Urdu:wght@400;700' },
    te: { name: 'తెలుగు', short: 'తె', dir: 'ltr', font: 'Noto+Sans+Telugu:wght@400;600;700' },
    ta: { name: 'தமிழ்', short: 'த', dir: 'ltr', font: 'Noto+Sans+Tamil:wght@400;600;700' },
    bn: { name: 'বাংলা', short: 'বাং', dir: 'ltr', font: 'Noto+Sans+Bengali:wght@400;600;700' }
  };
  // The menu is in every page's header. Set this to false to hide it, and a
  // language is then reached only by a link carrying ?lang=.
  var MENU = true;
  // Content hashes of the data files and dictionaries, written by
  // scripts/stamp.py on every deploy, so a changed file gets a new address.
  window.SIR_V = /*stamp*/{"assets/i18n/bn.js":"f69de67f","assets/i18n/hi.js":"b43339ad","assets/i18n/ta.js":"5d919050","assets/i18n/te.js":"79d2d2ea","assets/i18n/ur.js":"64564981","data/andaman/summary.json":"087048f4","data/andhrapradesh/districts.json":"4b9e661b","data/andhrapradesh/summary.json":"cf1016e9","data/arunachal/summary.json":"65a98982","data/assam/constituencies.json":"b4e02b9e","data/assam/districts.json":"cb11122c","data/assam/summary.json":"51850f4b","data/bihar/booths/ac_001.json":"b7cfab69","data/bihar/booths/ac_002.json":"b5be644c","data/bihar/booths/ac_003.json":"f9191965","data/bihar/booths/ac_004.json":"b2f863e9","data/bihar/booths/ac_005.json":"b208af10","data/bihar/booths/ac_006.json":"e4377af3","data/bihar/booths/ac_007.json":"32b0c39d","data/bihar/booths/ac_008.json":"d77a83a4","data/bihar/booths/ac_009.json":"55fcc95d","data/bihar/booths/ac_010.json":"5f7c8b1a","data/bihar/booths/ac_011.json":"8686abc3","data/bihar/booths/ac_012.json":"32ac8840","data/bihar/booths/ac_013.json":"e2dcd7d7","data/bihar/booths/ac_014.json":"a58555dd","data/bihar/booths/ac_015.json":"b9bf7a09","data/bihar/booths/ac_016.json":"98b36e98","data/bihar/booths/ac_017.json":"252c84f8","data/bihar/booths/ac_018.json":"ee40b827","data/bihar/booths/ac_019.json":"87f9c51f","data/bihar/booths/ac_020.json":"8820acef","data/bihar/booths/ac_021.json":"6fa32456","data/bihar/booths/ac_022.json":"2fd149c8","data/bihar/booths/ac_023.json":"bb2cc222","data/bihar/booths/ac_024.json":"6a035574","data/bihar/booths/ac_025.json":"3137c9d7","data/bihar/booths/ac_026.json":"c3af4755","data/bihar/booths/ac_027.json":"b9896a9d","data/bihar/booths/ac_028.json":"6d943395","data/bihar/booths/ac_029.json":"7233598a","data/bihar/booths/ac_030.json":"9d9de06c","data/bihar/booths/ac_031.json":"7d1796ea","data/bihar/booths/ac_032.json":"02457d3f","data/bihar/booths/ac_033.json":"c1a0ee8b","data/bihar/booths/ac_034.json":"aafe5042","data/bihar/booths/ac_035.json":"7ff1a253","data/bihar/booths/ac_036.json":"356dd086","data/bihar/booths/ac_037.json":"b1cc34f4","data/bihar/booths/ac_038.json":"d61832fd","data/bihar/booths/ac_039.json":"76ac8256","data/bihar/booths/ac_040.json":"155d873e","data/bihar/booths/ac_041.json":"94c1712c","data/bihar/booths/ac_042.json":"95620d5c","data/bihar/booths/ac_043.json":"e1832ec7","data/bihar/booths/ac_044.json":"7e37cb07","data/bihar/booths/ac_045.json":"291d0d36","data/bihar/booths/ac_046.json":"082f34d9","data/bihar/booths/ac_047.json":"f4ed38bd","data/bihar/booths/ac_048.json":"fad80526","data/bihar/booths/ac_049.json":"c828daa6","data/bihar/booths/ac_050.json":"6e7edd56","data/bihar/booths/ac_051.json":"a93d41d8","data/bihar/booths/ac_052.json":"7fec890f","data/bihar/booths/ac_053.json":"c1c4cd98","data/bihar/booths/ac_054.json":"6779b877","data/bihar/booths/ac_055.json":"7de349f1","data/bihar/booths/ac_056.json":"31139707","data/bihar/booths/ac_057.json":"3e8e7876","data/bihar/booths/ac_058.json":"c7703eaf","data/bihar/booths/ac_059.json":"8d878fb6","data/bihar/booths/ac_060.json":"d1e62b18","data/bihar/booths/ac_061.json":"744062ce","data/bihar/booths/ac_062.json":"a5cd29d2","data/bihar/booths/ac_063.json":"e86927bc","data/bihar/booths/ac_064.json":"2d5f1960","data/bihar/booths/ac_065.json":"f5879f99","data/bihar/booths/ac_066.json":"eb42066c","data/bihar/booths/ac_067.json":"b1024bba","data/bihar/booths/ac_068.json":"99714e62","data/bihar/booths/ac_069.json":"312f2174","data/bihar/booths/ac_070.json":"784f410e","data/bihar/booths/ac_071.json":"f58637de","data/bihar/booths/ac_072.json":"d9cbcde8","data/bihar/booths/ac_073.json":"fd4148f5","data/bihar/booths/ac_074.json":"13c4720b","data/bihar/booths/ac_075.json":"3104a37a","data/bihar/booths/ac_076.json":"282b9ece","data/bihar/booths/ac_077.json":"a852c494","data/bihar/booths/ac_078.json":"e6f69838","data/bihar/booths/ac_079.json":"f548b3a5","data/bihar/booths/ac_080.json":"a4ac90d1","data/bihar/booths/ac_081.json":"6528c096","data/bihar/booths/ac_082.json":"6413ad2a","data/bihar/booths/ac_083.json":"cdcd8181","data/bihar/booths/ac_084.json":"8a414ba0","data/bihar/booths/ac_085.json":"bec5c4f1","data/bihar/booths/ac_086.json":"45230510","data/bihar/booths/ac_087.json":"01ec5c29","data/bihar/booths/ac_088.json":"a43cd278","data/bihar/booths/ac_089.json":"edfec946","data/bihar/booths/ac_090.json":"1578c474","data/bihar/booths/ac_091.json":"c1d27e10","data/bihar/booths/ac_092.json":"781ee173","data/bihar/booths/ac_093.json":"3dd5fd49","data/bihar/booths/ac_094.json":"d4a456d1","data/bihar/booths/ac_095.json":"55227c4e","data/bihar/booths/ac_096.json":"41860c71","data/bihar/booths/ac_097.json":"2eb499ba","data/bihar/booths/ac_098.json":"bcd52888","data/bihar/booths/ac_099.json":"cc6c85f8","data/bihar/booths/ac_100.json":"b0bb5daa","data/bihar/booths/ac_101.json":"d7e1f115","data/bihar/booths/ac_102.json":"bece458c","data/bihar/booths/ac_103.json":"ca3b1222","data/bihar/booths/ac_104.json":"390805e2","data/bihar/booths/ac_105.json":"37a5e5a5","data/bihar/booths/ac_106.json":"450c27b0","data/bihar/booths/ac_107.json":"5ed25635","data/bihar/booths/ac_108.json":"e61aed5e","data/bihar/booths/ac_109.json":"bd819e3e","data/bihar/booths/ac_110.json":"aa027b2e","data/bihar/booths/ac_111.json":"f00b15c5","data/bihar/booths/ac_112.json":"85fb7b23","data/bihar/booths/ac_113.json":"42d7e5c1","data/bihar/booths/ac_114.json":"0fee8559","data/bihar/booths/ac_115.json":"0f4afaa6","data/bihar/booths/ac_116.json":"29f59d02","data/bihar/booths/ac_117.json":"b20fc4cd","data/bihar/booths/ac_118.json":"08786511","data/bihar/booths/ac_119.json":"a9ac305d","data/bihar/booths/ac_120.json":"b3e2db24","data/bihar/booths/ac_121.json":"b04cf65a","data/bihar/booths/ac_122.json":"c4da1686","data/bihar/booths/ac_123.json":"1752c9b5","data/bihar/booths/ac_124.json":"ee23fab9","data/bihar/booths/ac_125.json":"1e3adf91","data/bihar/booths/ac_126.json":"ce656262","data/bihar/booths/ac_127.json":"f094c0b5","data/bihar/booths/ac_128.json":"8d5d2c8f","data/bihar/booths/ac_129.json":"d6f6c52e","data/bihar/booths/ac_130.json":"2cc3265d","data/bihar/booths/ac_131.json":"1e891180","data/bihar/booths/ac_132.json":"439e9737","data/bihar/booths/ac_133.json":"d5585521","data/bihar/booths/ac_134.json":"78b17411","data/bihar/booths/ac_135.json":"5491969b","data/bihar/booths/ac_136.json":"10c41db8","data/bihar/booths/ac_137.json":"63404c7b","data/bihar/booths/ac_138.json":"bb19ba0f","data/bihar/booths/ac_139.json":"c29579c5","data/bihar/booths/ac_140.json":"d4e8b7fa","data/bihar/booths/ac_141.json":"e8efdce9","data/bihar/booths/ac_142.json":"c4e889c8","data/bihar/booths/ac_143.json":"91be4dff","data/bihar/booths/ac_144.json":"55f741bb","data/bihar/booths/ac_145.json":"4c6cca6f","data/bihar/booths/ac_146.json":"a587511e","data/bihar/booths/ac_147.json":"81c14b09","data/bihar/booths/ac_148.json":"92f36293","data/bihar/booths/ac_149.json":"266aff9c","data/bihar/booths/ac_150.json":"9824fa60","data/bihar/booths/ac_151.json":"212db14a","data/bihar/booths/ac_152.json":"ebea3839","data/bihar/booths/ac_153.json":"c15d5726","data/bihar/booths/ac_154.json":"1a51bac9","data/bihar/booths/ac_155.json":"5e2ed285","data/bihar/booths/ac_156.json":"30a978a5","data/bihar/booths/ac_157.json":"9be9fe94","data/bihar/booths/ac_158.json":"f14e4ffe","data/bihar/booths/ac_159.json":"c50f4649","data/bihar/booths/ac_160.json":"555a0f96","data/bihar/booths/ac_161.json":"90674c10","data/bihar/booths/ac_162.json":"d27be467","data/bihar/booths/ac_163.json":"bf16c303","data/bihar/booths/ac_164.json":"a744c4a0","data/bihar/booths/ac_165.json":"50ecc8a3","data/bihar/booths/ac_166.json":"22040099","data/bihar/booths/ac_167.json":"83d6891e","data/bihar/booths/ac_168.json":"185c18bc","data/bihar/booths/ac_169.json":"93f36840","data/bihar/booths/ac_170.json":"ebd44a93","data/bihar/booths/ac_171.json":"d58003da","data/bihar/booths/ac_172.json":"625f7d1b","data/bihar/booths/ac_173.json":"7b23f357","data/bihar/booths/ac_174.json":"dd0e2a4c","data/bihar/booths/ac_175.json":"b7021be3","data/bihar/booths/ac_176.json":"51749038","data/bihar/booths/ac_177.json":"1cde94a4","data/bihar/booths/ac_178.json":"d2b68b03","data/bihar/booths/ac_179.json":"70de7ebb","data/bihar/booths/ac_180.json":"93835818","data/bihar/booths/ac_181.json":"8a5497f8","data/bihar/booths/ac_182.json":"d295f15b","data/bihar/booths/ac_183.json":"ecf62ac6","data/bihar/booths/ac_184.json":"ed1a27b1","data/bihar/booths/ac_185.json":"52ee3caa","data/bihar/booths/ac_186.json":"b795cc0e","data/bihar/booths/ac_187.json":"41af21fb","data/bihar/booths/ac_188.json":"99b8ddee","data/bihar/booths/ac_189.json":"c7d8c563","data/bihar/booths/ac_190.json":"6553cef8","data/bihar/booths/ac_191.json":"f9833a5e","data/bihar/booths/ac_192.json":"cb4b6c70","data/bihar/booths/ac_193.json":"204ab22a","data/bihar/booths/ac_194.json":"fbd5e389","data/bihar/booths/ac_195.json":"8c8f648f","data/bihar/booths/ac_196.json":"b4ecbccb","data/bihar/booths/ac_197.json":"473b6b0a","data/bihar/booths/ac_198.json":"b4cd1654","data/bihar/booths/ac_199.json":"e7cb7ec5","data/bihar/booths/ac_200.json":"50aee4a9","data/bihar/booths/ac_201.json":"b0688a37","data/bihar/booths/ac_202.json":"26628a56","data/bihar/booths/ac_203.json":"6ff2522e","data/bihar/booths/ac_204.json":"3ce15002","data/bihar/booths/ac_205.json":"f6792241","data/bihar/booths/ac_206.json":"8aa87e1f","data/bihar/booths/ac_207.json":"30b5aecf","data/bihar/booths/ac_208.json":"691dff8c","data/bihar/booths/ac_209.json":"b4739d1b","data/bihar/booths/ac_210.json":"9b53af03","data/bihar/booths/ac_211.json":"965facfa","data/bihar/booths/ac_212.json":"ca5266f4","data/bihar/booths/ac_213.json":"d799a79f","data/bihar/booths/ac_214.json":"e289a1cb","data/bihar/booths/ac_215.json":"023939b7","data/bihar/booths/ac_216.json":"d065ea75","data/bihar/booths/ac_217.json":"5f5ffad2","data/bihar/booths/ac_218.json":"81d13fb2","data/bihar/booths/ac_219.json":"aac7ea19","data/bihar/booths/ac_220.json":"04addd9f","data/bihar/booths/ac_221.json":"f304441f","data/bihar/booths/ac_222.json":"8dd351c1","data/bihar/booths/ac_223.json":"1384e191","data/bihar/booths/ac_224.json":"793b7dc7","data/bihar/booths/ac_225.json":"cffb20c1","data/bihar/booths/ac_226.json":"ee669184","data/bihar/booths/ac_227.json":"63d85ab3","data/bihar/booths/ac_228.json":"54550c97","data/bihar/booths/ac_229.json":"b711e67e","data/bihar/booths/ac_230.json":"41a94570","data/bihar/booths/ac_231.json":"021bebbc","data/bihar/booths/ac_232.json":"8728d8c8","data/bihar/booths/ac_233.json":"6a929af6","data/bihar/booths/ac_234.json":"d913fdd4","data/bihar/booths/ac_235.json":"d8e24cb0","data/bihar/booths/ac_236.json":"b30e0171","data/bihar/booths/ac_237.json":"b9d33435","data/bihar/booths/ac_238.json":"ad3fed81","data/bihar/booths/ac_239.json":"e34974a5","data/bihar/booths/ac_240.json":"b027b994","data/bihar/booths/ac_241.json":"9e419357","data/bihar/booths/ac_242.json":"ecc8d0df","data/bihar/booths/ac_243.json":"18beb2cd","data/bihar/constituencies.json":"74f03d84","data/bihar/districts.json":"24fb692e","data/bihar/final.json":"b7a5c724","data/bihar/identity.json":"8793a166","data/bihar/impact.json":"c277b60a","data/bihar/reasons.json":"8a09fb02","data/bihar/robust.json":"a020a1f2","data/bihar/summary.json":"2fa3801c","data/bihar/swing.json":"7fed00d1","data/bihar/tests.json":"01440e10","data/chandigarh/summary.json":"8df4ac5f","data/chhattisgarh/districts.json":"47421152","data/chhattisgarh/summary.json":"095cd652","data/delhi/constituencies.json":"dac1d25c","data/delhi/districts.json":"2ddb4d94","data/delhi/summary.json":"fb7fc0ea","data/dnhdd/summary.json":"c14376d4","data/downloads.json":"59f4bc60","data/geo/bihar.json":"57b782e9","data/geo/delhi.json":"7a319f12","data/geo/gujarat.json":"ad40f63f","data/geo/india.json":"f82dbbe5","data/geo/karnataka.json":"04fafe07","data/geo/kerala.json":"89fe67ed","data/geo/maharashtra.json":"567b261a","data/geo/maharashtra_ac.json":"06877dc3","data/geo/rajasthan.json":"4eca4012","data/geo/tamilnadu.json":"19568e15","data/geo/uttarakhand.json":"09f082bc","data/geo/uttarpradesh.json":"94fbba58","data/geo/westbengal.json":"d8696f63","data/goa/summary.json":"423bc859","data/gujarat/constituencies.json":"da55c574","data/gujarat/districts.json":"048b21ff","data/gujarat/final.json":"a82b4f47","data/gujarat/summary.json":"0bc9ebf5","data/haryana/summary.json":"13e1435a","data/hyderabad/impact.json":"bacb0c82","data/hyderabad/parts.json":"605536e2","data/hyderabad/summary.json":"985ee2e8","data/hyderabad/telangana.json":"38c4e0ad","data/india/ac_change.json":"3522c7e4","data/india/ac_finder.json":"dbd93f59","data/india/border.json":"7b025c6c","data/india/brief.json":"a051f3d6","data/india/cases.json":"a1e6010a","data/india/cities.json":"4e6e4a01","data/india/disputes.json":"23fd1966","data/india/disputes_counts.json":"744ca7c1","data/india/events.json":"bc671cd1","data/india/factors.json":"a39f862e","data/india/factors/andhra-pradesh.json":"cf92c41e","data/india/factors/assam.json":"fdb12919","data/india/factors/bihar.json":"d7000bde","data/india/factors/chhattisgarh.json":"de6b2739","data/india/factors/delhi.json":"34b5c65c","data/india/factors/gujarat.json":"6fb34517","data/india/factors/karnataka.json":"2d6bc13f","data/india/factors/kerala.json":"0aca1c31","data/india/factors/maharashtra.json":"48e25f83","data/india/factors/manipur.json":"c93cb45e","data/india/factors/meghalaya.json":"684c42bd","data/india/factors/mizoram.json":"93143691","data/india/factors/odisha.json":"7ea544d2","data/india/factors/rajasthan.json":"b55104fa","data/india/factors/tamil-nadu.json":"11d15e41","data/india/factors/telangana.json":"f770bab8","data/india/factors/uttar-pradesh.json":"4dd86d9f","data/india/factors/uttarakhand.json":"9ffe827e","data/india/factors/west-bengal.json":"6c731e73","data/india/help.json":"014677db","data/india/help_counts.json":"ffea2542","data/india/lok_sabha_electors.json":"37e60e75","data/india/margins.json":"fa13cd7d","data/india/notices.json":"901f98b6","data/india/nrc.json":"9d0757fe","data/india/panels.json":"9c44dca8","data/india/process.json":"f70743ed","data/india/reads.json":"01afaa03","data/india/reserved.json":"366f7e5e","data/india/rti.json":"96905ff5","data/india/states.json":"bef707f8","data/india/urban.json":"99c3744e","data/india/women.json":"0152a12d","data/jharkhand/summary.json":"f875b4d3","data/karnataka/districts.json":"f84bae75","data/karnataka/summary.json":"f3a4e694","data/kerala/constituencies.json":"30ae1874","data/kerala/districts.json":"42cefeda","data/kerala/summary.json":"5baa96d6","data/lakshadweep/summary.json":"d8ceffc3","data/madhyapradesh/summary.json":"ae018c6b","data/maharashtra/constituencies.json":"abb3e00f","data/maharashtra/districts.json":"8df4fe78","data/maharashtra/summary.json":"8d737c5e","data/manipur/constituencies.json":"0e31d684","data/manipur/districts.json":"54650d9b","data/manipur/summary.json":"70884385","data/meghalaya/constituencies.json":"1a23a81d","data/meghalaya/districts.json":"509acdb0","data/meghalaya/summary.json":"033fdf1f","data/mizoram/districts.json":"b6fa6184","data/mizoram/summary.json":"8c59c9ed","data/nagaland/summary.json":"35d72180","data/odisha/constituencies.json":"61eeb005","data/odisha/districts.json":"382020c8","data/odisha/summary.json":"7cbe18a4","data/puducherry/summary.json":"fe8289e0","data/punjab/summary.json":"cd6f4846","data/rajasthan/constituencies.json":"6e0c7717","data/rajasthan/districts.json":"c257f374","data/rajasthan/summary.json":"6c89a470","data/search.json":"9b9321c0","data/sikkim/summary.json":"f9f9f60c","data/tamilnadu/constituencies.json":"5b04861d","data/tamilnadu/districts.json":"8f03e4e6","data/tamilnadu/summary.json":"157a25fa","data/tripura/summary.json":"c8cd0399","data/updates.json":"c7657e2d","data/uttarakhand/constituencies.json":"bcf46b57","data/uttarakhand/districts.json":"c98e7762","data/uttarakhand/summary.json":"e5a5a7f0","data/uttarpradesh/analysis.json":"9194770f","data/uttarpradesh/districts.json":"d0bf5fb6","data/uttarpradesh/summary.json":"aaff7dda","data/westbengal/constituencies.json":"b7e92307","data/westbengal/districts.json":"d6cdc3f8","data/westbengal/summary.json":"0fadde49"}/*stamp*/;
  var vq = function (p) { return SIR_V[p] ? '?v=' + SIR_V[p] : ''; };
  var here = document.currentScript ? document.currentScript.src : '';
  var base = here.slice(0, here.lastIndexOf('/') + 1);
  var params = new URLSearchParams(location.search);
  var asked = params.get('lang'), saved = null;
  try { saved = localStorage.getItem('sir-lang'); } catch (e) {}
  var lang = LANGS[asked] ? asked : (MENU && LANGS[saved] ? saved : 'en');
  if (LANGS[asked]) { try { localStorage.setItem('sir-lang', asked); } catch (e) {} }
  var collect = params.has('i18n-collect');
  var html = document.documentElement;
  html.lang = lang;
  html.dir = LANGS[lang].dir;
  html.setAttribute('data-lang', lang);
  window.SIR_DICT = window.SIR_DICT || {};
  if (lang !== 'en') {
    document.write('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' +
      '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=' + LANGS[lang].font + '&display=swap">' +
      '<script src="' + base + 'i18n/' + lang + '.js' + vq('assets/i18n/' + lang + '.js') + '"><\/script>');
  }

  function norm(s) { return s.replace(/\s+/g, ' ').trim(); }
  var seen = {};
  var L = window.L = function (key, vars) {
    if (collect) seen[key] = 1;
    var s = (lang !== 'en' && window.SIR_DICT[key]) || key;
    if (vars) s = s.replace(/\{(\w+)\}/g, function (m, k) { return vars[k] != null ? vars[k] : m; });
    return s;
  };
  L.lang = lang;
  L.langs = LANGS;
  L.seen = seen;

  // ------------------------------------------------------ fixed text in markup
  var INLINE = { A: 1, B: 1, STRONG: 1, EM: 1, I: 1, SPAN: 1, BR: 1, CODE: 1, SUP: 1, SUB: 1, SMALL: 1, ABBR: 1, TIME: 1 };
  var SKIP = { SCRIPT: 1, STYLE: 1, SVG: 1, CANVAS: 1, TEXTAREA: 1, svg: 1, NOSCRIPT: 1 };
  var ATTRS = ['aria-label', 'placeholder', 'title'];
  var statics = {};
  function has(s) { return /[A-Za-z]/.test(s); }
  function tr(key) {
    if (collect) { statics[key] = 1; return null; }
    if (lang === 'en') return null;
    return window.SIR_DICT[key] || null;
  }
  function attrs(el) {
    ATTRS.forEach(function (a) {
      var v = el.getAttribute(a);
      if (v && has(v)) { var t = tr(norm(v)); if (t) el.setAttribute(a, t); }
    });
  }
  function isUnit(el) {
    for (var c = el.firstElementChild; c; c = c.nextElementSibling) {
      if (!INLINE[c.tagName] || c.hasAttribute('data-no-i18n')) return false;
      if (c.firstElementChild && !isUnit(c)) return false;
    }
    return true;
  }
  function walk(el) {
    if (SKIP[el.tagName] || el.hasAttribute('data-no-i18n')) return;
    attrs(el);
    if (el.firstElementChild && el.tagName !== 'BODY' && !el.hasAttribute('data-i18n-each') && isUnit(el) && has(el.textContent)) {
      var key = norm(el.innerHTML), t = tr(key);
      if (t) el.innerHTML = t;
      el.querySelectorAll('*').forEach(attrs);
      return;
    }
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3) {
        var raw = n.nodeValue;
        if (!has(raw)) continue;
        var k = norm(raw), tt = tr(k);
        if (tt) n.nodeValue = raw.replace(k, tt);
      } else if (n.nodeType === 1) walk(n);
    }
  }
  L.apply = function (root) {
    root = root || document.body;
    var t = tr(norm(document.title)); if (t) document.title = t;
    var md = document.querySelector('meta[name="description"]');
    if (md) { var tm = tr(norm(md.content)); if (tm) md.content = tm; }
    walk(root);
    // The language menu, first among the controls in the header.
    var ctl = document.querySelector('header.top .controls');
    if (ctl && (MENU || lang !== 'en') && !document.getElementById('lang')) {
      // On a phone the controls share one row with the title, so the menu
      // shows a short name; the list itself is still one language per line.
      var narrow = window.matchMedia && matchMedia('(max-width: 700px)').matches;
      var opts = Object.keys(LANGS).map(function (k) { return '<option value="' + k + '"' + (k === lang ? ' selected' : '') + ' lang="' + k + '" title="' + LANGS[k].name + '">' + (narrow ? LANGS[k].short : LANGS[k].name) + '</option>'; }).join('');
      var sel = '<select id="lang" aria-label="' + L('Language') + '" data-no-i18n>' + opts + '</select>';
      ctl.insertAdjacentHTML('afterbegin', sel);
      document.getElementById('lang').addEventListener('change', function () {
        try { localStorage.setItem('sir-lang', this.value); } catch (e) {}
        var u = new URL(location.href); u.searchParams.set('lang', this.value); location.href = u.toString();
      });
    }
    // Every translation is made by machine and carries this notice for good:
    // the English page governs.
    if (lang !== 'en' && !document.getElementById('i18n-note')) {
      var m = document.querySelector('main') || document.body;
      var en = new URL(location.href); en.searchParams.set('lang', 'en');
      m.insertAdjacentHTML('beforebegin', '<p id="i18n-note" class="i18n-note" role="note">' + L('This page was translated by machine. Where it differs from the English page, the English page is correct.') + ' <a href="' + en.toString() + '" lang="en" dir="ltr">English</a></p>');
    }
    // Keep the chosen language when following a link to another page here.
    if (lang !== 'en') document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href]'); if (!a) return;
      var u = new URL(a.href, location.href);
      if (u.origin !== location.origin || u.searchParams.has('lang') || /\.(json|pdf|png|csv|docx|pptx)$/.test(u.pathname)) return;
      u.searchParams.set('lang', lang); a.href = u.toString();
    });
  };
  L.collected = function () { return { statics: Object.keys(statics), dynamic: Object.keys(seen) }; };
})();
