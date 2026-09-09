// Pure navigation functions; independent from rendering and testable in Node.
export const contains=(r,x,z,margin=0)=>x>=r.min[0]+margin&&x<=r.max[0]-margin&&z>=r.min[1]+margin&&z<=r.max[1]-margin;
export function floorAt(nav,x,z,current){
 for(const st of nav.stairs){if(x>=st.xMin&&x<=st.xMax&&z>=st.zMin&&z<=st.zMax){let t;if(st.axis==='x'){t=st.upDirection===-1?(st.xMax-x)/(st.xMax-st.xMin):(x-st.xMin)/(st.xMax-st.xMin);}else{t=st.upDirection===-1?(st.zMax-z)/(st.zMax-st.zMin):(z-st.zMin)/(st.zMax-st.zMin);}const f=st.floorStart+t*(st.floorEnd-st.floorStart);if(Math.abs(f-current)<.4)return f;}}
 if(current>(nav.galleryLevel??5)){if((nav.galleryVoids||[]).some(r=>contains(r,x,z,-nav.radius)))return null;const supported=Array.from({length:8},(_,i)=>[x+nav.radius*Math.cos(i*Math.PI/4),z+nav.radius*Math.sin(i*Math.PI/4)]).every(([px,pz])=>nav.galleryZones.some(r=>contains(r,px,pz)));return supported?nav.galleryZones.find(r=>contains(r,x,z)).floor:null;}
 const valid=nav.walkZones.filter(r=>contains(r,x,z,0)).sort((a,b)=>b.floor-a.floor);
 for(const r of valid){if(Math.abs(r.floor-current)<=.29)return r.floor;}
 return null;
}
export function collides(nav,x,y,z){const r=nav.radius,feet=y-nav.eyeHeight;return nav.obstacles.some(o=>y+.10>o.min[1]&&feet<o.max[1]&&x>o.min[0]-r&&x<o.max[0]+r&&z>o.min[2]-r&&z<o.max[2]+r);}
export function moveWithCollision(nav,position,dx,dz){let[x,y,z]=position;const steps=Math.max(1,Math.ceil(Math.hypot(dx,dz)/.09));for(let i=0;i<steps;i++){for(const axis of [0,2]){const nx=x+(axis===0?dx/steps:0),nz=z+(axis===2?dz/steps:0);const f=floorAt(nav,nx,nz,y-nav.eyeHeight);if(f===null)continue;const ny=f+nav.eyeHeight;if(!collides(nav,nx,ny,nz)){x=nx;y=ny;z=nz;}}}return[x,y,z];}
export const smoothstep=t=>t*t*(3-2*t);
