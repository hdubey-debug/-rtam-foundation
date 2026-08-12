/** Stage ground: dissolve disc (y=−0.014) + contact disc (y=−0.007,
 * renderOrder 1) + non-counted reference rings. Concentric circles ONLY —
 * a 12-sector grid would put a system number on a repeating element
 * (design law 3), so the rings stay 3 plain circles.
 */
import * as THREE from "three/webgpu";
import { color, mix, positionLocal, smoothstep } from "three/tsl";

export interface Ground {
  group: THREE.Group;
  dispose(): void;
}

export function buildGround(scene: THREE.Scene): Ground {
  const group = new THREE.Group();
  group.name = "stage-ground";

  // dissolve disc — receives the key shadow, fades into the backdrop
  const dissolveR = 2.4;
  const dissolveGeo = new THREE.CircleGeometry(dissolveR, 96).rotateX(-Math.PI / 2);
  const dissolveMat = new THREE.MeshStandardNodeMaterial({
    roughness: 1,
    metalness: 0,
  });
  {
    const radial = positionLocal.xz.length().div(dissolveR);
    dissolveMat.colorNode = mix(color(0x1b1a18), color(0x141414), radial);
    dissolveMat.opacityNode = smoothstep(0.55, 1.0, radial).oneMinus();
    dissolveMat.transparent = true;
  }
  const dissolve = new THREE.Mesh(dissolveGeo, dissolveMat);
  dissolve.position.y = -0.014;
  dissolve.receiveShadow = true;

  // contact disc — tight dark pool giving the model weight
  const contactR = 1.35;
  const contactGeo = new THREE.CircleGeometry(contactR, 72).rotateX(-Math.PI / 2);
  const contactMat = new THREE.MeshStandardNodeMaterial({
    roughness: 1,
    metalness: 0,
  });
  {
    const radial = positionLocal.xz.length().div(contactR);
    contactMat.colorNode = color(0x0f0f0e);
    contactMat.opacityNode = smoothstep(0.35, 1.0, radial).oneMinus().mul(0.7);
    contactMat.transparent = true;
  }
  const contact = new THREE.Mesh(contactGeo, contactMat);
  contact.position.y = -0.007;
  contact.renderOrder = 1;
  contact.receiveShadow = true;

  // reference rings — thin, unlit, non-counted (3 concentric circles)
  const rings = new THREE.Group();
  rings.name = "reference-rings";
  const ringMat = new THREE.MeshBasicNodeMaterial({
    transparent: true,
    opacity: 0.16,
  });
  ringMat.colorNode = color(0x8f887c);
  for (const r of [0.9, 1.55, 2.2]) {
    const g = new THREE.RingGeometry(r - 0.0035, r + 0.0035, 128).rotateX(-Math.PI / 2);
    const m = new THREE.Mesh(g, ringMat);
    m.position.y = -0.005;
    rings.add(m);
  }

  group.add(dissolve, contact, rings);
  scene.add(group);

  return {
    group,
    dispose() {
      scene.remove(group);
      for (const g of [dissolveGeo, contactGeo]) g.dispose();
      rings.children.forEach((m) => (m as THREE.Mesh).geometry.dispose());
      dissolveMat.dispose();
      contactMat.dispose();
      ringMat.dispose();
    },
  };
}
