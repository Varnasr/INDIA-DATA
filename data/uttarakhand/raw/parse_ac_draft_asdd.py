import re,subprocess,csv,sys
t=subprocess.run(['pdftotext','-layout',sys.argv[1],'-'],capture_output=True,text=True).stdout
cats=['agegap_lt15','agegap_gt50','grandparent_lt40','progeny_gt6','progeny_agediff_lt9m','rel_name_var_progeny','self_name_var','rel_name_var_self','no_mapping']
hdr=['level','ac','name','district','ps','draft','anomalies','anomalies_pct']
for c in cats: hdr+= [c,c+'_pct']
hdr+=['asdd_deleted','service_electors']
rows=[];seen=set();dist=None;pending=[]
for line in t.splitlines():
    m=re.match(r'^\s*(\d+)\s+-\s+([A-Za-z.() ]+?)\s{2,}(\d.*)$',line)
    m2=re.match(r'^\s*(\d+)-([A-Za-z. ]+)-?\s+(\d.*)$',line)
    g=re.match(r'^\s*Grand Total-\s+(\d.*)$',line)
    if g: nums=g.group(1).split(); key=('state',)
    elif m: nums=m.group(3).split(); key=('ac',int(m.group(1)),m.group(2).strip())
    elif m2: nums=m2.group(3).split(); key=('district',int(m2.group(1)),m2.group(2).strip())
    else: continue
    nums=[int(x) for x in nums]
    assert len(nums)==24,(line,len(nums))
    if key in seen: continue
    seen.add(key)
    if key[0]=='ac': pending.append((key,nums))
    elif key[0]=='district':
        for k,n in pending: rows.append(['ac',k[1],k[2],key[2]]+n)
        pending=[]; rows.append(['district','',key[2],key[2]]+nums)
    else: rows.append(['state','','Uttarakhand','']+nums)
w=csv.writer(open(sys.argv[2],'w',newline='')); w.writerow(hdr); w.writerows(rows)
print(len(rows))
