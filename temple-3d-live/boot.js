const $=id=>document.getElementById(id);
for(const [button,dialog] of [['stills-open','stills-dialog'],['about-open','about-dialog']])$(button).addEventListener('click',()=>$(dialog).showModal());
for(const b of document.querySelectorAll('.dialog-close'))b.addEventListener('click',()=>b.closest('dialog').close());
$('fullscreen').addEventListener('click',()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen().catch(()=>{}));
function fallback(message){document.body.dataset.renderOnly='true';document.body.classList.add('fallback');$('status').textContent=message;$('hint').textContent='Choose a destination to see its rendered view.';$('walk-mode').disabled=true;$('orbit-mode').disabled=true;$('tour').disabled=true;
 for(const link of document.querySelectorAll('[data-dest]'))link.onclick=e=>{e.preventDefault();$('poster').src=link.href;$('poster').alt=link.innerText;for(const a of document.querySelectorAll('[data-dest]'))a.removeAttribute('aria-current');link.setAttribute('aria-current','location');$('place-title').textContent=link.children[1].childNodes[0].textContent;$('place-description').textContent='A rendered view from the measured Blender scene.';};}
window.addEventListener('temple-fallback',e=>fallback(e.detail||'Rendered views are available.'));
if(new URLSearchParams(location.search).has('forceFallback'))fallback('Showing rendered views. 3D is unavailable.');
else import('./viewer.js?v=20260906-entry').catch(error=>{console.error(error);fallback('The 3D scene could not start. Rendered views are available.');});
