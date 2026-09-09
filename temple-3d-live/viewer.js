import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {RGBELoader} from 'three/addons/loaders/RGBELoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {moveWithCollision,smoothstep} from './navigation.mjs';

const $=id=>document.getElementById(id),params=new URLSearchParams(location.search);
const reduce=matchMedia('(prefers-reduced-motion: reduce)'),mobile=matchMedia('(max-width: 620px)');
const response=await fetch('scene-manifest.json');if(!response.ok)throw new Error('Scene manifest unavailable');
const manifest=await response.json(),nav=manifest.navigation;
if(manifest.threeVersion!==THREE.REVISION.replace(/^170$/,'0.170.0'))throw new Error('Viewer version mismatch');
const canvas=$('scene'),renderer=new THREE.WebGLRenderer({canvas,antialias:!mobile.matches,alpha:false,powerPreference:'high-performance'});
renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.95;
renderer.shadowMap.enabled=!mobile.matches;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.shadowMap.autoUpdate=false;renderer.shadowMap.needsUpdate=true;
const scene=new THREE.Scene();scene.background=new THREE.Color('#a6b3b5');scene.fog=new THREE.Fog('#a6b3b5',65,145);
const camera=new THREE.PerspectiveCamera(46,1,.06,280);camera.position.fromArray(manifest.destinations[0].position);
const controls=new OrbitControls(camera,canvas);controls.target.fromArray(manifest.destinations[0].target);controls.enableDamping=!reduce.matches;controls.dampingFactor=.08;controls.autoRotate=false;controls.minDistance=23;controls.maxDistance=85;controls.maxPolarAngle=Math.PI*.49;controls.enablePan=false;
const hemi=new THREE.HemisphereLight('#dae3ed','#766549',.14);scene.add(hemi);
const sun=new THREE.DirectionalLight('#ffe1b1',1.7);sun.position.set(-18,28,15);sun.target.position.set(0,0,-2);sun.castShadow=!mobile.matches;sun.shadow.mapSize.set(1536,1536);Object.assign(sun.shadow.camera,{left:-27,right:27,top:31,bottom:-31,near:.5,far:90});sun.shadow.normalBias=.025;sun.shadow.bias=-.0001;scene.add(sun,sun.target);
const contextGround=new THREE.Mesh(new THREE.PlaneGeometry(300,300),new THREE.MeshStandardMaterial({color:'#68754a',roughness:1}));contextGround.rotation.x=-Math.PI/2;contextGround.position.y=-.06;contextGround.receiveShadow=true;scene.add(contextGround);
const sy=nav.shrineCenter[2],interiorLights=new THREE.Group();scene.add(interiorLights);interiorLights.visible=false;
for(const x of [-4.25,4.25])for(const z of [sy-2.25,sy+2.25]){const l=new THREE.SpotLight('#ffe6bb',120,18,Math.PI*.27,.6,2);l.position.set(x,nav.shrineCenter[1]+7.76,z);l.target.position.set(0,nav.shrineCenter[1]+1.7,sy);interiorLights.add(l,l.target);}
for(const x of [-6.12,6.12])for(const z of [9,4,-4,-9]){const l=new THREE.PointLight('#ffbe77',8,6,2);l.position.set(x,nav.shrineCenter[1]+.6,z);interiorLights.add(l);}
const draco=new DRACOLoader();draco.setDecoderPath('vendor/examples/jsm/libs/draco/gltf/');draco.setWorkerLimit(mobile.matches?1:2);
const loader=new GLTFLoader();loader.setDRACOLoader(draco);const loaded=new Map(),pending=new Map();let active='overview',walking=false,transition=null,visit=0,tourTimer=0,tourIndex=0,frameLast=performance.now(),lookYaw=0,lookPitch=0,pointer=null,benchmarking=false;
const keys=new Set(),vec=new THREE.Vector3();let frameMs=[],lastMetrics=0,dpr=Math.min(devicePixelRatio,mobile.matches?1:1.5);
function resize(){if(benchmarking)return;renderer.setPixelRatio(dpr);renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();}addEventListener('resize',resize);resize();
function status(message){$('status').textContent=message;}
function bakedMaterial(material,baked,asset){const m=material.clone();if(!/Foliage|water/i.test(m.name))m.side=THREE.FrontSide;m.envMapIntensity=asset==='interior'?.025:.20;
 if(baked){m.vertexColors=true;m.onBeforeCompile=shader=>{shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>','// Color stores irradiance; preserve the material albedo.').replace('#include <lights_fragment_maps>','#include <lights_fragment_maps>\n#if defined(USE_COLOR) || defined(USE_COLOR_ALPHA)\n irradiance += PI * vColor.rgb;\n#endif');};m.customProgramCacheKey=()=>`temple-irradiance-${asset}`;}
 return m;}
async function loadAsset(id){if(loaded.has(id))return loaded.get(id);if(pending.has(id))return pending.get(id);const asset=manifest.assets.find(a=>a.id===id);if(!asset)return;
 const promise=(async()=>{if(params.get('failAsset')===id)throw new Error('Asset failure test');const gltf=await loader.loadAsync(asset.url);gltf.scene.traverse(o=>{if(!o.isMesh)return;const baked=!!o.geometry.getAttribute('color');o.material=Array.isArray(o.material)?o.material.map(m=>bakedMaterial(m,baked,id)):bakedMaterial(o.material,baked,id);o.castShadow=id!=='landscape';o.receiveShadow=true;});scene.add(gltf.scene);renderer.shadowMap.needsUpdate=true;loaded.set(id,gltf.scene);if(id==='interior')interiorLights.visible=true;return gltf.scene;})();pending.set(id,promise);try{return await promise;}catch(e){pending.delete(id);throw e;}}
function caption(dest){active=dest.id;const index=manifest.destinations.indexOf(dest);$('chapter-number').textContent=String(index+1).padStart(2,'0');$('place-title').textContent=dest.id==='overview'?'A place for stillness.':dest.label;$('place-description').textContent=dest.description;for(const a of document.querySelectorAll('[data-dest]')){if(a.dataset.dest===dest.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');}history.replaceState(null,'','#'+dest.id);}
function stopTour(){clearTimeout(tourTimer);tourTimer=0;$('tour').children[1].textContent='Take a guided visit';$('tour').setAttribute('aria-pressed','false');}
function setWalking(value){const wasWalking=walking;walking=value;keys.clear();controls.enabled=!value;transition=null;$('walk-help').hidden=!value;$('walk-mode').setAttribute('aria-pressed',String(value));$('orbit-mode').setAttribute('aria-pressed',String(!value));$('hint').textContent=value?'WASD to move · Drag to look · Esc to finish':'Drag to look · Scroll to move closer';if(value){camera.getWorldDirection(vec);lookYaw=Math.atan2(-vec.x,-vec.z);lookPitch=Math.asin(vec.y);}else if(wasWalking){controls.target.copy(camera.position).add(camera.getWorldDirection(vec).multiplyScalar(7));controls.update();}}
function showStill(dest,message){document.body.classList.add('fallback');$('poster').src=dest.fallback;$('poster').alt=dest.label;caption(dest);status(message);}
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function go(id,{instant=false,fromTour=false}={}){if(document.body.dataset.renderOnly==='true')return;const dest=manifest.destinations.find(d=>d.id===id);if(!dest)return;const token=++visit;const previous=active;if(!fromTour)stopTour();setWalking(false);status(dest.requires==='interior'&&!loaded.has('interior')?'Opening the interior…':'Moving to '+dest.label.toLowerCase());
 try{await loadAsset(dest.requires);}catch(e){if(token===visit)showStill(dest,'This model is unavailable. Its rendered view is shown.');return;}if(token!==visit)return;
 const restoring=document.body.classList.contains('fallback');document.body.classList.remove('fallback');caption(dest);$('poster').src=dest.fallback;
 const pos=new THREE.Vector3().fromArray(dest.position),target=new THREE.Vector3().fromArray(dest.target);controls.enabled=false;
 controls.minDistance=id==='overview'?23:id==='nandi'?7:2;controls.maxDistance=id==='overview'?85:18;controls.maxPolarAngle=Math.PI*.86;
 const floorChange=id==='gallery'||previous==='gallery';
 if(instant||reduce.matches||restoring){camera.position.copy(pos);controls.target.copy(target);controls.enabled=true;controls.update();status('Ready to explore');return;}
 if(floorChange){document.body.classList.add('veiled');await delay(250);if(token!==visit)return;camera.position.copy(pos);controls.target.copy(target);controls.update();document.body.classList.remove('veiled');controls.enabled=true;status('Ready to explore');return;}
 let route=[];
 if(id==='shrine'||id==='entrance'){
  if(previous==='shrine'&&id==='entrance')route=[nav.entrancePortal.map((v,i)=>i===2?v-1:v),dest.position];
  else if(previous==='entrance')route=[dest.position];
  else route=[[12,7,18],[9,3.5,16.8],[0,nav.entrancePortal[1],16.8],nav.entrancePortal,dest.position];
 }else if(previous==='shrine'||previous==='entrance')route=[nav.entrancePortal,[0,nav.entrancePortal[1],16.8],[12,6,18],dest.position];
 else route=[dest.position];
 const points=[camera.position.clone(),...route.map(p=>new THREE.Vector3().fromArray(p))];const lengths=[0];for(let i=1;i<points.length;i++)lengths.push(lengths.at(-1)+points[i].distanceTo(points[i-1]));
 transition={points,lengths,total:lengths.at(-1),start:performance.now(),duration:Math.min(6500,1200+lengths.at(-1)*95),target0:controls.target.clone(),target1:target,token};
}
for(const a of document.querySelectorAll('[data-dest]'))a.addEventListener('click',e=>{e.preventDefault();go(a.dataset.dest);});
$('orbit-mode').addEventListener('click',()=>go(active));
$('walk-mode').addEventListener('click',async()=>{stopTour();try{await loadAsset('interior');}catch(e){showStill(manifest.destinations.find(d=>d.id==='shrine'),'The interior could not load. Its rendered view is shown.');return;}document.body.classList.remove('fallback');if(active==='gallery'){camera.position.fromArray(nav.galleryWalkingStart);controls.target.set(0,nav.shrineCenter[1]+2.1,sy);}else{camera.position.set(0,nav.shrineCenter[1]+nav.eyeHeight,nav.entrancePortal[2]+.9);controls.target.set(0,nav.entrancePortal[1],sy);}camera.lookAt(controls.target);setWalking(true);canvas.focus();status('Walking · collision protection on');});
$('tour').addEventListener('click',()=>{if(tourTimer){stopTour();return;}tourIndex=0;$('tour').children[1].textContent='Stop guided visit';$('tour').setAttribute('aria-pressed','true');const next=async()=>{await go(manifest.destinations[tourIndex].id,{fromTour:true});tourIndex++;if(tourIndex<manifest.destinations.length)tourTimer=setTimeout(next,10000);else tourTimer=setTimeout(stopTour,10000);};next();});
controls.addEventListener('start',()=>{transition=null;stopTour();});
const movementKeys=['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'];
addEventListener('keydown',e=>{if(document.querySelector('dialog[open]'))return;if(e.code==='Escape'){setWalking(false);stopTour();return;}if(walking&&movementKeys.includes(e.code)){e.preventDefault();keys.add(e.code);stopTour();}});
addEventListener('keyup',e=>keys.delete(e.code));addEventListener('blur',()=>keys.clear());document.addEventListener('visibilitychange',()=>{keys.clear();frameLast=performance.now();if(document.hidden)stopTour();});
canvas.addEventListener('pointerdown',e=>{if(walking){pointer={x:e.clientX,y:e.clientY,id:e.pointerId};canvas.setPointerCapture(e.pointerId);}});
canvas.addEventListener('pointermove',e=>{if(walking&&pointer){lookYaw-=(e.clientX-pointer.x)*.003;lookPitch=Math.max(-1.15,Math.min(1.15,lookPitch-(e.clientY-pointer.y)*.003));pointer.x=e.clientX;pointer.y=e.clientY;}});
canvas.addEventListener('pointerup',()=>pointer=null);canvas.addEventListener('pointercancel',()=>pointer=null);
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();stopTour();window.dispatchEvent(new CustomEvent('temple-fallback',{detail:'The 3D context was interrupted. Rendered views remain available.'}));});
reduce.addEventListener('change',()=>{controls.enableDamping=!reduce.matches;transition=null;if(reduce.matches)go(active,{instant:true});});
let bench=null;
$('qa').hidden=!params.has('qa');
$('benchmark').addEventListener('click',async()=>{stopTour();setWalking(false);try{await Promise.all(manifest.assets.map(a=>loadAsset(a.id)));}catch(e){$('benchmark-report').textContent='Benchmark unavailable: a model asset failed to load.';return;}benchmarking=true;controls.enabled=false;renderer.setPixelRatio(1);renderer.setSize(1920,1080,false);camera.aspect=1920/1080;camera.updateProjectionMatrix();bench={start:performance.now(),frames:[],places:[],segments:manifest.destinations.map(d=>({id:d.id,frames:[]})),index:-1};$('benchmark-report').textContent='Benchmarking camera movement at all five destinations, 1920 × 1080…';});
function frame(now){const raw=Math.max(.01,now-frameLast),dt=Math.min(raw/1000,.06);frameLast=now;if(document.hidden){requestAnimationFrame(frame);return;}
 if(transition){const tr=transition,t=Math.min(1,(now-tr.start)/tr.duration),distance=smoothstep(t)*tr.total;let i=1;while(i<tr.lengths.length-1&&tr.lengths[i]<distance)i++;const frac=(distance-tr.lengths[i-1])/Math.max(.001,tr.lengths[i]-tr.lengths[i-1]);camera.position.copy(tr.points[i-1]).lerp(tr.points[i],frac);controls.target.copy(tr.target0).lerp(tr.target1,smoothstep(t));camera.lookAt(controls.target);if(t===1){transition=null;controls.enabled=true;status('Ready to explore');}}
 if(walking){let f=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown')),side=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));const norm=Math.hypot(f,side)||1;f/=norm;side/=norm;const dx=(-Math.sin(lookYaw)*f+Math.cos(lookYaw)*side)*nav.speed*dt,dz=(-Math.cos(lookYaw)*f-Math.sin(lookYaw)*side)*nav.speed*dt;camera.position.fromArray(moveWithCollision(nav,camera.position.toArray(),dx,dz));camera.rotation.order='YXZ';camera.rotation.set(lookPitch,lookYaw,0);}
 else if(!transition&&!bench)controls.update();
 if(bench){const elapsed=Math.max(0,now-bench.start),index=Math.min(4,Math.floor(elapsed/6000)),dest=manifest.destinations[index],t=Math.min(1,(elapsed%6000)/6000);
  if(index!==bench.index){caption(dest);bench.index=index;bench.places.push(dest.id);}
  // A short dolly at each representative location measures actual camera motion.
  camera.position.fromArray(dest.position);controls.target.fromArray(dest.target);camera.position.lerp(controls.target,.08*smoothstep(t));camera.lookAt(controls.target);
  if(elapsed%6000>1500&&raw<500){bench.frames.push(raw);bench.segments[index].frames.push(raw);}
  if(elapsed>=30000){const stats=values=>{const sorted=[...values].sort((a,b)=>a-b);return {averageFps:+(1000/(values.reduce((a,b)=>a+b,0)/values.length)).toFixed(1),p95FrameMs:+sorted[Math.floor(sorted.length*.95)].toFixed(2),samples:values.length};},overall=stats(bench.frames),segments=bench.segments.map(v=>({id:v.id,...stats(v.frames)})),report={width:1920,height:1080,dpr:1,motion:'Five continuous dolly segments with cuts between destinations; first 1.5 seconds of each segment excluded for warmup.',...overall,segments,passes30Fps:segments.every(v=>v.averageFps>=30),mobileHardwareVerified:false};$('benchmark-report').textContent=JSON.stringify(report,null,2);bench=null;benchmarking=false;controls.enabled=true;controls.minDistance=2;controls.maxDistance=18;resize();}}

 renderer.render(scene,camera);if(raw>0)frameMs.push(raw);if(frameMs.length>120)frameMs.shift();if(now-lastMetrics>1000){lastMetrics=now;const fps=1000/(frameMs.reduce((a,b)=>a+b,0)/frameMs.length);$('metrics').textContent=`${fps.toFixed(1)} fps · ${renderer.info.render.triangles.toLocaleString()} triangles · ${renderer.info.render.calls} draws · ${renderer.domElement.width}×${renderer.domElement.height} · eye ${camera.position.toArray().map(v=>v.toFixed(2)).join(', ')}`;}
 requestAnimationFrame(frame);}
requestAnimationFrame(frame);
try{await loadAsset('exterior');document.body.classList.add('ready');status('Exterior ready');loadAsset('landscape').then(()=>{if(!document.body.classList.contains('fallback'))status('Ready to explore');}).catch(()=>{if(!document.body.classList.contains('fallback'))status('Temple ready · some landscape details are unavailable');});new RGBELoader().load('assets/daylight-2k.hdr',tex=>{tex.mapping=THREE.EquirectangularReflectionMapping;scene.environment=tex;scene.background=tex;scene.backgroundIntensity=.45;},undefined,()=>{});const initial=location.hash.slice(1);if(initial&&manifest.destinations.some(d=>d.id===initial))await go(initial,{instant:true});}
catch(error){console.error(error);window.dispatchEvent(new CustomEvent('temple-fallback',{detail:'The model could not load. Rendered views are available.'}));}
