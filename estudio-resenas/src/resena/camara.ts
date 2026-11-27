import { Easing, interpolate } from "remotion";
import * as THREE from "three";

// Sala del canal: pantalla grande al frente, proyector arriba a la izquierda.
export const PANTALLA = { x: 0, y: 3.8, z: -12, w: 9.6, h: 5.4 };
export const FOV = 62;
export const PROYECTOR = new THREE.Vector3(-2.6, 7.5, -2.5);

// Distancia a la que la pantalla llena exactamente el alto del video:
// así el paso "sala → historia" no tiene salto.
const D_LLENO = PANTALLA.h / (2 * Math.tan(THREE.MathUtils.degToRad(FOV / 2)));

// p = 0: detrás del Espectador. p = 1: la pantalla llena todo el cuadro.
export const poseSala = (p: number) => {
  const sway = Math.sin(p * 9) * 0.02 * (1 - p);
  return {
    position: new THREE.Vector3(
      interpolate(p, [0, 1], [0.4, PANTALLA.x]) + sway,
      interpolate(p, [0, 0.45, 1], [3.6, 4.05, PANTALLA.y]),
      interpolate(p, [0, 1], [6.4, PANTALLA.z + D_LLENO]),
    ),
    target: new THREE.Vector3(
      PANTALLA.x,
      interpolate(p, [0, 1], [3.15, PANTALLA.y]),
      PANTALLA.z,
    ),
  };
};

export const camaraDesdeP = (p: number, aspect: number) => {
  const { position, target } = poseSala(p);
  const cam = new THREE.PerspectiveCamera(FOV, aspect, 0.1, 200);
  cam.position.copy(position);
  cam.lookAt(target);
  cam.updateMatrixWorld();
  return cam;
};

// Rectángulo (en píxeles del video) que ocupa la pantalla del cine.
export const rectPantalla = (p: number, width: number, height: number) => {
  const cam = camaraDesdeP(p, width / height);
  const pts = [
    [-1, 1],
    [1, -1],
  ].map(([sx, sy]) => {
    const v = new THREE.Vector3(
      PANTALLA.x + (sx * PANTALLA.w) / 2,
      PANTALLA.y + (sy * PANTALLA.h) / 2,
      PANTALLA.z,
    ).project(cam);
    return { x: ((v.x + 1) / 2) * width, y: ((1 - v.y) / 2) * height };
  });
  return {
    left: pts[0].x,
    top: pts[0].y,
    width: pts[1].x - pts[0].x,
    height: pts[1].y - pts[0].y,
  };
};

// Progreso de cámara de la sala según el segundo del video:
// entra a la pantalla al inicio y sale de ella en «Se trata de…».
export const progresoSala = (
  t: number,
  entrada: [number, number],
  salida: [number, number],
) => {
  const ease = Easing.bezier(0.6, 0, 0.3, 1);
  if (t < salida[0]) {
    return interpolate(t, entrada, [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: ease,
    });
  }
  return interpolate(t, salida, [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.5, 0, 0.2, 1),
  });
};
