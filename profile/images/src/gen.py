import math, random, subprocess, sys, os
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
TMP = os.path.join(OUT, "src"); os.makedirs(TMP, exist_ok=True)

MARK = '''<g transform="translate(-212.74741,-257.60345)">
<path fill="#b8cee0" d="m 312.18676,363.65149 c 12.17995,0.008 22.04788,9.88627 22.04217,22.06617 -0.008,12.17069 -9.87133,22.03533 -22.04217,22.04274 h -63.26499 -3.66251 -0.26154 -15.61028 c -6.71517,0 -12.28234,-5.57227 -12.28234,-12.28834 v -19.53211 c 0,-6.71611 5.56717,-12.28846 12.28234,-12.28846 h 15.68651 0.19351 3.65681 z m -63.26499,10.71262 h -15.84015 -3.69777 c -0.95573,0 -1.59289,0.60987 -1.59289,1.57584 v 19.53211 c 0,0.96483 0.62578,1.56978 1.59289,1.56978 h 3.69777 15.84015 c 0.95573,0 1.57013,-0.60415 1.57013,-1.56978 v -19.53211 c 0,-0.96484 -0.60302,-1.57584 -1.57013,-1.57584 z"/>
<path fill="#55d43f" d="m 274.68674,297.49959 v 0.23093 c -0.42096,0.0227 -0.71679,-0.21959 -1.13775,-0.19805 -28.09516,1.94801 -27.01883,43.56325 1.13775,44.0592 h 37.47614 c 24.37122,-0.008 44.13328,19.74773 44.12984,44.1196 -0.29594,21.40207 -17.08713,36.2388 -31.03287,50.57266 -19.93047,20.78763 10.39702,51.11762 31.18764,31.18783 l 66.16517,-66.16642 c 8.60958,-8.61343 8.60958,-22.57444 0,-31.18787 l -66.16517,-66.16645 c -4.13813,-4.13311 -9.74623,-6.45427 -15.59554,-6.45313 z"/>
</g>'''
# mark spans roughly x 4..201, y 40..225 in its own frame -> centre (102,132), size ~200
def mark(cx, cy, size, shadow=True):
    s = size/200.0
    t = f'translate({cx-102*s:.2f},{cy-132*s:.2f}) scale({s:.4f})'
    sh = f'<g transform="translate({4*s:.2f},{6*s:.2f}) {t}" opacity="0.35" filter="url(#blur)">{MARK.replace("#b8cee0","#000").replace("#55d43f","#000")}</g>' if shadow else ''
    return sh + f'<g transform="{t}">{MARK}</g>'

def defs(w, h, cx=0.3, cy=0.45):
    return f'''<defs>
<radialGradient id="bg" cx="{cx*w}" cy="{cy*h}" r="{0.75*w}" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#566f84"/><stop offset="0.55" stop-color="#2b3845"/><stop offset="1" stop-color="#161d24"/></radialGradient>
<linearGradient id="fadeX" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.15" stop-color="#fff" stop-opacity="1"/><stop offset="0.85" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="fade"><rect width="{w}" height="{h}" fill="url(#fadeX)"/></mask>
<filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
<linearGradient id="fr" x1="0" x2="1"><stop offset="0.6" stop-color="#fff" stop-opacity="0"/><stop offset="0.78" stop-color="#fff"/><stop offset="0.97" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><mask id="fadeR"><rect width="{w}" height="{h}" fill="url(#fr)"/></mask>
<clipPath id="card"><rect width="{w}" height="{h}" rx="22"/></clipPath>
</defs>'''

def wave(x0, x1, cy, amp, seed, step=3.0, env=None):
    r = random.Random(seed); pts_top=[]; pts_bot=[]
    n = int((x1-x0)/step)
    phase = [r.random()*6.28 for _ in range(4)]
    for i in range(n+1):
        x = x0 + i*step; u = i/n
        e = env(u) if env else (0.35+0.65*abs(math.sin(u*math.pi*3.3+phase[0]))*(0.6+0.4*math.sin(u*17+phase[1])))
        e *= math.sin(math.pi*u)**0.35
        a = amp*e*(0.55+0.45*r.random())
        pts_top.append((x, cy-a)); pts_bot.append((x, cy+a*(0.8+0.2*r.random())))
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts_top) + ' L' + ' L'.join(f'{x:.1f},{y:.1f}' for x,y in reversed(pts_bot)) + 'Z'
    return d

COLORS = ['#4a90d9','#d9536b','#55d43f','#d9b23f','#9b6bd9']
def blocks(x0, x1, cy, h, seed, alpha=0.22):
    r = random.Random(seed); x=x0; out=[]; i=0
    while x < x1:
        w = r.uniform(70, 190)
        y = cy - h/2 + r.uniform(-h*0.25, h*0.25)
        c = COLORS[r.randrange(len(COLORS))]
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="4" fill="#b8cee0" opacity="{alpha}"/>'
                   f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="3" fill="{c}" opacity="{alpha*2.4}"/>')
        x += w + r.uniform(14, 40); i+=1
    return ''.join(out)

FONT = "font-family:Montserrat;"
def render(name, svg, w, h, scale=2):
    p = os.path.join(TMP, name+'.svg'); open(p,'w').write(svg)
    subprocess.run(['inkscape', p, '--export-type=png', f'--export-filename={os.path.join(OUT,name+".png")}',
                    f'--export-width={w*scale}'], check=True, capture_output=True)

# 1. banner ---------------------------------------------------------------
W,H = 880,300
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs(W,H,0.22,0.45)}
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#bg)"/>
<g mask="url(#fade)"><path d="{wave(0,W,262,26,7)}" fill="#b8cee0" opacity="0.12"/>{blocks(-20,W,262,22,3,0.16)}</g>
<line x1="610" y1="236" x2="610" y2="288" stroke="#e05a5a" stroke-width="1.6" opacity="0.8"/>
{mark(170,128,140)}
<text x="300" y="126" fill="#e6eef5" style="{FONT}font-weight:300;font-size:56px;letter-spacing:18px">SUBTITLD</text>
<text x="302" y="166" fill="#9fb3c4" style="{FONT}font-weight:400;font-size:17px">Free and open source subtitles, from the waveform up.</text>
<text x="302" y="196" fill="#6f8597" style="{FONT}font-weight:500;font-size:12px;letter-spacing:3px">LINUX · WINDOWS · MACOS · HAIKU</text>
</g></svg>'''
render('banner', svg, W, H)

# 2. pipeline -------------------------------------------------------------
W,H = 880,210
stages = [('TIME','on the waveform'),('TRANSCRIBE','speech to text'),('TRANSLATE','into other languages'),('DUB','with synthetic voices')]
cw, gap = 182, 30; x0 = (W - (4*cw+3*gap))/2
def glyph(k, cx, cy):
    g = '#55d43f'; l = '#b8cee0'
    if k==0:  # waveform with a block and playhead
        return (f'<path d="{wave(cx-48,cx+48,cy,18,11,2)}" fill="{l}" opacity="0.55"/>'
                f'<rect x="{cx-22}" y="{cy-12}" width="40" height="24" rx="3" fill="{g}" opacity="0.85"/>'
                f'<line x1="{cx+28}" y1="{cy-26}" x2="{cx+28}" y2="{cy+26}" stroke="#e05a5a" stroke-width="2"/>')
    if k==1:  # wave -> lines
        return (f'<path d="{wave(cx-50,cx-6,cy,18,5,2)}" fill="{l}" opacity="0.55"/>'
                f'<path d="M{cx-2},{cy} l10,0" stroke="{g}" stroke-width="3" stroke-linecap="round"/><path d="M{cx+4},{cy-5} l5,5 -5,5" fill="none" stroke="{g}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
                + ''.join(f'<rect x="{cx+16}" y="{cy-16+i*12}" width="{[34,28,20][i]}" height="6" rx="3" fill="{l}" opacity="0.85"/>' for i in range(3)))
    if k==2:
        return (f'<text x="{cx-30}" y="{cy+11}" text-anchor="middle" fill="{l}" style="{FONT}font-weight:500;font-size:32px">A</text>'
                f'<path d="M{cx-12},{cy} l22,0" stroke="{g}" stroke-width="3" stroke-linecap="round"/><path d="M{cx+4},{cy-6} l6,6 -6,6" fill="none" stroke="{g}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<text x="{cx+32}" y="{cy+11}" text-anchor="middle" fill="{l}" style="font-family:Noto Sans CJK JP,Noto Sans CJK SC,sans-serif;font-size:30px">文</text>')
    return (''.join(f'<rect x="{cx-50}" y="{cy-16+i*12}" width="{[30,24,18][i]}" height="6" rx="3" fill="{l}" opacity="0.85"/>' for i in range(3))
            + f'<path d="M{cx-14},{cy} l10,0" stroke="{g}" stroke-width="3" stroke-linecap="round"/><path d="M{cx-8},{cy-5} l5,5 -5,5" fill="none" stroke="{g}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            + f'<path d="{wave(cx+4,cx+52,cy,20,9,2)}" fill="{g}" opacity="0.8"/>')
parts=[]
for i,(t,s) in enumerate(stages):
    x = x0 + i*(cw+gap); cx = x+cw/2
    parts.append(f'<rect x="{x}" y="28" width="{cw}" height="154" rx="16" fill="#0f151b" opacity="0.35"/>'
                 f'<rect x="{x}" y="28" width="{cw}" height="154" rx="16" fill="none" stroke="#b8cee0" stroke-opacity="0.12"/>'
                 + glyph(i, cx, 80) +
                 f'<text x="{cx}" y="136" text-anchor="middle" fill="#e6eef5" style="{FONT}font-weight:500;font-size:15px;letter-spacing:4px">{t}</text>'
                 f'<text x="{cx}" y="158" text-anchor="middle" fill="#8ca2b4" style="{FONT}font-size:12px">{s}</text>')
    if i<3:
        ax = x+cw+gap/2
        parts.append(f'<path d="M{ax-6},{97} l7,8 -7,8" fill="none" stroke="#55d43f" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs(W,H,0.5,0.3)}
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#bg)"/>{''.join(parts)}</g></svg>'''
render('pipeline', svg, W, H)

# 3. section strips -------------------------------------------------------
W,H = 880,96
def strip(name, title, sub, motif, seed):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs(W,H,0.12,0.5)}
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#bg)"/><g mask="url(#fadeR)">{motif}</g>
<rect x="28" y="30" width="5" height="36" rx="2.5" fill="#55d43f"/>
<text x="48" y="50" fill="#e6eef5" style="{FONT}font-weight:400;font-size:20px;letter-spacing:6px">{title}</text>
<text x="49" y="72" fill="#8ca2b4" style="{FONT}font-size:13px">{sub}</text></g></svg>'''
    render(name, svg, W, H)

L='#b8cee0'; G='#55d43f'
def lines(x0,x1,cy,seed,color=L,op=0.5):
    r=random.Random(seed); x=x0; o=[]
    while x<x1:
        w=r.uniform(20,70); o.append(f'<rect x="{x:.0f}" y="{cy-3}" width="{w:.0f}" height="6" rx="3" fill="{color}" opacity="{op}"/>'); x+=w+r.uniform(8,16)
    return ''.join(o)
fadeR = lambda inner: f'<g opacity="1">{inner}</g>'
strip('speech-to-text','SPEECH-TO-TEXT','Hear the audio, write the subtitles. Offline, or through Subtitld Cloud.',
      f'<path d="{wave(560,760,48,26,21)}" fill="{L}" opacity="0.18"/>'
      + lines(770,860,38,1,L,0.45)+lines(778,850,58,2,L,0.35), 1)
strip('translation','TRANSLATION','Every subtitle into another language, on this computer.',
      ''.join(f'<text x="{x}" y="{y}" fill="{L}" opacity="{o}" style="font-family:Montserrat,Noto Sans CJK JP,sans-serif;font-size:{s}px">{t}</text>'
              for x,y,o,s,t in [(560,60,0.22,30,'Olá'),(628,38,0.2,20,'Hello'),(650,78,0.22,24,'Hallo'),(712,44,0.25,20,'こんにちは'),(730,84,0.2,18,'Bonjour'),(818,74,0.25,24,'你好')]), 2)
strip('text-to-speech','TEXT-TO-SPEECH AND DUBBING','Voices for the subtitles: presets, described voices, or the speaker’s own.',
      lines(600,700,38,3,L,0.4)+lines(606,690,58,4,L,0.3)+f'<path d="{wave(705,870,48,30,33)}" fill="{G}" opacity="0.4"/>', 3)
strip('audio-video','AUDIO AND VIDEO','Pull the voice apart from the music, and move the lips to the new words.',
      f'<path d="{wave(580,870,34,14,41)}" fill="{L}" opacity="0.3"/><path d="{wave(580,870,64,14,42)}" fill="{G}" opacity="0.4"/>', 4)
print('ok')
