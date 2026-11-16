"""SIADS 521 economic dashboard: offline linked dashboard using Plotly.

Run: python build_dashboard.py
Creates: macrodata_clean.csv and index.html

Source: statsmodels.datasets.macrodata, public domain, originally FRED and BLS.
Plotly is MIT licensed. No Matplotlib or pandas .plot is used.
"""
from pathlib import Path
import json
import pandas as pd
import statsmodels.api as sm
from plotly.offline import get_plotlyjs

HERE = Path(__file__).resolve().parent


def clean_data():
    """Load the unmodified 203-row data and add interpretable, reproducible fields."""
    df = sm.datasets.macrodata.load_pandas().data.copy()
    df = df.sort_values(["year", "quarter"]).reset_index(drop=True)
    numeric = ["realgdp", "realcons", "realinv", "tbilrate", "unemp", "infl"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["year"] = df["year"].astype(int)
    df["quarter"] = df["quarter"].astype(int)
    assert len(df) == 203 and df[numeric].notna().all().all()
    df["period"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)
    df["date"] = pd.PeriodIndex.from_fields(
        year=df["year"], quarter=df["quarter"], freq="Q"
    ).to_timestamp().strftime("%Y-%m-%d")
    df["decade"] = (df["year"] // 10) * 10
    df["gdp_growth_qoq"] = 100 * df["realgdp"].pct_change()
    df["investment_share"] = 100 * df["realinv"] / df["realgdp"]
    df["joint_high"] = (df["infl"] >= 6) & (df["unemp"] >= 6)
    return df


# Single HTML keeps all interactive data and Plotly.js embedded locally.
PAGE_TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Four views of the US economy | SIADS 521</title>
<style>
:root{--bg:#0b1221;--panel:#121e32;--panel2:#17253a;--line:#2b3c53;--ink:#eff6ff;--muted:#a1b4c8;--cyan:#48c9e8;--pink:#f7a28e;--gold:#f4c76c}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 10% 0,#1c3451 0,#0b1221 47%);color:var(--ink);font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:14px}
.wrap{max-width:1450px;margin:0 auto;padding:29px 28px 55px}
.topline{color:var(--cyan);font-size:11px;font-weight:750;letter-spacing:2.2px;text-transform:uppercase;margin-bottom:7px}
h1{font-weight:740;font-size:clamp(25px,3.5vw,39px);letter-spacing:-.8px;margin:0 0 8px}h2{font-size:14px;font-weight:710;letter-spacing:.25px;margin:0}
p{line-height:1.5}.lead{max-width:920px;color:var(--muted);font-size:14px;margin:0 0 21px}
.toolbar{display:flex;flex-wrap:wrap;gap:17px;align-items:end;border:1px solid var(--line);background:#121f32d9;border-radius:15px;padding:17px 20px;margin-bottom:15px}
.field{display:grid;gap:6px;min-width:155px}.field.year{flex:1;min-width:160px}.field label{font-size:11px;color:var(--muted);letter-spacing:.35px;font-weight:700}
select{background:var(--panel2);border:1px solid #355069;color:var(--ink);padding:10px;border-radius:8px;font-size:13px;min-width:160px}
.val{color:#fff;font-size:12px;font-weight:750}
.year-label{display:flex;justify-content:space-between;gap:12px;color:var(--muted);font-size:11px;font-weight:700;letter-spacing:.35px}
.range-control{position:relative;height:32px;min-width:160px}
.range-track{position:absolute;left:11px;right:11px;top:13px;height:6px;background:#355069;border-radius:6px;pointer-events:none}
.range-selection{position:absolute;height:100%;background:var(--cyan);border-radius:6px}
.range-control input[type=range]{appearance:none;-webkit-appearance:none;position:absolute;inset:0;width:100%;height:32px;margin:0;background:transparent;pointer-events:none}
.range-control input::-webkit-slider-runnable-track{height:6px;background:transparent}
.range-control input::-moz-range-track{height:6px;background:transparent}
.range-control input::-webkit-slider-thumb{-webkit-appearance:none;width:22px;height:22px;margin-top:-8px;border:2px solid var(--panel);border-radius:50%;background:var(--cyan);cursor:ew-resize;pointer-events:auto;touch-action:none}
.range-control input::-moz-range-thumb{width:18px;height:18px;border:2px solid var(--panel);border-radius:50%;background:var(--cyan);cursor:ew-resize;pointer-events:auto;touch-action:none}
.range-control input:focus-visible{outline:none}
.range-control input:focus-visible::-webkit-slider-thumb{outline:2px solid white;outline-offset:2px}
.range-control input:focus-visible::-moz-range-thumb{outline:2px solid white;outline-offset:2px}
.compare-toggle{display:block;margin:0 0 15px;padding:9px 14px;border:1px solid #355069;border-radius:8px;background:var(--panel2);color:var(--ink);font:inherit;cursor:pointer}
.compare-toggle:focus-visible{outline:2px solid var(--cyan);outline-offset:3px}
.comparison-panel{margin-bottom:17px;padding:16px;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
.comparison-panel[hidden]{display:none}
.comparison-note{margin:7px 0 13px;color:var(--muted);font-size:12px}
.comparison-controls{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:12px}
.comparison-controls .field{flex:1;min-width:0;flex-basis:240px}
.comparison-controls select{width:100%;min-width:0}
.comparison-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.comparison-card{padding:13px;border:1px solid var(--line);border-radius:9px;background:var(--panel2);min-width:0}
.comparison-card h3{font-size:12px;margin:0 0 10px;font-weight:650}
.comparison-value{display:flex;justify-content:space-between;gap:10px;margin:5px 0;color:var(--muted);font-size:12px}
.comparison-value strong{color:var(--ink);white-space:nowrap}
.comparison-delta{display:block;font-size:23px;font-weight:750;margin-top:10px;color:var(--muted)}
.comparison-delta.increase{color:var(--cyan)}.comparison-delta.decrease{color:var(--pink)}
.comparison-direction{display:block;color:var(--muted);font-size:11px;margin-top:4px}
@media(max-width:650px){.comparison-cards{grid-template-columns:1fr}}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:17px}
.stat{border:1px solid var(--line);background:var(--panel);padding:14px 16px;border-radius:12px;min-width:0}
.stat label{display:block;color:var(--muted);font-size:11px;margin-bottom:7px}.stat strong{display:block;font-size:26px;letter-spacing:-.7px}.stat small{display:block;color:#9db5ca;font-size:11px;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}
.chartcard{border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:16px 16px 9px;overflow:hidden;min-width:0}
.chartcard header{display:flex;flex-direction:column;gap:5px;margin-bottom:1px}.subtitle{font-size:11px;color:var(--muted)}.plot{height:320px;width:100%}
.insight{margin-top:17px;border:1px solid #3b5965;border-left:4px solid var(--cyan);background:#13253a;border-radius:11px;padding:15px 19px}
.insight h2{margin-bottom:5px}.insight p{margin:0;color:#c2d1de}
footer{padding-top:20px;color:#9bb0c4;font-size:11px;line-height:1.7}footer a{color:#8bddf1}
@media(max-width:850px){.grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.wrap{padding:18px 15px 40px}.plot{height:320px}}
@media(max-width:470px){.toolbar{gap:10px}.stats{gap:8px}.stat{padding:10px}.stat strong{font-size:21px}}
</style>
<script>/*PLOTLY_BUNDLE*/</script>
</head>
<body><main class="wrap">
<div class="topline">SIADS 521 • Interactive exploration demo • Historical snapshot</div>
<h1>Four views of the U.S. economy</h1>
<p class="lead">What changes when we compare inflation, unemployment and growth across decades? Use the same year selection to update all four views. Data: 1959 Q1–2009 Q3 (203 quarterly observations).</p>
<section class="toolbar" aria-label="Dashboard filters">
  <div class="field"><label for="decade">DECADE PRESET</label>
    <select id="decade"><option value="all">All available years</option><option value="custom">Custom range</option><option value="1960">1960s</option><option value="1970">1970s</option><option value="1980">1980s</option><option value="1990">1990s</option><option value="2000">2000s</option></select>
  </div>
  <div class="field year" role="group" aria-labelledby="yearRangeLabel">
    <div class="year-label"><span id="yearRangeLabel">YEAR RANGE</span><span class="val"><span id="startval">1959</span> – <span id="endval">2009</span></span></div>
    <div class="range-control">
      <div class="range-track"><div class="range-selection" id="yearSelection"></div></div>
      <input id="start" aria-label="Start year" type="range" min="1959" max="2009" step="1" value="1959"/>
      <input id="end" aria-label="End year" type="range" min="1959" max="2009" step="1" value="2009"/>
    </div>
  </div>
</section>
<button type="button" class="compare-toggle" id="compareToggle" aria-expanded="false" aria-controls="comparisonPanel">Compare Decades ▸</button>
<section class="comparison-panel" id="comparisonPanel" aria-labelledby="comparisonTitle" hidden>
  <h2 id="comparisonTitle">Compare Decades</h2>
  <p class="comparison-note">Each period uses all available quarters in that decade from the full dataset, independently of the chart filters above. Decades with at least 36 of 40 quarters are offered; partial coverage is labeled. The four quarters from 1959 are excluded.</p>
  <div class="comparison-controls">
    <div class="field"><label for="periodA">Period A</label><select id="periodA"></select></div>
    <div class="field"><label for="periodB">Period B</label><select id="periodB"></select></div>
  </div>
  <p class="comparison-note">Deltas are Period B − Period A in percentage points (pp). Colors and signs indicate direction only; an increase or decrease is not automatically good or bad.</p>
  <div class="comparison-cards" aria-live="polite" aria-atomic="true">
    <article class="comparison-card"><h3>Average inflation rate</h3><div id="compareInflation"></div></article>
    <article class="comparison-card"><h3>Average unemployment rate</h3><div id="compareUnemployment"></div></article>
    <article class="comparison-card"><h3>Quarters with both indicators ≥6%</h3><div id="compareJoint"></div></article>
  </div>
  <aside class="insight"><h2>What changed between these decades?</h2><p id="comparisonInsight" aria-live="polite" aria-atomic="true"></p></aside>
</section>
<section class="stats" aria-label="Selected-period summary">
  <div class="stat"><label>Quarters selected</label><strong id="n">—</strong><small id="periodSummary">1959–2009</small></div>
  <div class="stat"><label>Average inflation</label><strong id="meanInfl">—</strong><small>Annualized CPI inflation %</small></div>
  <div class="stat"><label>Average unemployment</label><strong id="meanUn">—</strong><small>Unemployment %</small></div>
  <div class="stat"><label>Both ≥6% at once</label><strong id="joint">—</strong><small>Quarters with both elevated</small></div>
</section>
<section class="grid" aria-label="Linked charts">
  <article class="chartcard"><header><h2>Inflation and unemployment through time</h2><span class="subtitle">Two rates on one shared percentage scale</span></header><div class="plot" id="lineplot"></div></article>
  <article class="chartcard"><header><h2>Do the two rates rise together?</h2><span class="subtitle">Each point is one quarter; color indicates GDP growth</span></header><div class="plot" id="scatterplot"></div></article>
  <article class="chartcard"><header><h2>Distribution of inflation</h2><span class="subtitle">How common were low and high inflation quarters?</span></header><div class="plot" id="histplot"></div></article>
  <article class="chartcard"><header><h2>How often are both rates elevated?</h2><span class="subtitle">Follow the hierarchy: inflation band → unemployment band</span></header><div class="plot" id="parallelplot"></div></article>
</section>
<aside class="insight"><h2>What did the filter reveal?</h2><p id="insight">Choose a decade to compare the frequency of jointly high inflation and unemployment.</p></aside>
<footer>Data: <a href="https://www.statsmodels.org/stable/datasets/generated/macrodata.html" target="_blank" rel="noopener">U.S. macroeconomic indicators</a>, compiled from the Federal Reserve Bank of St. Louis (FRED) and U.S. Bureau of Labor Statistics; data public domain. Inflation is already an annualized log CPI rate in the original source. GDP growth is computed quarter-over-quarter (not annualized). Values are historical, not current. Chart library: Plotly (MIT). Offline file, with data and scripts embedded—no network needed to use the charts.</footer>
</main>
<script>
const rows=/*DATA_JSON*/;
const P={paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{family:'Inter, system-ui, sans-serif',size:11,color:'#b8cbde'},margin:{l:48,r:16,t:25,b:46},hovermode:'closest',showlegend:false};
const cfg={displayModeBar:false,responsive:true};
const has=(x)=>x!==null&&x!==undefined&&Number.isFinite(Number(x));
// Calculate bounds once from all quarters so colors stay comparable across filters.
const growthValues=rows.filter(r=>has(r.gdp_growth_qoq)).map(r=>r.gdp_growth_qoq);
const growthMin=Math.floor(Math.min(...growthValues));
const growthMax=Math.ceil(Math.max(...growthValues));
const avg=(array)=>array.length?array.reduce((a,b)=>a+b,0)/array.length:0;
const pct=(n)=>n.toFixed(2)+'%';
const chartGrid={gridcolor:'#2c4057',zerolinecolor:'#344d64'};
function baseLayout(extra){return {...P,...extra,xaxis:{...(extra.xaxis||{}),...chartGrid},yaxis:{...(extra.yaxis||{}),...chartGrid}};}
function initializeComparison(){
 // Separate summaries use the complete dataset, never the main chart selection.
 const periods=[...new Set(rows.map(r=>r.decade))].sort((a,b)=>a-b).map(decade=>{
   const d=rows.filter(r=>r.decade===decade);
   return {decade,label:decade+'s',count:d.length,first:d[0].period,last:d[d.length-1].period,
     inflation:avg(d.map(r=>r.infl)),unemployment:avg(d.map(r=>r.unemp)),
     joint:100*d.filter(r=>r.infl>=6&&r.unemp>=6).length/d.length};
 }).filter(p=>p.count>=36);
 const periodA=document.getElementById('periodA'),periodB=document.getElementById('periodB');
 for(const select of [periodA,periodB]){
   for(const p of periods){
     const option=document.createElement('option');
     option.value=p.decade;
     option.textContent=p.label+' ('+(p.count<40?'partial: '+p.first+'–'+p.last+'; ':'')+p.count+'/40 quarters)';
     select.appendChild(option);
   }
 }
 periodA.value='1970';periodB.value='1990';
 function renderComparison(){
   const a=periods.find(p=>p.decade===Number(periodA.value));
   const b=periods.find(p=>p.decade===Number(periodB.value));
   for(const [id,key] of [['compareInflation','inflation'],['compareUnemployment','unemployment'],['compareJoint','joint']]){
     const card=document.getElementById(id);
     card.replaceChildren();
     for(const [name,p] of [['A',a],['B',b]]){
       const row=document.createElement('div');row.className='comparison-value';
       const label=document.createElement('span');label.textContent=name+' · '+p.label;
       const value=document.createElement('strong');value.textContent=pct(p[key]);
       row.appendChild(label);row.appendChild(value);card.appendChild(row);
     }
     // Round only for display; subtract the full-precision period summaries.
     const delta=Number((b[key]-a[key]).toFixed(2));
     const value=document.createElement('span');
     value.className='comparison-delta '+(delta>0?'increase':delta<0?'decrease':'unchanged');
     value.textContent=(delta>0?'+':delta<0?'−':'')+Math.abs(delta).toFixed(2)+' pp';
     const direction=document.createElement('span');direction.className='comparison-direction';
     direction.textContent=(delta>0?'Increase':delta<0?'Decrease':'No change')+' · B − A';
     card.appendChild(value);card.appendChild(direction);
   }
   function describeChange(label,key){
     const delta=Number((b[key]-a[key]).toFixed(2));
     const change=delta===0?'was unchanged':(delta>0?'rose':'fell')+' by '+Math.abs(delta).toFixed(2)+' percentage points';
     return label+' '+change+' (from '+pct(a[key])+' to '+pct(b[key])+').';
   }
   const coverage=p=>p.count+' quarters in the '+p.label+(p.count<40?' (partial decade)':'');
   document.getElementById('comparisonInsight').textContent=[
     'Comparing the '+a.label+' (Period A) with the '+b.label+' (Period B):',
     describeChange('Average inflation','inflation'),
     describeChange('Average unemployment','unemployment'),
     describeChange('The share of quarters with both inflation and unemployment at least 6%','joint'),
     'This comparison uses '+coverage(a)+' and '+coverage(b)+', independently of the main chart filters.'
   ].join(' ');
 }
 periodA.addEventListener('change',renderComparison);
 periodB.addEventListener('change',renderComparison);
 const toggle=document.getElementById('compareToggle'),panel=document.getElementById('comparisonPanel');
 toggle.addEventListener('click',()=>{
   panel.hidden=!panel.hidden;
   toggle.setAttribute('aria-expanded',String(!panel.hidden));
   toggle.textContent='Compare Decades '+(panel.hidden?'▸':'▾');
 });
 renderComparison();
}
function update(){
 const start=Number(document.getElementById('start').value);
 const end=Number(document.getElementById('end').value);
 document.getElementById('startval').textContent=start;
 document.getElementById('endval').textContent=end;
 const selection=document.getElementById('yearSelection');
 selection.style.left=((start-1959)/50*100)+'%';
 selection.style.right=((2009-end)/50*100)+'%';
 // Keep the start handle reachable when both handles meet at the maximum year.
 document.getElementById('start').style.zIndex=start===2009?'2':'0';
 const d=rows.filter(r=>r.year>=start && r.year<=end);
 const colors={inf:'#f7a28e',un:'#48c9e8'};
 const set=(id,text)=>{document.getElementById(id).textContent=text};
 const joint=d.filter(r=>r.infl>=6&&r.unemp>=6).length;
 set('n',d.length);set('periodSummary',start+'–'+end);
 set('meanInfl',d.length?pct(avg(d.map(r=>r.infl))):'—');
 set('meanUn',d.length?pct(avg(d.map(r=>r.unemp))):'—');
 set('joint',d.length?joint+' / '+d.length:'—');
 const cdates=d.map(r=>r.date);
 const xLabel=d.map(r=>r.period);
 Plotly.react('lineplot',[
   {type:'scatter',mode:'lines+markers',x:cdates,y:d.map(r=>r.infl),name:'Inflation',line:{color:colors.inf,width:2.6},marker:{size:4},customdata:xLabel,hovertemplate:'%{customdata}<br>Inflation: %{y:.2f}%<extra></extra>'},
   {type:'scatter',mode:'lines+markers',x:cdates,y:d.map(r=>r.unemp),name:'Unemployment',line:{color:colors.un,width:2.6},marker:{size:4},customdata:xLabel,hovertemplate:'%{customdata}<br>Unemployment: %{y:.2f}%<extra></extra>'}
 ],baseLayout({showlegend:true,legend:{orientation:'h',x:0,y:1.13,font:{size:10}},xaxis:{title:{text:'Year - Quarter'},tickformat:'%Y'},yaxis:{title:{text:'Percent (%)'}},hovermode:'x unified'}),cfg);
 const scat=d.filter(r=>has(r.gdp_growth_qoq));
 Plotly.react('scatterplot',[{type:'scatter',mode:'markers',x:scat.map(r=>r.unemp),y:scat.map(r=>r.infl),text:scat.map(r=>r.period),customdata:scat.map(r=>r.gdp_growth_qoq),marker:{size:9,opacity:.88,color:scat.map(r=>r.gdp_growth_qoq),cmin:growthMin,cmax:growthMax,colorscale:'RdYlBu',line:{color:'#233a50',width:.5},showscale:true,colorbar:{title:{text:'GDP QoQ<br>% change',side:'top'},len:.72,thickness:10,font:{size:9},x:1.02}},hovertemplate:'%{text}<br>Unemployment: %{x:.2f}%<br>Inflation: %{y:.2f}%<br>GDP growth: %{customdata:.2f}%<extra></extra>'}],baseLayout({margin:{l:49,r:70,t:26,b:45},xaxis:{title:{text:'Unemployment (%)'}},yaxis:{title:{text:'Inflation (%)'}},shapes:[{type:'line',xref:'x',yref:'paper',x0:6,x1:6,y0:0,y1:1,line:{color:'#658199',dash:'dot',width:1}},{type:'line',xref:'paper',yref:'y',x0:0,x1:1,y0:6,y1:6,line:{color:'#658199',dash:'dot',width:1}}]}),cfg);
 Plotly.react('histplot',[{type:'histogram',x:d.map(r=>r.infl),xbins:{start:-16,end:20,size:2},marker:{color:'#48c9e8',line:{color:'#0d2033',width:1}},opacity:.9,hovertemplate:'Inflation bin: %{x:.1f}%<br>Quarters: %{y}<extra></extra>'}],baseLayout({bargap:.07,xaxis:{title:{text:'Annualized inflation (%)'},range:[-16,20]},yaxis:{title:{text:'Number of quarters'},rangemode:'tozero'}}),cfg);
 const count=(highInfl,highUn)=>d.filter(r=>(r.infl>=6)===highInfl && (r.unemp>=6)===highUn).length;
 const ih=count(true,true)+count(true,false), il=count(false,true)+count(false,false);
 const ids=['root','highinf','lowinf','highinf-highun','highinf-lowun','lowinf-highun','lowinf-lowun'];
 const labels=['All quarters','Inflation ≥6%','Inflation <6%','Unemp ≥6%','Unemp <6%','Unemp ≥6%','Unemp <6%'];
 const parents=['','root','root','highinf','highinf','lowinf','lowinf'];
 const values=[d.length,ih,il,count(true,true),count(true,false),count(false,true),count(false,false)];
 Plotly.react('parallelplot',[{type:'sunburst',ids:ids,labels:labels,parents:parents,values:values,branchvalues:'total',maxdepth:3,sort:false,insidetextorientation:'radial',textinfo:'label+value',textfont:{size:12},marker:{colors:['#29445e','#ee9a86','#4cbcd6','#cb655f','#f1c57d','#7bb8b9','#58a2bf']},hovertemplate:'%{label}<br>%{value} quarters<br>%{percentRoot:.1%} of selection<extra></extra>'}],{...P,margin:{l:5,r:5,t:3,b:5}},cfg);
 const rate=d.length?Math.round(joint/d.length*100):0;
 document.getElementById('insight').textContent=`From ${start} to ${end}, ${joint} out of ${d.length} quarters (${rate}%) had both inflation and unemployment at or above 6%. Use the decade preset to compare with other decades. The dashed guides on the scatterplot mark the same thresholds; the sunburst breaks the selected quarters into the four combinations of high/low inflation and unemployment. This is descriptive, not a claim about causation.`;
}
const startInput=document.getElementById('start'),endInput=document.getElementById('end'),decade=document.getElementById('decade');
decade.addEventListener('change',()=>{
 if(decade.value==='all'){startInput.value=1959;endInput.value=2009;}
 else if(decade.value!=='custom'){startInput.value=Number(decade.value);endInput.value=Math.min(Number(decade.value)+9,2009);}
 update();
});
startInput.addEventListener('input',()=>{if(+startInput.value>+endInput.value)endInput.value=startInput.value;decade.value='custom';update();});
endInput.addEventListener('input',()=>{if(+endInput.value<+startInput.value)startInput.value=endInput.value;decade.value='custom';update();});
initializeComparison();
update();
</script>
</body></html>'''


def create_dashboard(df=None):
    """Write shareable CSV and a *truly offline*, linked four-chart HTML page."""
    df = clean_data() if df is None else df.copy()
    # Notebook dates are timestamps; normalize both build paths before CSV/JSON export.
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    csv_path = HERE / "macrodata_clean.csv"
    df.to_csv(csv_path, index=False)
    used = ["year", "quarter", "date", "period", "decade", "infl", "unemp", "gdp_growth_qoq", "tbilrate", "investment_share"]
    records = df[used].astype(object).where(pd.notna(df[used]), None).to_dict(orient="records")
    # Use safe JSON numeric nulls, never NaN (not legal JSON in browser).
    records = json.loads(json.dumps(records, allow_nan=False, default=str))
    html = PAGE_TEMPLATE.replace("/*PLOTLY_BUNDLE*/", get_plotlyjs())
    html = html.replace("/*DATA_JSON*/", json.dumps(records, separators=(",", ":"), allow_nan=False))
    out = HERE / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Created {out.name} ({out.stat().st_size / 1e6:.1f} MB) and {csv_path.name} ({len(df)} rows)")
    return out


if __name__ == "__main__":
    create_dashboard()
