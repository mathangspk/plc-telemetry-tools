import socket, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
s.connect(('10.2.3.4', 49870))

def ru(m):
    d=b''
    while m not in d:
        try:
            c=s.recv(4096)
            if not c: break
            d+=c
        except: break
    return d.decode('utf-8',errors='ignore')

def ex(cmd):
    s.sendall((cmd+'\n').encode('utf-8'))
    r=ru(b'|>')
    try:
        si=r.find('{');ei=r.rfind('}')
        if si==-1 and r.find('[')!=-1: si=r.find('[');ei=r.rfind(']')
        if si!=-1 and ei!=-1: return json.loads(r[si:ei+1])
    except: pass
    return r.strip()

def get_names(path):
    r=ex(path+' describe -children')
    if not isinstance(r,dict): return [],0,0
    op=r.get('op-children',[])
    nop=r.get('nop-children',[])
    names=[]
    for c in op+nop:
        if isinstance(c,dict):
            idt=c.get('identity','')
            names.append(idt.split('/')[-1].split('.')[-1])
        elif isinstance(c,str): names.append(c)
    return names,len(op),len(nop)

ru(b'>')
print('CONNECTED')

# Quick burst - all subsystems in one session
subs = ['System.BMSAB','System.Steer','System.ChargerABC','System.Secondary',
        'System.ProgMovCntrl','System.TMS','System.Travel','System.Lift',
        'CANBusDrive','System.Spreader','System.SystemState']

for sub in subs:
    try:
        names,op,nop = get_names(sub)
        print('%s: %d op, %d nop -> %s' % (sub, op, nop, ','.join(sorted(names))[:200]))
    except Exception as e:
        print('%s: ERROR %s' % (sub, str(e)))
        break

s.close()
print('DONE')
