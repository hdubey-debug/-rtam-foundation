// The light you move: a test, on the pilot pages with ?light. One light, held anywhere round the building: drag its handle
// and its light falls on the stone from there, with true shadows, while the jali's lamps keep burning within. The page
// stays black; nothing else is added (no sky, no ground, no sun). Off, the walk is the posters' night, as before.
import * as THREE from 'three';
import { MODES } from './stage.js';

const KNOB_R = { temple: .62, nandi: .2, complex: 1.05 };     // how far from the middle the handle floats (world units)
const REACH = { temple: .75, nandi: .3, complex: 1.25 };      // what the shadows must cover

export async function addLight(stage, { base = '', host } = {}) {
  const S = stage, R = S.renderer, scene = S.scene;
  R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap; R.shadowMap.autoUpdate = false;   // drawn only when the light moves
  const loader = new THREE.TextureLoader();
  const tex = (u, data) => new Promise((res, rej) => loader.load(base + u, (t) => {
    t.colorSpace = data ? THREE.NoColorSpace : THREE.SRGBColorSpace; t.flipY = false; t.anisotropy = Math.min(8, R.capabilities.getMaxAnisotropy()); res(t);
  }, undefined, rej));
  // the stone without its source light (build/night_texture.py --albedo), the lamps alone (--lamps), and the full models'
  // own normals (build/normal_map.py: the web models carry none, and these keep the carving the reduced meshes lost)
  const [ta, na, tl, tn, nn] = await Promise.all([tex('media/temple-albedo-2048.jpg'), tex('media/nandi-albedo-2048.jpg'), tex('media/temple-lamps-2048.jpg'),
    tex('media/temple-normal-2048.webp', true), tex('media/nandi-normal-2048.webp', true)]);
  const none = new THREE.DataTexture(new Uint8Array([0, 0, 0, 255]), 1, 1); none.needsUpdate = true;
  const albedo = { temple: ta, nandi: na }, lamps = { temple: tl, nandi: none }, normals = { temple: tn, nandi: nn };

  const mix = { value: 0 };                                   // 0: the posters' night, as baked; 1: the stone in your light
  const light = new THREE.DirectionalLight(0xfff0dc, 4.4), ambient = new THREE.AmbientLight(0xd8dce6, .2);   // one strong light, little fill
  light.castShadow = true;
  const sz = S.tier === 'hi' ? 2048 : 1024; light.shadow.mapSize.set(sz, sz);
  light.shadow.bias = -.0004; light.shadow.normalBias = .0015;
  scene.add(light, light.target, ambient);
  const uL = { value: new THREE.Vector3() }, uLc = { value: new THREE.Vector3() }, uAmb = { value: 0 };
  const sync = () => {                                        // the reflection's own copy of the light (it is lit by hand)
    uLc.value.set(light.color.r, light.color.g, light.color.b).multiplyScalar(light.intensity / Math.PI);
    uAmb.value = ambient.intensity / Math.PI;
  };

  // the stone: lit by the light, the lamps added; the baked night where the mix is 0
  S.lit = (src, name) => {
    if (!src.geometry.attributes.normal) src.geometry.computeVertexNormals();   // (only for the shadows' offset; the map shades)
    const m = new THREE.MeshLambertMaterial({ map: albedo[name], normalMap: normals[name], normalMapType: THREE.ObjectSpaceNormalMap });
    m.onBeforeCompile = (sh) => {
      sh.uniforms.uMix = mix; sh.uniforms.nightMap = { value: src.map }; sh.uniforms.lampMap = { value: lamps[name] };
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', '#include <common>\nuniform float uMix; uniform sampler2D nightMap; uniform sampler2D lampMap;')
        .replace('#include <opaque_fragment>', '#include <opaque_fragment>\nvec3 lit = gl_FragColor.rgb + texture2D(lampMap, vMapUv).rgb;\ngl_FragColor.rgb = mix(texture2D(nightMap, vMapUv).rgb, lit, uMix);');
    };
    m.customProgramCacheKey = () => 'light';
    return m;
  };
  // the reflection: the same, lit by hand (a mirror shows the stone as it is lit), fading into the black floor
  S.litMirror = (src, name) => {
    const m = new THREE.MeshBasicMaterial({ map: src.map });
    m.onBeforeCompile = (sh) => {
      const rot = new THREE.Matrix3().setFromMatrix4(S.groups[name].matrixWorld);   // the stone's turn (Nandi faces the temple)
      Object.assign(sh.uniforms, { uGround: { value: new THREE.Vector3(20 / 255, 20 / 255, 20 / 255) }, uK: { value: .28 }, uLen: { value: .16 },
        uMix: mix, albedoMap: { value: albedo[name] }, lampMap: { value: lamps[name] }, nrmMap: { value: normals[name] }, uRot: { value: rot }, uL, uLc, uAmb });
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying float vWY;')
        .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWY = (modelMatrix * vec4(transformed, 1.0)).y;');
      sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
        varying float vWY; uniform vec3 uGround; uniform float uK; uniform float uLen; uniform float uMix; uniform mat3 uRot;
        uniform sampler2D albedoMap; uniform sampler2D lampMap; uniform sampler2D nrmMap; uniform vec3 uL; uniform vec3 uLc; uniform float uAmb;`)
        .replace('#include <dithering_fragment>', `#include <dithering_fragment>
        vec3 n = normalize(uRot * (texture2D(nrmMap, vMapUv).xyz * 2.0 - 1.0));
        vec3 lit = texture2D(albedoMap, vMapUv).rgb * (uAmb + uLc * max(dot(n, uL), 0.0)) + texture2D(lampMap, vMapUv).rgb;
        gl_FragColor.rgb = mix(gl_FragColor.rgb, linearToOutputTexel(vec4(lit, 1.0)).rgb, uMix);
        float k = uK * pow(clamp(1.0 + vWY / uLen, 0.0, 1.0), 1.3);
        gl_FragColor.rgb = mix(uGround, gl_FragColor.rgb, k);`);
    };
    m.customProgramCacheKey = () => 'light-mirror';
    return m;
  };
  for (const name of ['temple', 'nandi']) for (const o of S.groups[name].children) {
    if (o.isMesh && o.userData.model) { o.material = S.lit(o.userData.model, name); o.castShadow = o.receiveShadow = true; }
  }
  for (const o of S.groups.mirror.children) if (o.isMesh) { const of = o.userData.of, src = S.groups[of].children.find((c) => c.userData.model); if (src) o.material = S.litMirror(src.userData.model, of); }

  // where the light is: a direction from the middle of what is walked round (world), kept as one walks
  const dir = new THREE.Vector3();
  const setDir = (az, el) => { const a = az * Math.PI / 180, e = el * Math.PI / 180; dir.set(Math.cos(e) * Math.cos(a), Math.sin(e), Math.cos(e) * Math.sin(a)); };
  setDir(MODES.temple.home + 45, 38);                         // to start: high, and to the front's left (a painter's light)
  const centre = () => { const M = MODES[S.mode]; return new THREE.Vector3(M.c[0], M.ly, M.c[1]); };
  function place() {
    const c = centre(), r = REACH[S.mode], cam = light.shadow.camera;
    cam.left = cam.bottom = -r; cam.right = cam.top = r; cam.near = .05; cam.far = 6; cam.updateProjectionMatrix();
    light.target.position.copy(c); light.position.copy(c).addScaledVector(dir, 3);
    uL.value.copy(dir); sync();
    const glowBase = place.glow || (place.glow = (S.glows || []).map((g) => g.opacity));
    (S.glows || []).forEach((g, i) => { g.opacity = glowBase[i] * (1 - .35 * mix.value); });
    S.shadowsDirty = true; S.dirty = true; S.wake(); knob();
  }

  // the handle: a plain point in a ring, where the light is held; drag it anywhere round the building
  const el = document.createElement('div'); el.id = 'lightknob'; el.setAttribute('role', 'slider'); el.setAttribute('aria-label', 'प्रकाश · move the light');
  (host || document.body).appendChild(el);
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), tmp = new THREE.Vector3();
  function knob() {
    if (!S.size) return;
    S.apply(); S.camera.updateMatrixWorld();
    const p = centre().addScaledVector(dir, KNOB_R[S.mode]).project(S.camera);
    const x = (p.x + 1) / 2 * S.size.w, y = (1 - p.y) / 2 * S.size.h, b = S.band || { top: 0, bottom: S.size.h };
    el.style.transform = `translate(${Math.max(14, Math.min(S.size.w - 14, x)).toFixed(1)}px, ${Math.max(b.top + 14, Math.min(b.bottom - 14, y)).toFixed(1)}px)`;
  }
  // the light goes where the finger points, on a sphere round the middle (its near side; beside it, its rim); never below
  // the ground
  function toward(px, py) {
    ndc.set(px / S.size.w * 2 - 1, -(py / S.size.h) * 2 + 1); ray.setFromCamera(ndc, S.camera);
    const c = centre(), r = KNOB_R[S.mode], o = ray.ray.origin, d = ray.ray.direction;
    const oc = tmp.subVectors(o, c), bq = oc.dot(d), cq = oc.lengthSq() - r * r, disc = bq * bq - cq;
    const t = disc >= 0 ? -bq - Math.sqrt(disc) : -bq;                     // the near hit, or the closest approach
    const hit = o.clone().addScaledVector(d, t).sub(c).normalize();
    hit.y = Math.max(hit.y, .06); dir.copy(hit.normalize()); place();
  }
  let drag = false;
  el.addEventListener('pointerdown', (e) => { e.stopPropagation(); e.preventDefault(); el.setPointerCapture(e.pointerId); drag = true; el.classList.add('held'); S.stopSpin(); S.vel = 0; });
  el.addEventListener('pointermove', (e) => { if (drag) toward(e.clientX, e.clientY); });
  const up = () => { drag = false; el.classList.remove('held'); };
  el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
  const prev = S.onframe; S.onframe = (az) => { prev && prev(az); knob(); };
  S.onmode = () => { place(); };
  place();

  let anim = 0;
  return {
    get on() { return mix.value > .5; },
    // into your light (1) or back to the night (0), over 0.9 s
    set(on) {
      const from = mix.value, to = on ? 1 : 0, t0 = performance.now(), id = ++anim;
      el.classList.toggle('on', on);
      const tick = (now) => {
        if (id !== anim) return; const k = Math.min(1, (now - t0) / 900), e = k * k * (3 - 2 * k);
        mix.value = from + (to - from) * e; place(); if (k < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    },
  };
}
