// 動物・人物の側面形（右向き、足元 y=0、上がマイナス）。洞窟画風・シルエット風の両方で使う
const ANIMALS={
 mammoth:{body:[[10,-92],[0,-132],[10,-172],[42,-202],[92,-216],[150,-228],[190,-246],[214,-262],[240,-259],[262,-242],[272,-216],[276,-186],[281,-150],[287,-112],[293,-72],[299,-42],[307,-20],[298,-12],[288,-38],[277,-78],[264,-118],[250,-134],[232,-122],[222,-104],[204,-96],[150,-86],[92,-88],[40,-88]],
  legs:[[44,-92,92,30,0],[70,-90,90,28,Math.PI],[198,-100,100,32,Math.PI],[226,-102,102,30,0]],
  extra:(g,c,cave)=>{g.strokeStyle=cave?c:'rgba(225,208,180,0.95)';g.lineWidth=cave?6:8;g.stroke(smoothPath([[258,-128],[284,-104],[312,-92],[336,-102],[344,-124]],false));
   g.strokeStyle=c;g.lineWidth=3;for(let i=0;i<9;i++){const x=70+i*16;g.beginPath();g.moveTo(x,-90);g.lineTo(x-4,-62+((i*7)%3)*4);g.stroke()}}},
 rhino:{body:[[10,-62],[0,-102],[16,-136],[60,-150],[110,-158],[150,-171],[186,-161],[216,-141],[242,-126],[264,-113],[286,-96],[301,-80],[303,-66],[289,-58],[266,-62],[246,-72],[226,-75],[210,-62],[180,-54],[120,-52],[60,-54]],
  legs:[[30,-60,60,24,0],[52,-58,58,22,Math.PI],[188,-60,60,26,Math.PI],[210,-62,62,24,0]],
  extra:(g,c)=>{g.fillStyle=c;g.fill(smoothPath([[286,-92],[322,-176],[331,-174],[302,-84]],true,0.15));g.fill(smoothPath([[264,-108],[276,-140],[283,-138],[278,-102]],true,0.15));
   g.strokeStyle=c;g.lineWidth=3;for(let i=0;i<8;i++){const x=60+i*17;g.beginPath();g.moveTo(x,-54);g.lineTo(x-3,-40);g.stroke()}}},
 reindeer:{body:[[8,-112],[2,-134],[18,-150],[60,-156],[110,-154],[140,-158],[154,-176],[166,-198],[180,-214],[198,-210],[216,-198],[216,-186],[196,-183],[182,-180],[172,-152],[164,-122],[150,-104],[110,-98],[60,-100],[30,-104]],
  legs:[[26,-104,108,17,0],[42,-102,106,15,Math.PI],[146,-104,110,17,Math.PI],[160,-106,112,15,0]],
  extra:(g,c)=>{g.strokeStyle=c;g.lineWidth=6;const a=[[[188,-204],[178,-238],[160,-268],[146,-290]],[[178,-238],[196,-252]],[[163,-264],[178,-286]],[[194,-204],[200,-236],[192,-270],[184,-292]],[[198,-236],[214,-244]],[[183,-208],[196,-226]]];
   for(const p of a)g.stroke(smoothPath(p,false));}},
 horse:{body:[[6,-100],[0,-124],[18,-142],[70,-146],[120,-144],[146,-150],[162,-172],[178,-196],[196,-206],[210,-200],[232,-172],[240,-156],[234,-147],[216,-150],[200,-160],[188,-146],[176,-122],[160,-104],[110,-96],[50,-98]],
  legs:[[24,-98,100,22,0],[42,-98,100,19,Math.PI],[150,-100,102,22,Math.PI],[166,-100,102,19,0]],
  extra:(g,c)=>{g.strokeStyle=c;g.lineWidth=13;g.stroke(smoothPath([[6,-120],[-12,-94],[-16,-56]],false))}},
 bison:{body:[[6,-80],[0,-111],[15,-136],[60,-141],[110,-151],[150,-176],[180,-191],[205,-181],[222,-161],[240,-141],[250,-118],[252,-95],[244,-82],[232,-66],[222,-80],[210,-73],[190,-70],[150,-72],[90,-75],[40,-78]],
  legs:[[26,-80,80,26,0],[46,-78,78,23,Math.PI],[178,-74,74,28,Math.PI],[198,-74,74,25,0]],
  extra:(g,c)=>{g.strokeStyle=c;g.lineWidth=7;g.stroke(smoothPath([[228,-150],[246,-166],[240,-182]],false));g.lineWidth=7;g.stroke(smoothPath([[6,-108],[-10,-84],[-8,-60]],false))}},
 lion:{body:[[10,-74],[4,-100],[28,-118],[90,-122],[150,-124],[186,-132],[208,-138],[226,-146],[248,-140],[262,-124],[259,-108],[242,-102],[222,-100],[204,-88],[182,-70],[120,-62],[60,-66]],
  legs:[[30,-68,72,24,0],[48,-66,72,21,Math.PI],[180,-72,76,25,Math.PI],[196,-74,78,22,0]],
  extra:(g,c)=>{g.strokeStyle=c;g.lineWidth=6;g.stroke(smoothPath([[8,-92],[-24,-80],[-40,-56],[-46,-36]],false));g.fillStyle=c;g.beginPath();g.ellipse(-46,-34,7,10,0.3,0,7);g.fill();g.beginPath();g.ellipse(222,-138,7,9,-0.3,0,7);g.fill()}},
 wolf:{body:[[10,-64],[4,-84],[24,-98],[70,-100],[110,-100],[132,-108],[146,-120],[160,-122],[178,-112],[192,-104],[190,-96],[172,-92],[156,-90],[140,-78],[122,-60],[80,-56],[40,-58]],
  legs:[[24,-60,62,15,0],[38,-58,60,13,Math.PI],[122,-62,64,15,Math.PI],[136,-64,66,13,0]],
  extra:(g,c)=>{g.fillStyle=c;g.fill(smoothPath([[8,-80],[-24,-64],[-42,-48],[-30,-56],[-8,-66]],true,0.3));g.fill(smoothPath([[148,-114],[150,-136],[160,-116]],true,0.1))}},
 bear:{body:[[6,-60],[0,-96],[25,-126],[80,-141],[130,-146],[160,-139],[185,-131],[203,-130],[222,-120],[241,-102],[239,-91],[222,-88],[205,-86],[190,-71],[170,-56],[110,-52],[50,-55]],
  legs:[[30,-62,62,30,0],[56,-60,60,26,Math.PI],[168,-62,62,30,Math.PI],[190,-66,66,26,0]],
  extra:(g,c)=>{g.fillStyle=c;g.beginPath();g.ellipse(198,-132,9,8,0,0,7);g.fill()}},
 deer:{body:[[8,-112],[2,-134],[18,-150],[60,-156],[110,-154],[140,-158],[154,-176],[166,-198],[180,-214],[198,-210],[216,-198],[216,-186],[196,-183],[182,-180],[172,-152],[164,-122],[150,-104],[110,-98],[60,-100],[30,-104]],
  legs:[[26,-104,108,17,0],[42,-102,106,15,Math.PI],[146,-104,110,17,Math.PI],[160,-106,112,15,0]],
  extra:(g,c)=>{g.strokeStyle=c;g.lineWidth=5;for(const p of [[[180,-210],[160,-250],[150,-290],[134,-320]],[[160,-250],[140,-262]],[[153,-282],[170,-300]],[[186,-210],[196,-250],[204,-290]],[[196,-250],[214,-262]]])g.stroke(smoothPath(p,false))}},
 aurochs:{body:[[6,-90],[0,-121],[18,-141],[70,-146],[130,-149],[170,-156],[196,-161],[214,-156],[232,-142],[247,-121],[249,-103],[237,-97],[222,-104],[208,-101],[192,-84],[150,-76],[90,-78],[40,-84]],
  legs:[[24,-90,90,24,0],[42,-88,88,21,Math.PI],[170,-86,86,25,Math.PI],[188,-88,88,22,0]],
  extra:(g,c)=>{g.strokeStyle=c;g.lineWidth=7;g.stroke(smoothPath([[216,-152],[236,-182],[262,-196]],false));g.stroke(smoothPath([[6,-118],[-8,-90],[-6,-56]],false))}},
};
// 人（狩人）。phase で歩く
function drawHunter(g,x,y,s,phase,c){g.save();g.translate(x,y);g.scale(s,s);g.fillStyle=c;g.strokeStyle=c;g.lineCap='round';
 const sw=Math.sin(phase)*0.35;
 g.lineWidth=13;for(const a of [sw,-sw]){g.beginPath();g.moveTo(0,-84);g.lineTo(Math.sin(a)*86,-84+Math.cos(a)*84);g.stroke()}
 g.fill(smoothPath([[-15,-152],[12,-154],[22,-118],[20,-84],[-20,-82],[-22,-118]],true,0.3));
 g.beginPath();g.arc(2,-166,14,0,7);g.fill();
 g.lineWidth=9;g.beginPath();g.moveTo(10,-140);g.lineTo(34,-112);g.stroke();
 g.lineWidth=3.5;g.beginPath();g.moveTo(-28,-36);g.lineTo(64,-228);g.stroke();
 g.fill(smoothPath([[60,-222],[72,-246],[69,-218]],true,0.1));
 g.restore()}

// mode 'sil': シルエット / 'cave': 木炭の輪郭＋淡い彩色
function drawAnimal(g,name,x,y,s,o={}){const A=ANIMALS[name];const c=o.color||'rgb(38,26,18)';const cave=o.mode==='cave';
 g.save();g.translate(x,y);g.scale(o.flip?-s:s,s);g.lineCap='round';g.lineJoin='round';
 const ph=o.walk??null;
 for(const [hx,hy,len,w,p] of A.legs){const a=ph===null?0:Math.sin(ph+p)*0.26;
  g.save();g.translate(hx,hy);g.rotate(-a);const lp=smoothPath([[-w/2,-14],[w/2,-14],[w*0.42,len*0.45],[w*0.24,len*0.86],[w*0.3,len],[-w*0.3,len],[-w*0.26,len*0.86],[-w*0.36,len*0.45]],true,0.25);
  if(cave){const lp2=new Path2D();lp2.moveTo(-w*0.34,0);lp2.quadraticCurveTo(-w*0.3,len*0.5,-w*0.2,len*0.92);lp2.quadraticCurveTo(0,len*0.98,w*0.18,len*0.92);lp2.quadraticCurveTo(w*0.26,len*0.5,w*0.3,0);
   const lg=g.createLinearGradient(0,0,0,len);lg.addColorStop(0,'rgba(22,14,10,0.45)');lg.addColorStop(1,'rgba(22,14,10,0.0)');g.fillStyle=lg;g.fill(lp2);g.globalAlpha=0.9;charcoal(g,lp2,(o.line||7)*0.55,(o.seed||1)+hx)}else{g.fillStyle=c;g.fill(lp)}g.restore();g.globalAlpha=1}
 const bob=ph===null?0:Math.abs(Math.sin(ph))*-3;g.translate(0,bob);
 const body=smoothPath(jitter(A.body,cave?3:0,o.seed||1));
 if(cave){g.fillStyle=o.fill||'rgba(150,72,30,0.35)';g.fill(body);g.save();g.clip(body);const xs=A.body.map(p=>p[0]);const x1=Math.max(...xs),x0=Math.min(...xs);const sg=g.createLinearGradient(x1,0,x1-(x1-x0)*0.55,0);sg.addColorStop(0,'rgba(22,14,10,0.75)');sg.addColorStop(1,'rgba(22,14,10,0)');g.fillStyle=sg;g.fillRect(x0-20,-400,x1-x0+40,420);g.restore();charcoal(g,body,o.line||7,o.seed||3)}
 else{g.fillStyle=c;g.fill(body)}
 A.extra&&A.extra(g,c,cave);
 g.restore()}
