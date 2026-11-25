#!/usr/bin/env python3
"""The court cases on the revision, matter by matter, for india/courts/.

    python3 scripts/build_courts.py          # writes data/india/courts.json
    python3 scripts/build_courts.py --check  # fails if it is stale or a rule breaks

Reads data/india/disputes.json, which holds only the entries whose second
reading confirmed or corrected them, with the dated hearings ahead
(listings). Nothing here is typed: every date, claim, court and case number
on the page is an entry's own, and the page links each entry to its place on
india/disputes/.

How entries are grouped into a matter. The rules are conservative: two
entries go into one matter only where an entry says they are the same case
or that one is heard with, tagged with or connected to the other.

  1. Case numbers. Each entry's case field is read for case numbers
     (W.P.(C) No. 1089 of 2025, Diary No. 64196 of 2026, W.P. No. 31887 of
     2026 and the rest), keyed by court. A matter starts from one number.
     Another number joins it only through an entry, named in JOINED, whose
     case field names the new number beside a number or a phrase the matter
     already has. An entry whose numbers all belong to one matter is in it.
  2. Phrases. An entry with no case number is in a matter when its case
     field carries one of the matter's PHRASES, which are the words entries
     themselves use for that case, such as "in the West Bengal SIR matter".
  3. Links. An entry with no case number and no phrase is in a matter when
     LINKS names it, and the link is accepted only if the entry or a member
     cites the other by its entry number and both are before the same court.
  4. Related, never merged. An entry that names case numbers of two
     matters, that cites a member by its entry number, that a member cites,
     or that RELATED names with its reason, is listed under "related" and not
     in the case.

An entry that names a case number no matter holds, beside one a matter does,
fails the build, so a new connection is decided here and not by accident.
Every other entry with a case field, or in the courts section of the
disputes page, is listed under "Other cases", by court, with entries that
carry the same case field word for word kept together.

The parties are the bodies and parties the entries' tags name (tags.json),
and a case title in "X v. Y" form where TITLE_FROM names an entry whose case
field opens with one. A private person is never named here: the titles used
are those of organisations, public figures and the Commission.
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RES = os.path.join(ROOT, 'data', 'india', 'raw', 'disputes_research')
OUT = os.path.join(ROOT, 'data', 'india', 'courts.json')
LANGS = ('hi', 'ur', 'te', 'ta', 'bn')

# case numbers as the entries write them, to a key: type number/year
NUMBERS = [
    ('Suo Motu WP(C)', r'Suo Motu W\.P\.\(C\) No\. (\d+) of (\d{4})'),
    ('WP(C)', r'(?<!Motu )W\.P\.\s?\(C\)\s*(?:No\.\s*)?(\d+)(?: of |/)(\d{4})'),
    ('WP(Crl)', r'W\.P\.\s?\(Crl\.\)\s*(?:No\.\s*)?(\d+)(?: of |/)(\d{4})'),
    ('WP(C)', r'\bWP\(c\)\s*(\d+)/(\d{4})'),
    ('SLP(C)', r'\bSLP\(C\)\s*(?:No\.\s*)?(\d+)(?: of |/)(\d{4})'),
    ('WP', r'\bWrit Petition No\. (\d+) of (\d{4})'),
    ('Writ-A', r'\bWrit - A No\. (\d+) of (\d{4})'),
    ('WP', r'\bW\.P\. No\. (\d+) of (\d{4})'),
    ('WP', r'\bWP (\d+) of (\d{4})'),
    ('PIL', r'\bPIL No\. (\d+) of (\d{4})'),
    ('Crl.P', r'\bCRL\.P (\d+)/(\d{4})'),
    ('Crl.P', r'\bCrl\.P\. No\. (\d+) of (\d{4})'),
    ('Diary', r'\bDiary No\. (\d+) of (\d{4})'),
    ('IA', r'\bIA No\. (\d+) of (\d{4})'),
]
REF = re.compile(r'\b((?:court|form7|up|soft|protest|process)-\d+)\b')
# words by which an entry says two numbers are one proceeding
JOINING = re.compile(r'\b(?:heard with|tagged|connected|with|among them|batch|in W\.P\.|and IA No\.|and W\.P\. No\.)|\(Diary No\.')

# The matters, in the order the page lists them. "numbers" are keys as
# case_numbers() writes them, the first being where the matter starts.
MATTERS = [
    {'id': 'bihar', 'court': 'Supreme Court', 'states': ['Bihar'],
     'title': "The Bihar revision in the Supreme Court",
     't': {'hi': 'सुप्रीम कोर्ट में बिहार का पुनरीक्षण', 'ur': 'سپریم کورٹ میں بہار کی نظرثانی', 'te': 'సుప్రీంకోర్టులో బిహార్ సవరణ',
           'ta': 'உச்ச நீதிமன்றத்தில் பீகார் திருத்தம்', 'bn': 'সুপ্রিম কোর্টে বিহারের সংশোধন'},
     'numbers': ['WP(C) 640/2025', 'Diary 35785/2025', 'WP(C) 855/2025'],
     'phrases': ['Association for Democratic Reforms & Ors. v. Election Commission of India'],
     'title_from': 'court-03'},
    {'id': 'west-bengal', 'court': 'Supreme Court', 'states': ['West Bengal'],
     'title': "West Bengal's revision in the Supreme Court",
     't': {'hi': 'सुप्रीम कोर्ट में पश्चिम बंगाल का पुनरीक्षण', 'ur': 'سپریم کورٹ میں مغربی بنگال کی نظرثانی', 'te': 'సుప్రీంకోర్టులో పశ్చిమ బెంగాల్ సవరణ',
           'ta': 'உச்ச நீதிமன்றத்தில் மேற்கு வங்கத் திருத்தம்', 'bn': 'সুপ্রিম কোর্টে পশ্চিমবঙ্গের সংশোধন'},
     'numbers': ['WP(C) 1089/2025', 'WP(C) 129/2026', 'WP(C) 462/2026'],
     'phrases': ['in the West Bengal SIR matter']},
    {'id': 'wb-tribunals', 'court': 'Appellate tribunal (West Bengal)', 'states': ['West Bengal'],
     'title': "West Bengal's SIR appellate tribunals and the appeals before them",
     't': {'hi': 'पश्चिम बंगाल के एसआईआर अपीलीय न्यायाधिकरण और उनके सामने की अपीलें', 'ur': 'مغربی بنگال کے ایس آئی آر اپیلیٹ ٹریبیونل اور ان کے سامنے اپیلیں',
           'te': 'పశ్చిమ బెంగాల్ ఎస్ఐఆర్ అప్పీలేట్ ట్రైబ్యునళ్లు, వాటి ముందున్న అప్పీళ్లు', 'ta': 'மேற்கு வங்க எஸ்ஐஆர் மேல்முறையீட்டுத் தீர்ப்பாயங்களும் அவற்றின் முன் உள்ள மேல்முறையீடுகளும்',
           'bn': 'পশ্চিমবঙ্গের এসআইআর আপিল ট্রাইব্যুনাল ও সেগুলির সামনে থাকা আপিল'},
     # a subject, many cases: the page says so beside the matter
     'note': "This matter brings together the entries on the appellate tribunals that hear appeals in West Bengal's revision, on the appeals before them and on how the tribunals work. Each appeal before a tribunal is a case of its own, and the entries are kept together because they describe their subject in the same words.",
     'nt': {'hi': 'यह मामला उन प्रविष्टियों को एक साथ रखता है जो पश्चिम बंगाल के पुनरीक्षण में अपीलें सुनने वाले अपीलीय न्यायाधिकरणों, उनके सामने की अपीलों और न्यायाधिकरणों के कामकाज के बारे में हैं। न्यायाधिकरण के सामने हर अपील अपना अलग मुक़दमा है, और ये प्रविष्टियाँ इसलिए साथ रखी गई हैं कि वे अपने विषय को एक ही शब्दों में बताती हैं।',
            'ur': 'یہ معاملہ اُن اندراجات کو یکجا کرتا ہے جو مغربی بنگال کی نظرثانی میں اپیلیں سننے والے اپیلیٹ ٹریبیونلز، ان کے سامنے کی اپیلوں اور ٹریبیونلز کے کام کاج کے بارے میں ہیں۔ ٹریبیونل کے سامنے ہر اپیل اپنا الگ مقدمہ ہے، اور یہ اندراجات اس لیے ساتھ رکھے گئے ہیں کہ وہ اپنے موضوع کو ایک ہی الفاظ میں بیان کرتے ہیں۔',
            'te': 'పశ్చిమ బెంగాల్ సవరణలో అప్పీళ్లను విచారించే అప్పీలేట్ ట్రైబ్యునళ్లు, వాటి ముందున్న అప్పీళ్లు, ట్రైబ్యునళ్ల పనితీరు గురించిన నమోదులను ఈ వ్యవహారం ఒకచోట చేరుస్తుంది. ట్రైబ్యునల్ ముందున్న ప్రతి అప్పీలు ఒక ప్రత్యేక కేసు. ఈ నమోదులు తమ విషయాన్ని ఒకే మాటల్లో వివరిస్తాయి కాబట్టి వాటిని కలిపి ఉంచారు.',
            'ta': 'மேற்கு வங்கத் திருத்தத்தில் மேல்முறையீடுகளை விசாரிக்கும் மேல்முறையீட்டுத் தீர்ப்பாயங்கள், அவற்றின் முன் உள்ள மேல்முறையீடுகள், தீர்ப்பாயங்களின் செயல்பாடு பற்றிய பதிவுகளை இந்த விவகாரம் ஒன்றாகத் தொகுக்கிறது. தீர்ப்பாயத்தின் முன் உள்ள ஒவ்வொரு மேல்முறையீடும் தனி வழக்கு. இந்தப் பதிவுகள் தங்கள் பொருளை ஒரே சொற்களில் விவரிப்பதால் ஒன்றாக வைக்கப்பட்டுள்ளன.',
            'bn': 'এই বিষয়ে রাখা হয়েছে পশ্চিমবঙ্গের সংশোধনে আপিল শোনা আপিল ট্রাইব্যুনাল, সেগুলির সামনে থাকা আপিল এবং ট্রাইব্যুনালের কাজকর্ম নিয়ে এন্ট্রিগুলি। ট্রাইব্যুনালের সামনে প্রতিটি আপিল একটি আলাদা মামলা। এন্ট্রিগুলি নিজেদের বিষয় একই কথায় বর্ণনা করে বলে সেগুলি একসঙ্গে রাখা হয়েছে।'},
     'numbers': [],
     'phrases': ["West Bengal's SIR appellate tribunals"],
     'page': 'westbengal/tribunals/'},
    {'id': 'functioning', 'court': 'Supreme Court', 'states': ['India'],
     'title': "The petitions on the Commission's functioning",
     't': {'hi': 'आयोग के कामकाज पर याचिकाएँ', 'ur': 'کمیشن کے کام کاج پر درخواستیں', 'te': 'సంఘం పనితీరుపై పిటిషన్లు',
           'ta': 'ஆணையத்தின் செயல்பாடு குறித்த மனுக்கள்', 'bn': 'কমিশনের কাজকর্ম নিয়ে আবেদন'},
     'numbers': ['WP(C) 1246/2026', 'WP(C) 1351/2026', 'Diary 64196/2026', 'WP(Crl) 401/2026'],
     'phrases': ['a writ of quo warranto against the Chief Election Commissioner'],
     # no case title: the lead petition, W.P.(C) No. 1246 of 2026, is a
     # private person's, and the title of one petition in the batch is not
     # the matter's
     },
    {'id': 'delhi', 'court': 'Supreme Court', 'states': ['Delhi'],
     'title': "Delhi's revision in the Supreme Court",
     't': {'hi': 'सुप्रीम कोर्ट में दिल्ली का पुनरीक्षण', 'ur': 'سپریم کورٹ میں دہلی کی نظرثانی', 'te': 'సుప్రీంకోర్టులో ఢిల్లీ సవరణ',
           'ta': 'உச்ச நீதிமன்றத்தில் டெல்லி திருத்தம்', 'bn': 'সুপ্রিম কোর্টে দিল্লির সংশোধন'},
     'numbers': ['WP(C) 1188/2026', 'IA 317050/2026'],
     'phrases': [],
     'links': {'court-30': 'court-54'},
     'title_from': 'court-86'},
    {'id': 'mustafabad', 'court': 'Supreme Court', 'states': ['Delhi'],
     'title': 'Form 7 objections in Mustafabad, in the Supreme Court',
     't': {'hi': 'सुप्रीम कोर्ट में मुस्तफ़ाबाद की फ़ॉर्म 7 आपत्तियाँ', 'ur': 'سپریم کورٹ میں مصطفیٰ آباد کے فارم 7 اعتراضات', 'te': 'సుప్రీంకోర్టులో ముస్తఫాబాద్ ఫారం 7 అభ్యంతరాలు',
           'ta': 'உச்ச நீதிமன்றத்தில் முஸ்தபாபாத் படிவம் 7 ஆட்சேபனைகள்', 'bn': 'সুপ্রিম কোর্টে মুস্তাফাবাদের ফর্ম 7 আপত্তি'},
     'numbers': ['WP(C) 1493/2026'],
     'phrases': [],
     'links': {'court-81': 'court-85'},
     'title_from': 'court-85'},
    {'id': 'maharashtra', 'court': 'Supreme Court', 'states': ['Maharashtra'],
     'title': "Deletions in Maharashtra's revision, in the Supreme Court",
     't': {'hi': 'सुप्रीम कोर्ट में महाराष्ट्र के पुनरीक्षण में हटाए गए नाम', 'ur': 'سپریم کورٹ میں مہاراشٹر کی نظرثانی میں حذف کیے گئے نام', 'te': 'సుప్రీంకోర్టులో మహారాష్ట్ర సవరణలో తొలగించిన పేర్లు',
           'ta': 'உச்ச நீதிமன்றத்தில் மகாராஷ்டிர திருத்தத்தில் நீக்கப்பட்ட பெயர்கள்', 'bn': 'সুপ্রিম কোর্টে মহারাষ্ট্রের সংশোধনে বাদ দেওয়া নাম'},
     'numbers': ['WP(C) 1330/2026'],
     'phrases': []},
    {'id': 'up-kerala-chhattisgarh', 'court': 'Supreme Court', 'states': ['Uttar Pradesh', 'Kerala', 'Chhattisgarh'],
     'title': 'The revisions in Uttar Pradesh, Kerala and Chhattisgarh, in the Supreme Court',
     't': {'hi': 'सुप्रीम कोर्ट में उत्तर प्रदेश, केरल और छत्तीसगढ़ के पुनरीक्षण', 'ur': 'سپریم کورٹ میں اتر پردیش، کیرالہ اور چھتیس گڑھ کی نظرثانیاں',
           'te': 'సుప్రీంకోర్టులో ఉత్తర ప్రదేశ్, కేరళ, ఛత్తీస్‌గఢ్ సవరణలు', 'ta': 'உச்ச நீதிமன்றத்தில் உத்தரப் பிரதேசம், கேரளா, சத்தீஸ்கர் திருத்தங்கள்',
           'bn': 'সুপ্রিম কোর্টে উত্তরপ্রদেশ, কেরল ও ছত্তিশগড়ের সংশোধন'},
     'numbers': [],
     'phrases': ['the SIR matters concerning Uttar Pradesh']},
    {'id': 'karnataka-form7', 'court': 'Karnataka High Court', 'states': ['Karnataka'],
     'title': 'Petitions against the FIRs over Form 7 applications, in the Karnataka High Court',
     't': {'hi': 'कर्नाटक हाई कोर्ट में फ़ॉर्म 7 आवेदनों पर दर्ज एफ़आईआर के ख़िलाफ़ याचिकाएँ', 'ur': 'کرناٹک ہائی کورٹ میں فارم 7 درخواستوں پر درج ایف آئی آر کے خلاف درخواستیں',
           'te': 'కర్ణాటక హైకోర్టులో ఫారం 7 దరఖాస్తులపై ఎఫ్ఐఆర్‌లకు వ్యతిరేకంగా పిటిషన్లు', 'ta': 'கர்நாடக உயர் நீதிமன்றத்தில் படிவம் 7 விண்ணப்பங்கள் மீதான எஃப்ஐஆர்களை எதிர்த்த மனுக்கள்',
           'bn': 'কর্ণাটক হাইকোর্টে ফর্ম 7 আবেদন নিয়ে এফআইআরের বিরুদ্ধে আবেদন'},
     'numbers': ['WP 31887/2026', 'WP 31893/2026', 'WP 32308/2026', 'WP 32215/2026', 'Crl.P 15507/2026'],
     'phrases': [],
     'note': "These are separate petitions by BJP booth agents, each against its own FIR. They are kept together because one entry reports the High Court's orders in all five.",
     'nt': {'hi': 'ये भाजपा के बूथ एजेंटों की अलग-अलग याचिकाएँ हैं, हर एक अपनी एफ़आईआर के ख़िलाफ़। इन्हें साथ इसलिए रखा गया है कि एक प्रविष्टि पाँचों में हाई कोर्ट के आदेशों की ख़बर देती है।',
            'ur': 'یہ بی جے پی کے بوتھ ایجنٹوں کی الگ الگ درخواستیں ہیں، ہر ایک اپنی ایف آئی آر کے خلاف۔ انہیں اس لیے ساتھ رکھا گیا ہے کہ ایک اندراج پانچوں میں ہائی کورٹ کے احکامات کی خبر دیتا ہے۔',
            'te': 'ఇవి బీజేపీ బూత్ ఏజెంట్ల వేర్వేరు పిటిషన్లు, ఒక్కొక్కటి దాని సొంత ఎఫ్ఐఆర్‌కు వ్యతిరేకంగా. ఒక నమోదు ఈ ఐదింటిలోనూ హైకోర్టు ఉత్తర్వులను నివేదిస్తుంది కాబట్టి వాటిని కలిపి ఉంచారు.',
            'ta': 'இவை பாஜக வாக்குச்சாவடி முகவர்களின் தனித்தனி மனுக்கள், ஒவ்வொன்றும் அதற்குரிய எஃப்ஐஆருக்கு எதிரானது. ஒரு பதிவு ஐந்திலும் உயர் நீதிமன்றத்தின் உத்தரவுகளைத் தெரிவிப்பதால் இவை ஒன்றாக வைக்கப்பட்டுள்ளன.',
            'bn': 'এগুলি বিজেপির বুথ এজেন্টদের আলাদা আলাদা আবেদন, প্রতিটি নিজের এফআইআরের বিরুদ্ধে। একটি এন্ট্রি পাঁচটিতেই হাইকোর্টের আদেশের খবর দেয় বলে এগুলি একসঙ্গে রাখা হয়েছে।'}},
    {'id': 'bengaluru-polls', 'court': 'Supreme Court', 'states': ['Karnataka'],
     'title': "The elections to Bengaluru's five city corporations, in the Supreme Court",
     't': {'hi': 'सुप्रीम कोर्ट में बेंगलुरु के पाँच नगर निगमों के चुनाव', 'ur': 'سپریم کورٹ میں بنگلورو کی پانچ میونسپل کارپوریشنوں کے انتخابات',
           'te': 'సుప్రీంకోర్టులో బెంగళూరు ఐదు నగర పాలక సంస్థల ఎన్నికలు', 'ta': 'உச்ச நீதிமன்றத்தில் பெங்களூருவின் ஐந்து மாநகராட்சித் தேர்தல்கள்',
           'bn': 'সুপ্রিম কোর্টে বেঙ্গালুরুর পাঁচটি পুর নিগমের নির্বাচন'},
     'numbers': [],
     'phrases': ['the five city corporations under the Greater Bengaluru Authority']},
    {'id': 'goa-form8', 'court': 'Bombay High Court at Goa', 'states': ['Goa'],
     'title': "A family's petition on deletion after Form 8, in the Bombay High Court at Goa",
     't': {'hi': 'बॉम्बे हाई कोर्ट, गोवा में फ़ॉर्म 8 के बाद नाम हटाए जाने पर एक परिवार की याचिका', 'ur': 'بمبئی ہائی کورٹ، گوا میں فارم 8 کے بعد نام حذف کیے جانے پر ایک خاندان کی درخواست',
           'te': 'బాంబే హైకోర్టు, గోవాలో ఫారం 8 తర్వాత పేర్ల తొలగింపుపై ఒక కుటుంబం పిటిషన్', 'ta': 'பம்பாய் உயர் நீதிமன்றம், கோவாவில் படிவம் 8க்குப் பின் பெயர் நீக்கம் குறித்து ஒரு குடும்பத்தின் மனு',
           'bn': 'বম্বে হাইকোর্ট, গোয়ায় ফর্ম 8-এর পরে নাম বাদ দেওয়া নিয়ে একটি পরিবারের আবেদন'},
     'numbers': ['WP 732/2026'],
     'phrases': []},
    {'id': 'journalists', 'court': 'Supreme Court', 'states': ['Delhi'],
     'title': 'The journalists covering the October protests, in the Supreme Court',
     't': {'hi': 'सुप्रीम कोर्ट में अक्टूबर के विरोध प्रदर्शनों की रिपोर्टिंग करने वाले पत्रकार', 'ur': 'سپریم کورٹ میں اکتوبر کے احتجاج کی رپورٹنگ کرنے والے صحافی',
           'te': 'సుప్రీంకోర్టులో అక్టోబర్ నిరసనలను కవర్ చేసిన జర్నలిస్టులు', 'ta': 'உச்ச நீதிமன்றத்தில் அக்டோபர் போராட்டங்களைச் செய்தியாக்கிய பத்திரிகையாளர்கள்',
           'bn': 'সুপ্রিম কোর্টে অক্টোবরের প্রতিবাদের খবর করা সাংবাদিকেরা'},
     'numbers': ['WP(C) 1361/2026'],
     'phrases': [],
     'title_from': 'court-83'},
    {'id': 'traders', 'court': 'Supreme Court', 'states': ['Delhi'],
     'title': "The traders' petition on the October protests, in the Supreme Court",
     't': {'hi': 'सुप्रीम कोर्ट में अक्टूबर के विरोध प्रदर्शनों पर व्यापारियों की याचिका', 'ur': 'سپریم کورٹ میں اکتوبر کے احتجاج پر تاجروں کی درخواست',
           'te': 'సుప్రీంకోర్టులో అక్టోబర్ నిరసనలపై వ్యాపారుల పిటిషన్', 'ta': 'உச்ச நீதிமன்றத்தில் அக்டோபர் போராட்டங்கள் குறித்த வணிகர்களின் மனு',
           'bn': 'সুপ্রিম কোর্টে অক্টোবরের প্রতিবাদ নিয়ে ব্যবসায়ীদের আবেদন'},
     'numbers': ['WP(C) 1395/2026'],
     'phrases': [],
     'links': {'protest-47': 'court-88'},
     'title_from': 'court-88'},
    {'id': 'march', 'court': 'Supreme Court', 'states': ['India'],
     'title': "The advocates' petition on the march of 12 October, in the Supreme Court",
     't': {'hi': 'सुप्रीम कोर्ट में 12 अक्टूबर के मार्च पर वकीलों की याचिका', 'ur': 'سپریم کورٹ میں 12 اکتوبر کے مارچ پر وکیلوں کی درخواست',
           'te': 'సుప్రీంకోర్టులో అక్టోబర్ 12 మార్చ్‌పై న్యాయవాదుల పిటిషన్', 'ta': 'உச்ச நீதிமன்றத்தில் அக்டோபர் 12 பேரணி குறித்த வழக்கறிஞர்களின் மனு',
           'bn': 'সুপ্রিম কোর্টে 12 অক্টোবরের মিছিল নিয়ে আইনজীবীদের আবেদন'},
     'numbers': ['WP(C) 1360/2026', 'Diary 64394/2026'],
     'phrases': [],
     'links': {'court-62': 'court-44'}},
    {'id': 'detention', 'court': 'Supreme Court', 'states': ['Delhi'],
     'title': 'The detention of protesters in October, in the Supreme Court',
     't': {'hi': 'सुप्रीम कोर्ट में अक्टूबर में प्रदर्शनकारियों को हिरासत में लिया जाना', 'ur': 'سپریم کورٹ میں اکتوبر میں مظاہرین کی حراست',
           'te': 'సుప్రీంకోర్టులో అక్టోబర్‌లో నిరసనకారుల నిర్బంధం', 'ta': 'உச்ச நீதிமன்றத்தில் அக்டோபரில் போராட்டக்காரர்கள் தடுத்து வைக்கப்பட்டது',
           'bn': 'সুপ্রিম কোর্টে অক্টোবরে প্রতিবাদকারীদের আটক'},
     'numbers': [],
     'phrases': ['petitions alleging illegal detention of protesters']},
    {'id': 'pilibhit', 'court': "Magistrate's court", 'states': ['Uttar Pradesh'],
     'title': 'An application for an FIR against the District Election Officer of Pilibhit',
     't': {'hi': 'पीलीभीत के ज़िला निर्वाचन अधिकारी के ख़िलाफ़ एफ़आईआर के लिए आवेदन', 'ur': 'پیلی بھیت کے ضلع الیکشن افسر کے خلاف ایف آئی آر کے لیے درخواست',
           'te': 'పిలిభిత్ జిల్లా ఎన్నికల అధికారిపై ఎఫ్ఐఆర్ కోసం దరఖాస్తు', 'ta': 'பிலிபித் மாவட்டத் தேர்தல் அலுவலர் மீது எஃப்ஐஆர் கோரும் விண்ணப்பம்',
           'bn': 'পিলিভিতের জেলা নির্বাচন আধিকারিকের বিরুদ্ধে এফআইআরের আবেদন'},
     'numbers': [],
     'phrases': ["Kumud Gangwar's application"]},
]
# A number beyond a matter's first joins it through this entry, whose case
# field names it beside a number or phrase the matter already has.
JOINED = {
    'Diary 35785/2025': 'court-02', 'WP(C) 855/2025': 'court-06',
    'WP(C) 129/2026': 'court-15', 'WP(C) 462/2026': 'court-20',
    'WP(C) 1351/2026': 'court-53', 'Diary 64196/2026': 'court-42', 'WP(Crl) 401/2026': 'court-52',
    'IA 317050/2026': 'court-60', 'Diary 64394/2026': 'court-44',
    'WP 31893/2026': 'form7-48', 'WP 32308/2026': 'form7-75', 'WP 32215/2026': 'form7-75', 'Crl.P 15507/2026': 'form7-75',
}
# Entries listed as related by hand, each with the reason it is not in the case.
RELATED = {
    'maharashtra': {'court-46': 'This entry concerns deletions in Maharashtra\'s revision in the Supreme Court and gives no case number, so it is not shown to be the same petition.'},
    'karnataka-form7': {'form7-49': 'This entry concerns a petition over FIRs on Form 7 applications in the Karnataka High Court at Dharwad, and does not say it is heard with these petitions.'},
}
# The page links each matter's entries; these keys are what the page shows.
KEEP = ('date', 'state', 'place', 'court', 'case', 'kind', 'outlet', 'url', 'claim', 'response', 'headline', 'section')


def order(i, it):
    """Date order, then the entry's number, so court-100 follows court-99."""
    p, _, k = i.rpartition('-')
    return (it['date'], p, int(k) if k.isdigit() else 0, i)


def case_numbers(text):
    out = []
    for kind, rx in NUMBERS:
        for m in re.finditer(rx, text or ''):
            k = '%s %s/%s' % (kind, m.group(1), m.group(2))
            if k not in out:
                out.append(k)
    return out


def refs(it):
    return set(REF.findall((it.get('case') or '') + ' ' + (it.get('claim') or ''))) - {it['id']}


def verified_status():
    """The second reading's verdict on every entry the research files hold."""
    st = {}
    for f in os.listdir(RES):
        if f.startswith('verified_') and f.endswith('.json'):
            d = json.load(open(os.path.join(RES, f), encoding='utf-8'))
            for k, v in d.get('items', d).items():
                if isinstance(v, dict):
                    st[k] = v.get('status')
    return st


def fail(msg):
    raise SystemExit('FAIL - ' + msg)


def build():
    D = json.load(open(os.path.join(ROOT, 'data', 'india', 'disputes.json'), encoding='utf-8'))
    ALL = {i['id']: i for s in D['sections'] for i in s['items']}
    ST = verified_status()

    def confirmed(i):
        # process-NN entries come from the process page's checked reports
        return i in ALL and (i.startswith('process-') or ST.get(i) in ('confirmed', 'corrected'))

    # each key a court can hold, to its matter
    key_of = {}
    for m in MATTERS:
        if not (m['numbers'] or m['phrases']):
            fail('matter %s has neither a case number nor a phrase' % m['id'])
        for k in m['numbers']:
            ck = (m['court'], k)
            if ck in key_of:
                fail('%s is in two matters' % k)
            key_of[ck] = m['id']
    M = {m['id']: m for m in MATTERS}
    members = {m['id']: [] for m in MATTERS}
    where = {}

    def put(i, mid):
        if i in where and where[i] != mid:
            fail('%s would be in two matters, %s and %s' % (i, where[i], mid))
        where[i] = mid
        if i not in members[mid]:
            members[mid].append(i)

    two = {}  # entries naming numbers of two matters
    for i, it in ALL.items():
        nums = case_numbers(it['case'])
        if not nums:
            continue
        hit = {key_of.get((it['court'], k)) for k in nums} - {None}
        loose = [k for k in nums if (it['court'], k) not in key_of]
        if hit and loose:
            fail('%s names %s beside a matter\'s number and no matter holds it: add it to the matter, with JOINED, or decide' % (i, ', '.join(loose)))
        if len(hit) == 1:
            put(i, hit.pop())
        elif len(hit) > 1:
            two[i] = sorted(hit)
    # a number joins a matter only through an entry that names it with the matter
    for m in MATTERS:
        for k in m['numbers'][1:]:
            j = JOINED.get(k)
            if not j or j not in ALL:
                fail('%s in %s has no entry that joins it' % (k, m['id']))
            nums = case_numbers(ALL[j]['case'])
            others = [x for x in nums if x != k and x in m['numbers']]
            phrase = any(p in ALL[j]['case'] for p in m['phrases'])
            if k not in nums or not (others or phrase) or not JOINING.search(ALL[j]['case']):
                fail('%s does not name %s beside %s\'s other numbers or phrase' % (j, k, m['id']))
    # phrases, for entries with no case number
    for m in MATTERS:
        for p in m['phrases']:
            hits = [i for i, it in ALL.items() if p in (it['case'] or '')]
            if not hits:
                fail('the phrase %r of %s matches no entry' % (p, m['id']))
            for i in hits:
                if not case_numbers(ALL[i]['case']):
                    put(i, m['id'])
    # links: the entry or a member cites the other, before the same court
    for m in MATTERS:
        for i, via in m.get('links', {}).items():
            if i not in ALL or via not in ALL:
                fail('link %s or %s is not an entry on the disputes page' % (i, via))
            if where.get(via) != m['id']:
                fail('%s links %s through %s, which is not in the matter' % (m['id'], i, via))
            if case_numbers(ALL[i]['case']):
                fail('%s carries a case number and is linked by hand' % i)
            if not (via in refs(ALL[i]) or i in refs(ALL[via])):
                fail('neither %s nor %s cites the other' % (i, via))
            if ALL[i]['court'] != ALL[via]['court']:
                fail('%s and %s are before different courts' % (i, via))
            put(i, m['id'])
    for mid, its in members.items():
        if not its:
            fail('matter %s has no entry' % mid)
    # related: never merged
    related = {m['id']: {} for m in MATTERS}
    for i, ms in two.items():
        for mid in ms:
            related[mid][i] = 'two'
    for m in MATTERS:
        mine = set(members[m['id']])
        for i, it in ALL.items():
            if i in mine:
                continue
            if refs(it) & mine or any(i in refs(ALL[x]) for x in mine):
                related[m['id']].setdefault(i, 'cites')
        for i, why in RELATED.get(m['id'], {}).items():
            if i not in ALL or i in mine:
                fail('related %s of %s is not an entry, or is in the case' % (i, m['id']))
            related[m['id']][i] = why
    # other cases: every entry with a case field, or in the courts section,
    # that no matter holds, kept together only where the case field is the same
    courts_sec = {i['id'] for s in D['sections'] if s['id'] == 'courts' for i in s['items']}
    other, by_case = {}, {}
    for i, it in ALL.items():
        if i in where or not (it['case'] or i in courts_sec):
            continue
        key = (it['court'], it['case'] or i)
        by_case.setdefault(key, []).append(i)
    for (court, _), ids in by_case.items():
        ids.sort(key=lambda x: order(x, ALL[x]))
        other.setdefault(court, []).append({'items': ids, 'numbers': case_numbers(ALL[ids[0]]['case'])})
    # every entry shown, from the disputes page, confirmed
    shown = set(where) | {i for r in related.values() for i in r} | {i for v in other.values() for c in v for i in c['items']}
    for i in sorted(shown):
        if not confirmed(i):
            fail('%s is on the courts page and is not a confirmed entry of the disputes page' % i)
    listings = {x['id']: x for x in D.get('listings', [])}
    for x in listings.values():
        if x['disputes_id'] not in ALL:
            fail('listing %s names no entry' % x['id'])

    def title(m):
        f = m.get('title_from')
        if not f:
            return ''
        c = ALL[f]['case']
        v = c.find(' v. ')
        t = c[:c.find(',', v) if c.find(',', v) > 0 else len(c)].strip() if v > 0 else ''
        if not t:
            fail('%s, named as the title of %s, opens with no "X v. Y" title' % (f, m['id']))
        return t

    out = []
    for m in MATTERS:
        ids = sorted(members[m['id']], key=lambda x: order(x, ALL[x]))
        docs = [i for i in ids if ALL[i]['kind'] == 'primary']
        nums = []
        for k in m['numbers']:
            src = next((i for i in ids if k in case_numbers(ALL[i]['case'])), None)
            if not src:
                fail('no entry of %s names %s' % (m['id'], k))
            nums.append({'key': k, 'item': src})
        actors = []
        for i in ids:
            for a in ALL[i]['actors']:
                if a not in actors:
                    actors.append(a)
        for lang in LANGS:
            if not m['t'].get(lang):
                fail('matter %s has no %s title' % (m['id'], lang))
        if m.get('note') and any(not m.get('nt', {}).get(lang) for lang in LANGS):
            fail('matter %s has a note without all its translations' % m['id'])
        text = ' '.join([m['title'], m.get('note', '')] + list(m['t'].values()) + list(m.get('nt', {}).values()) + list(RELATED.get(m['id'], {}).values()))
        if '—' in text or '–' in text or re.search('[০-৯०-९٠-٩۰-۹௦-௯౦-౯]', text):
            fail('matter %s carries a dash or an Indic digit' % m['id'])
        rel = related[m['id']]
        out.append({
            'id': m['id'], 'title': m['title'], 't': m['t'], 'court': m['court'], 'states': m['states'],
            'case_title': title(m), 'title_from': m.get('title_from', ''), 'page': m.get('page', ''),
            'note': m.get('note', ''), 'nt': m.get('nt', {}),
            'numbers': nums, 'actors': actors, 'items': ids,
            'first': ALL[ids[0]]['date'], 'last': ALL[ids[-1]]['date'],
            'latest': ids[-1], 'latest_document': docs[-1] if docs else '',
            'listings': sorted([x for x in listings if listings[x]['disputes_id'] in ids], key=lambda x: (listings[x]['date'], x)),
            'related': [{'id': i, 'why': rel[i]} for i in sorted(rel, key=lambda x: order(x, ALL[x]))],
            'related_listings': sorted([x for x in listings if listings[x]['disputes_id'] in rel], key=lambda x: (listings[x]['date'], x)),
        })
    other_out = []
    for court in sorted(other, key=lambda c: (c == '', c != 'Supreme Court', c)):
        cases = sorted(other[court], key=lambda c: order(c['items'][-1], ALL[c['items'][-1]]), reverse=True)
        for c in cases:
            c['listings'] = sorted([x for x in listings if listings[x]['disputes_id'] in c['items']], key=lambda x: (listings[x]['date'], x))
        other_out.append({'court': court, 'cases': cases})
    items = {i: {k: ALL[i].get(k, '') for k in KEEP} for i in sorted(shown)}
    used_l = {x for m in out for x in m['listings'] + m['related_listings']} | {x for o in other_out for c in o['cases'] for x in c['listings']}
    n_in = sum(len(m['items']) for m in out)
    return {
        'matters': out,
        'other': other_out,
        'items': items,
        'listings': {x: listings[x] for x in sorted(used_l)},
        'counts': {'matters': len(out), 'in_matters': n_in, 'other_cases': sum(len(o['cases']) for o in other_out),
                   'other_items': sum(len(c['items']) for o in other_out for c in o['cases']),
                   'courts': len({m['court'] for m in out} | {o['court'] for o in other_out if o['court']}),
                   'first': min(it['date'] for it in items.values()), 'last': max(it['date'] for it in items.values())},
    }


def main():
    d = build()
    text = json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n'
    if '--check' in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != text:
            raise SystemExit('FAIL - stale: data/india/courts.json')
        print('courts current: %d matters, %d entries in them, %d other cases' % (d['counts']['matters'], d['counts']['in_matters'], d['counts']['other_cases']))
        return
    open(OUT, 'w', encoding='utf-8').write(text)
    c = d['counts']
    print('%d matters holding %d entries, %d other cases (%d entries) before %d courts' % (c['matters'], c['in_matters'], c['other_cases'], c['other_items'], c['courts']))


if __name__ == '__main__':
    main()
