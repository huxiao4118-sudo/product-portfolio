/* Offline adapter. Reads a saved SQL export; never calls a server or retrains a model. */
(() => {
  'use strict';
  const source=window.OLIST_DATA;
  const orders=source.rows.map(row=>Object.fromEntries(source.columns.map((k,i)=>[k,row[i]])));
  const byId=new Map(orders.map(o=>[o.order_id,o]));
  const storageKey='olist-recruitment-demo-cases-v1';
  let localEvents=[];
  try{localEvents=JSON.parse(localStorage.getItem(storageKey)||'[]');if(!Array.isArray(localEvents))localEvents=[]}catch{}
  const events=()=>[...source.events,...localEvents];
  let revision=0,cache=null;
  const ts=v=>v?Date.parse(String(v).replace(' ','T')+( /(?:Z|[+-]\d\d:\d\d)$/.test(v)?'':'Z')):NaN;
  const day=v=>Math.floor(ts(v)/86400000);
  const quantile=(array,q)=>{const a=array.slice().sort((x,y)=>x-y);if(!a.length)return 1;const i=(a.length-1)*q,k=Math.floor(i);return a[k]+(a[Math.ceil(i)]-a[k])*(i-k)};
  const group=(rows,key)=>{const out=new Map;for(const r of rows){const k=r[key];if(!out.has(k))out.set(k,[]);out.get(k).push(r)}return [...out.entries()]};
  const sum=(a,k)=>a.reduce((s,r)=>s+Number(r[k]||0),0);
  function snapshot(params){
    const asof=params.get('asof')||'2018-06-15',state=params.get('state')||'';
    const key=asof+'|'+state+'|'+revision;
    if(cache?.key===key)return cache;
    const at=ts(asof+'T12:00:00'),d=day(asof),latest=new Map;
    for(const e of events()){const prev=latest.get(e.order_id);if(!prev||Number(e.event_id)>Number(prev.event_id))latest.set(e.order_id,e)}
    const frame=orders.filter(r=>ts(r.approval_at)<=at&&(!state||r.customer_state===state)).map(raw=>{
      const r={...raw},delivered=ts(r.delivered_at)<=at,carrier=ts(r.carrier_at)<=at;
      r.days_to_promise=day(r.promised_at)-d;
      r.overdue_days=delivered?0:Math.max(d-day(r.promised_at),0);
      r.delivery_status=delivered?(day(r.delivered_at)>day(r.promised_at)?'Delivered late':'Delivered on time'):
        day(r.promised_at)<d?'Overdue':r.days_to_promise<=2?'Due soon':'Within promise';
      r.fulfillment_stage=delivered?'Delivered':carrier?'In transit':'Awaiting carrier';
      r.carrier_at=carrier?r.carrier_at:null;r.delivered_at=delivered?r.delivered_at:null;
      r.dispatch_overdue=!carrier&&ts(r.shipping_limit_at)<at;
      r.case_status=latest.get(r.order_id)?.action_status||'Open';
      r.amount_risk=r.merchandise_value*r.risk_probability;r.top_factors=[];
      return r;
    });
    const pending=frame.filter(r=>r.fulfillment_stage!=='Delivered');
    const cutoff=quantile(pending.map(r=>r.risk_probability),.8);
    for(const r of pending){r.at_risk=r.risk_probability>=cutoff&&r.delivery_status==='Within promise';r.priority_label=r.at_risk?'At risk':r.delivery_status;r.priority_rank={'Overdue':0,'Due soon':1,'At risk':2,'Within promise':3}[r.priority_label]}
    const metrics={scored:frame.length,pending:pending.length,overdue:pending.filter(r=>r.delivery_status==='Overdue').length,
      due_soon:pending.filter(r=>r.delivery_status==='Due soon').length,at_risk:pending.filter(r=>r.at_risk).length,
      dispatch_overdue:pending.filter(r=>r.dispatch_overdue).length,pending_amount:sum(pending,'merchandise_value')};
    const states=group(pending,'customer_state').map(([customer_state,rows])=>({customer_state,pending:rows.length,overdue:rows.filter(r=>r.delivery_status==='Overdue').length,mean_risk:sum(rows,'risk_probability')/rows.length})).sort((a,b)=>b.overdue-a.overdue||a.customer_state.localeCompare(b.customer_state));
    const stages=group(pending,'fulfillment_stage').map(([fulfillment_stage,rows])=>({fulfillment_stage,orders:rows.length})).sort((a,b)=>a.fulfillment_stage.localeCompare(b.fulfillment_stage));
    const trend=group(frame.map(r=>({...r,day:r.approval_at.slice(0,10)})),'day').map(([day,rows])=>({day,orders:rows.length,mean_risk:sum(rows,'risk_probability')/rows.length})).sort((a,b)=>a.day.localeCompare(b.day));
    const sellers=group(pending,'seller_id').map(([seller_id,rows])=>({seller_id,pending:rows.length,overdue:rows.filter(r=>r.delivery_status==='Overdue').length,merchandise:sum(rows,'merchandise_value')})).sort((a,b)=>b.overdue-a.overdue||b.pending-a.pending||a.seller_id.localeCompare(b.seller_id)).slice(0,5);
    const status_counts=['Overdue','Due soon','At risk','Within promise'].map(status=>({status,orders:pending.filter(r=>r.priority_label===status).length}));
    cache={key,frame,pending,asof:asof+' 12:00:00',metrics,risk_cutoff:cutoff,states,stages,trend,sellers,status_counts};return cache;
  }
  function queue(s,params){
    const filter=params.get('filter')||'all',stage=params.get('stage')||'',search=(params.get('search')||'').trim().toLowerCase();
    return s.pending.filter(r=>(filter==='overdue'?r.delivery_status==='Overdue':filter==='due'?r.delivery_status==='Due soon':filter==='risk'?r.at_risk:true)&&(!stage||r.fulfillment_stage===stage)&&(!search||r.order_id.includes(search)||r.seller_id.includes(search)))
      .sort((a,b)=>a.priority_rank-b.priority_rank||b.overdue_days-a.overdue_days||b.risk_probability-a.risk_probability||a.order_id.localeCompare(b.order_id));
  }
  window.offlineAPI=async function(path,opts){
    const url=new URL(path,'https://offline.invalid'),p=url.searchParams;
    if(url.pathname==='/api/states')return source.states;
    if(url.pathname==='/api/performance')return source.performance;
    if(url.pathname==='/api/case'){
      const body=JSON.parse(opts?.body||'{}');
      if(!byId.has(body.order_id)||!['Open','Investigating','Contacted','Resolved'].includes(body.status))throw Error('Invalid case update');
      const e={event_id:Date.now(),order_id:body.order_id,action_status:body.status,note:String(body.note||'').slice(0,2000),recorded_at:new Date().toISOString()};
      const next=[...localEvents,e];
      try{localStorage.setItem(storageKey,JSON.stringify(next))}catch{throw Error('Browser storage is unavailable. Allow local storage to save demo notes.')}
      localEvents=next;revision++;cache=null;return {saved:true,event_id:e.event_id};
    }
    const s=snapshot(p);
    if(url.pathname==='/api/order'){
      const order=s.frame.find(r=>r.order_id===p.get('id'));if(!order)throw Error('Order not available at this date');
      return {order,events:events().filter(r=>r.order_id===order.order_id).sort((a,b)=>b.event_id-a.event_id)};
    }
    if(url.pathname==='/api/operations'){
      const rows=queue(s,p);const {key,frame,pending,...out}=s;return {...out,queue_total:rows.length,queue:rows.slice(0,150)};
    }
    throw Error('Unsupported offline action');
  };
  window.exportOfflineCSV=function(params){
    const rows=queue(snapshot(params),params),cols=['order_id','seller_id','delivery_status','fulfillment_stage','risk_probability','merchandise_value','promised_at','overdue_days','customer_state','case_status'];
    const cell=x=>'"'+String(x??'').replaceAll('"','""')+'"';
    const csv='\uFEFF'+[cols.join(','),...rows.map(r=>cols.map(c=>cell(r[c])).join(','))].join('\r\n');
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='olist_delivery_queue.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  window.resetOfflineDemo=function(){try{localStorage.removeItem(storageKey)}catch{}localEvents=[];revision++;cache=null;location.reload()};
})();
